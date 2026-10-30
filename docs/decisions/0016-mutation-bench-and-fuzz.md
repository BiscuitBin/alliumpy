---
title: "Decision 0016: Mutation testing, benchmarks and fuzzing"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_mutation_bench_fuzz"]
requires: []
---

# Decision 0016: Mutation testing, benchmarks and fuzzing

## Context

`alliumpy-core` is a thin conversion layer over upstream's parser, and its only consumer
is the wheel. Its tests reach the coverage floor, but coverage records that a line ran,
not that a test would notice it changing; nothing timed the conversion; and nothing fed
it input a person did not think of. libpawdoku's S03 spike at `ccdd001` measured
cargo-mutants, divan and cargo-fuzz and drafted their adoption, and pachinko carried
those drafts at `bf51e0d`. T15 adapts them to this core. Upstream decides behaviour
(invariant 1), so none of the three may change what `parse` returns; each can only
report.

## Decision

Three reports, none a gate. Their scope is the core, through `alliumpy_core::parse`,
and never upstream's parser beyond that call. The pyo3 crate is excluded from all three:
its tests are Python's, and a Rust test, bench or fuzz binary linking it would need
libpython at load time.

### Mutation testing

cargo-mutants 27.1.0 is pinned in `pyproject.toml`; on 2026-10-30 conda-forge's linux-64
and osx-arm64 builds depended on no rust, so rustup's cargo stays first on `PATH`.
`just mutants` mutates a copy of the tree, `--package alliumpy-core` alone, with every
feature, under `cargo test` so a doctest can catch a mutant. Its first line fails when
the mutant list is empty, so a wrong filter cannot pass over zero mutants. It watches
whether the core's assertions notice a change on a covered line. It is a report because
a survivor asks for a judgement and the run grows with the crate. `mutants.yml` runs it
weekly and by hand and keeps `mutants.out/` for 28 days. The first run tested 7 mutants:
5 caught, 2 unviable, none missed. An exclusion goes in `.cargo/mutants.toml` with a
comment, never through the `mutants` crate, and only for an equivalent mutant.

### Benchmarks

divan 0.1.21 is a development dependency of the core, behind one bench, `parse`, over
the two smoke fixtures through `divan::black_box`. On 2026-10-30 its repository was not
archived and was last pushed on 2026-07-19, so criterion, the spike's fallback, was not
needed. It watches the conversion's cost by hand. It is a report because timings measure
the machine and its load; no benchmark runs in CI.

### Fuzzing

cargo-fuzz 0.13.2, from `tools.txt` because conda-forge lacks it, drives libfuzzer-sys
0.4.13 in `fuzz/`, a crate outside the workspace with its own committed
`fuzz/Cargo.lock`. Its manifest repeats the root's `forbid` levels and Clippy table,
because an excluded crate cannot inherit `[workspace.lints]`, and `lock-check`,
`fmt-check` and `clippy` reach it by `--manifest-path`. The `parse` target passes valid
UTF-8 through `alliumpy_core::parse` and asserts every location is one-based, so it
watches for a panic in the parser or the conversion and for a zero coordinate.
`just fuzz` runs on the pinned stable with `--sanitizer none`: on 2026-10-30 this built
and ran on Rust 1.99.1 with no nightly installed, which answers pachinko's claim that
stable fuzzing works without a sanitizer. AddressSanitizer would need nightly, and every
crate forbids unsafe code. It is a report because fuzzing is nondeterministic.
`fuzz.yml` fuzzes each target for 300 seconds weekly and by hand and uploads a crash;
`just fuzz-build`, the one line the `rust` CI job runs, proves only that the target
compiles.

The first local run of `just fuzz parse 60` crashed after about 6,600 executions inside
upstream: `allium-parser` 3.6.1 slices its source at a byte offset inside a multi-byte
character (`src/parser.rs:109`, "end byte index 4 is not a char boundary"). The smallest
input found is `z/х`, whose last character is Cyrillic; through the Python API,
`alliumpy.parse("z/х")` raises pyo3's `PanicException`. This repository does not fix or
mask it, since upstream decides behaviour: the target stays as specified, so `fuzz.yml`
is expected to fail until the pin moves to an upstream release that fixes it.

## Consequences

The consequences that hurt. Every `just check` and the `rust` job now compile
libFuzzer's C++ through libfuzzer-sys's build script, so a C++ compiler is a
prerequisite of the gate; the fuzz crate's clippy line took 4.5 seconds cold and 0.08
warm, and `just fuzz-build` 21.4 seconds cold and 0.3 warm, on an Apple-silicon
workstation. The cargo-fuzz release has no arm64 macOS binary, so Apple silicon needs
Rosetta 2 for `just fuzz` and `just fuzz-build`. A third lockfile moves with the other
two, and because the fuzz crate's path dependency names no version, a version bump leaves
`fuzz/Cargo.lock` stale until `just lock`; `lock-check` refuses it meanwhile. divan adds
16 packages to `Cargo.lock`, a second `syn` major among them, outside the shipped graph
and cargo-deny's. Two weekly workflows spend Actions minutes on a private repository
(`tickets/CONVENTIONS.md` section 13). cargo-mutants never mutates a function named `new`
or every expression, so its silence is not proof. A red `fuzz.yml` is a known upstream
crash until upstream fixes it, which makes a second, new crash easier to miss; read the
crash's location, not just the colour.

## What would reopen this

A mutation score worth gating on, with evidence beyond line coverage. A crash the weekly
job finds in upstream's parser, which is reported upstream, not fixed here; the one
recorded above is the first. A crash in the conversion itself, which is fixed here with a
regression test in the core. conda-forge's cargo-mutants gaining a rust dependency.
cargo-fuzz dropping stable support without a sanitizer, or shipping an arm64 macOS
binary, which retires the Rosetta prerequisite. divan's maintenance blocking a toolchain
bump, which moves the bench to criterion with `default-features = false`. The fuzz crate's
lines making `just check` or the `rust` job slower than the maintainer accepts, which
moves them to `fuzz.yml`. A vendored CLI under `crates/alliumpy-core/src/cli/` after T13,
which settles whether its mutants are in scope and whether it earns a second fuzz target.

## Related pages

- [Testing](../reference/testing.md)
- [Quality gates](../reference/quality-gates.md)
- [Commands](../reference/commands.md)
- [Develop locally](../how-to/develop-locally.md)
- [Quality philosophy](../explanation/quality-philosophy.md)
- [Decision 0004: Dependency policy](0004-dependency-policy.md)
