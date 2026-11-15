---
title: "Quality gates"
kind: "reference"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["quality_gate_reference"]
requires: []
---

# Quality gates

`just check` runs the gates in the order below and snapshots the worktree between each
one. A recipe that modifies a file Git does not ignore fails the run, because checks are
read-only; an ignored path is outside the snapshot.

| Order | Gate | Proves |
| --- | --- | --- |
| 1 | `check-toolchain` | The dev shell is the one the committed flake files produce; cargo, rustc, rustfmt and clippy resolve inside the flake's toolchain and every other gate tool inside the shell's own packages; rustc and cargo report the channel `rust-toolchain.toml` pins. The toolchain and host are printed. |
| 2 | `lock-check` | `Cargo.lock`, `fuzz/Cargo.lock` and `flake.lock` match their manifests offline. |
| 3 | `lint` | The complete read-only hook gate passes. |
| 4 | `fmt-check` | Rust formatting matches rustfmt, in the workspace and the fuzz crate, and the flake's Nix files match nixfmt. |
| 5 | `toml-check` | TOML formatting and lint pass. |
| 6 | `clippy` | Both lint tables pass over every target and feature, and the fuzz crate's repeated tables over its targets, with warnings as errors. |
| 7 | `metrics` | The pinned rustqual passes once per crate against the configured thresholds. |
| 8 | `features` | Every feature combination compiles. |
| 9 | `test-doc` | Core doc examples compile and pass. |
| 10 | `coverage` | Core nextest tests pass and line coverage is at least 90 percent. |
| 11 | `doc` | Both crates have warning-free rustdoc. |
| 12 | `deny` | Shipping dependencies have permitted licences, bans and sources. |
| 13 | `deps-unused` | No crate declares an unused dependency. |
| 14 | `py-lint` | Ruff sees the package, lint and format pass, and the F401/E501 positive controls fire. |
| 15 | `py-typecheck` | mypy passes and the deliberately invalid fixture returns status 1. |
| 16 | `py-test` | The rebuilt extension passes pytest. |
| 17 | `py-stubtest` | The built native API agrees with the stub and reviewed allowlist. |
| 18 | `wheel-smoke` | One freshly built release wheel installs and works offline in an isolated venv. |
| 19 | `version-check` | The suffix-stripped wheel version, root workspace version, each workspace member crate's version as cargo resolves it, upstream pin, core constant and installed version output agree, and the whole output equals `ALLIUM_VERSION_STRING`. |
| 20 | `check-docs` | The documentation contract, spelling, Markdown and local links pass. |
| 21 | `check-agents` | The canonical instructions, adapters, skills and bridges satisfy their contract. |
| 22 | `snapshots-check` | All core snapshots match and no committed snapshot is unreferenced; locks are checked first and tests run offline. |

`parity` sits outside this list because its reference needs the network to build; the
`parity` CI job runs it, and [Testing](testing.md#command-parity) says what it proves.

After these twenty-two gates, `check-clean` compares the worktree with the starting
snapshot. A green dirty baseline means the checks changed nothing; hand-back additionally
requires a committed clean worktree. Gates 4 and 5 also run inside lint deliberately,
so a failure has a named place in the aggregate list.

The toolchain gate reads its checks from the shell itself. The dev shell exports a digest
of `flake.nix`, `flake.lock`, `rust-toolchain.toml` and `nix/*.nix`, and the gate
recomputes it from the worktree, so a shell entered before a pull, a lock or an edit is
refused. Tools are checked by where they resolve, not by their order on `PATH`, so a
rustup proxy, a Homebrew cargo or a uv in `~/.local/bin` placed ahead of the shell is
refused by name. Each refusal starts `check-toolchain:` and exits 2;
[Troubleshooting](../operations/troubleshooting.md) has the remedies. Outside the dev
shell no recipe runs at all ([decision 0018](../decisions/0018-nix-dev-environment.md)).

## Evidence that checks can fail

A ruff run over nothing can pass, so py-lint requires the package in `--show-files`.
Its fixture must exist and fail with status 1 naming both F401 and E501; a tool error or
a different rule is insufficient. mypy's deliberate assignment error must return 1,
rather than status 2 for a usage error. stubtest's allowlist is empty: each entry
would hide a discrepancy, and a deliberate stub error fails py-stubtest.

The wheel smoke empties dist, requires one real wheel and installs only that artefact
with offline, no-index and no-deps flags. Python runs with `-I`. The core's small
coverage denominator makes a single untested branch material. Metrics runs the rustqual
`nix/rustqual.nix` pins, which gate 1 has proved comes from the store; internal
module-boundary rules and their positive control
will arrive with modules, rather than claiming an empty rule set enforces a graph.

## What the hook gate contains

Read-only hooks include Rust and TOML formatting, unused dependencies, Python lint and
types, documentation and agent contracts, EditorConfig, markdownlint, typos, offline
links, shellcheck, actionlint, secret scanning and builtin file hygiene.
Every hook is a system hook on a binary the dev shell provides, so `flake.lock` pins
each checker and nothing is cloned or downloaded. The Rust, TOML and Python hooks run
through just, which keeps each tool's arguments in one place. Clippy, pytest, stubtest
and wheel builds are deliberately outside commit hooks because they build; the full gate
and CI run them.

`.pre-commit-fix.yaml` is the mutating counterpart, never installed, run by `just fix`;
its positive-control fixtures are excluded from repair. Actionlint validates workflow
structure and runs the shell's shellcheck over `run:` blocks in `bash` or `sh`. It does
not recognise the dev-shell default shell the gate jobs set, so it skips the `run:`
blocks of those jobs. Review multi-line workflow shell there explicitly.

## Continuous integration

CI runs seven gate jobs: `rust`, `python`, `wheel-smoke-py311`, `parity`, `coverage`,
`deny` and `documents`. The aggregate `check` job fails if any of them fails, is cancelled
or skipped. Every gate job but `wheel-smoke-py311` runs the shared setup action and then
its `run:` steps inside the dev shell, so CI and a local `just check` share one
environment. The Python job uploads the Linux wheel and the Python 3.11 job installs that
same artefact on a stock interpreter outside Nix. `macos-smoke`, outside `check`'s
`needs`, runs check-toolchain, build, test, fuzz-build and wheel-smoke in the dev shell
on Apple silicon. The Rust job runs test where the local aggregate runs test-doc and
coverage, and runs `fuzz-build` after `clippy`, so a fuzz target that no longer builds
names itself in the step list without waiting for the weekly run.

Audit and online links need network services and sit outside the gate. Mutation
testing, benchmarks and fuzzing sit outside it on purpose: a surviving mutant or a crash
asks for a judgement, mutation runs grow towards hours, fuzzing is nondeterministic, and
timings measure the machine. `mutants.yml` and `fuzz.yml` run weekly and by hand and are
never in `check`'s `needs`; no benchmark runs in CI
([decision 0016](../decisions/0016-mutation-bench-and-fuzz.md)). Pages also sits
outside it: a deployment failure blocks no merge, and deployment runs only for main
while the repository is public (`github.event.repository.private == false`). The
repository is public, and branch protection on main requires the `check` job alone.

## Related pages

- [Commands](commands.md)
- [Quality philosophy](../explanation/quality-philosophy.md)
- [Testing](testing.md)
