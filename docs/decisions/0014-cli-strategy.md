---
title: "Decision 0014: How the `allium` command gets into the wheel"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_cli_strategy"]
requires: []
---

# Decision 0014: How the `allium` command gets into the wheel

## Context

The wheel's `allium` command must behave exactly as upstream's `allium-cli` at the
pinned version (invariant 1). Upstream ships that behaviour only as a binary crate:
file discovery, the cross-module context, the JSON output, the exit-code policy, `plan`
and `model` live in `crates/allium/src/` with no library target, so bindings over
`allium-parser` alone cannot reproduce `allium check`. Three routes were open: vendor
upstream's CLI modules into the core, bundle upstream's binary as package data behind an
exec shim, or ask upstream to expose a `run` function. S01 built the first two and
measured both with a parity harness against `allium-cli` built from crates.io.

## Decision

Vendor. Upstream's `crates/allium/src/main.rs`, `test_plan.rs` and `domain_model.rs` at
the pinned tag live in `crates/alliumpy-core/src/cli/`, each with a provenance header
and a block of file-level `#[expect]` attributes, transformed mechanically so that
`main` becomes `alliumpy_core::cli::run(args, stdout, stderr) -> i32`: output goes to
the handles, a failed write still panics as upstream's does, and `run` returns 101 for a
panic as upstream's binary exits; `run_os` takes the arguments as the operating system
passed them and returns 101 for one that is not UTF-8, as upstream's `std::env::args`
panics. `--version` prints `ALLIUM_VERSION_STRING`. The bindings expose `_run_cli`,
which writes to the process's own streams; `_cli.py` restores SIGINT's default action
and points a closed standard descriptor at the null device, as Rust's runtime does for
upstream's binary, then passes `sys.argv[1:]` and exits with the status. `serde` and `serde_json` join the core's
dependencies under [decision 0004](0004-dependency-policy.md).

The vendored files keep upstream's formatting (`#[rustfmt::skip]` on their `mod`
declarations), are excluded from rustqual by `exclude_files` in `rustqual.toml`, and
are exempt from EditorConfig's indent-size rule by an `.editorconfig` section, which
also keeps upstream's help text byte for byte: their shape is upstream's, and parity, not the metrics gate, is what holds them. They
stay under the coverage floor and the lint tables; `cli.rs` carries the tests that keep
the floor. The sdist is kept and carries the vendored sources.

## Consequences

The wheel stays one extension module built once per target, and `just parity` proves the
command against the reference over upstream's fixture corpus. Every upstream bump re-runs
the vendoring transform, reviews upstream's diff to the three files and re-runs parity
(T17's runbook); a transform that no longer matches stops rather than producing a partial
copy. The vendored code can drift from upstream only between bumps, and the corpus is the
alarm, so it is only as good as the corpus (`tests/fixtures/parity/README.md` says what it
covers). The coverage margin is thin, and a bump that adds untested upstream lines can
breach the floor. Python can call the CLI's logic through the core later without a second
build.

## What would reopen this

Upstream releasing a library target that exposes `run` on crates.io (then a dependency
replaces the vendored copy); a vendored transform that can no longer be applied
mechanically; or a parity difference that the vendored build cannot reproduce.

## Related pages

- [Dependency policy](0004-dependency-policy.md)
- [The metrics gate](0007-metrics-gate.md)
- [Version tracks upstream](0010-version-tracks-upstream.md)
- [An exact pin on `allium-parser`](0011-exact-pin-on-allium-parser.md)
- [Architecture](../explanation/architecture.md)
