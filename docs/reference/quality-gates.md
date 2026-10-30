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
| 1 | `check-toolchain` | Cargo resolves to the expected rustup proxy path, and the active toolchain is the channel `rust-toolchain.toml` pins; the selected toolchain is printed. |
| 2 | `lock-check` | `Cargo.lock`, `fuzz/Cargo.lock` and `pixi.lock` match their manifests offline. |
| 3 | `lint` | The complete read-only hook gate passes. |
| 4 | `fmt-check` | Rust formatting matches rustfmt, in the workspace and the fuzz crate. |
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

The toolchain gate refuses an active toolchain other than the pinned channel for
rustup's default host. When `RUSTUP_TOOLCHAIN` or a `rustup override` supersedes the
repository pin, the gate names the toolchain it selects on stderr: remove the override
and rerun. An uninstalled override is refused, never downloaded.

## Evidence that checks can fail

A ruff run over nothing can pass, so py-lint requires the package in `--show-files`.
Its fixture must exist and fail with status 1 naming both F401 and E501; a tool error or
a different rule is insufficient. mypy's deliberate assignment error must return 1,
rather than status 2 for a usage error. stubtest's allowlist is empty: each entry
would hide a discrepancy, and a deliberate stub error fails py-stubtest.

The wheel smoke empties dist, requires one real wheel and installs only that artefact
with offline, no-index and no-deps flags. Python runs with `-I`. The core's small
coverage denominator makes a single untested branch material. Metrics checks the tool
version before invoking it; internal module-boundary rules and their positive control
will arrive with modules, rather than claiming an empty rule set enforces a graph.

## What the hook gate contains

Read-only hooks include Rust and TOML formatting, unused dependencies, Python lint and
types, documentation and agent contracts, EditorConfig, markdownlint, typos, offline
links, shellcheck, actionlint, secret scanning and builtin file hygiene.
The Python recipes run through just to inherit the pinned tool PATH. Contract hooks
use frozen pixi resolution. Clippy, pytest, stubtest and wheel builds are deliberately
outside commit hooks because they build; the full gate and CI run them.

Remote hooks use full commit SHAs. `.pre-commit-fix.yaml` is the mutating counterpart,
never installed, run by `just fix`; its positive-control fixtures are excluded from repair.
Actionlint validates workflow structure but can skip embedded shell analysis when its
own environment cannot find shellcheck. Review multi-line workflow shell explicitly.

## Continuous integration

CI runs six gate jobs: `rust`, `python`, `wheel-smoke-py311`, `coverage`, `deny` and
`documents`. The aggregate `check` job fails if any dependency fails, is cancelled or
skipped. The Python job uploads the Linux wheel and the Python 3.11 job installs that
same artefact. The Rust job runs test where the local aggregate runs test-doc and
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
