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
| 1 | `check-toolchain` | Cargo resolves to the expected rustup proxy path; the selected toolchain is printed. |
| 2 | `lock-check` | Both lockfiles match their manifests offline. |
| 3 | `lint` | The complete read-only hook gate passes. |
| 4 | `fmt-check` | Rust formatting matches rustfmt. |
| 5 | `toml-check` | TOML formatting and lint pass. |
| 6 | `clippy` | Both lint tables pass over every target and feature, with warnings as errors. |
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
| 19 | `version-check` | The suffix-stripped wheel version, root workspace version, upstream pin, core constant and installed version output agree. |
| 20 | `check-docs` | The documentation contract, spelling, Markdown and local links pass. |
| 21 | `check-agents` | The canonical instructions, adapters, skills and bridges satisfy their contract. |
| 22 | `snapshots-check` | All core snapshots match and no committed snapshot is unreferenced; locks are checked first and tests run offline. |

After these twenty-two gates, `check-clean` compares the worktree with the starting
snapshot. A green dirty baseline means the checks changed nothing; hand-back additionally
requires a committed clean worktree. Gates 4 and 5 also run inside lint deliberately,
so a failure has a named place in the aggregate list.

The toolchain gate does not compare the selected compiler with `rust-toolchain.toml`.
Check its printed selection: `RUSTUP_TOOLCHAIN` or a directory override can supersede
the repository pin. Remove an unintended override before running the gate.

## Evidence that checks can fail

A ruff run over nothing can pass, so py-lint requires the package in `--show-files`.
Its fixture must exist and fail with status 1 naming both F401 and E501; a tool error or
a different rule is insufficient. mypy's deliberate assignment error must return 1,
rather than status 2 for a usage error. stubtest's allowlist stays short: each entry
hides a discrepancy. T03 reviews it and tests a deliberate stub error.

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

T01 replaces the foundation's one-job workflow with six gate jobs: `rust`, `python`,
`wheel-smoke-py311`, `coverage`, `deny` and `documents`. The aggregate `check` job must
fail if any dependency fails, is cancelled or skipped. The Python job uploads the Linux
wheel and the Python 3.11 job installs that same artefact. The Rust job runs test where
the local aggregate runs test-doc and coverage. These are the designed T01 job names;
T11 reconciles them with the merged workflow.

Audit and online links need network services and sit outside the gate. Pages also sits
outside it: a deployment failure blocks no merge, and deployment runs only for main on
a public repository. Branch protection depends on visibility and plan; this page does
not claim the initially private free-plan repository already has it.

## Related pages

- [Commands](commands.md)
- [Quality philosophy](../explanation/quality-philosophy.md)
- [Testing](testing.md)
