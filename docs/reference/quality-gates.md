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
| 1 | `lock-check` | The lockfile matches the manifest offline. |
| 2 | `lint` | The complete read-only hook gate passes. |
| 3 | `toml-check` | TOML formatting and lint pass. |
| 4 | `py-lint` | Ruff sees the package, lint and format pass, and the F401/E501 positive controls fire. |
| 5 | `py-typecheck` | mypy passes in strict mode and the deliberately invalid fixture returns status 1. |
| 6 | `py-test` | The unit suite and the golden suite over the captured fixtures pass, offline. |
| 7 | `wheel-smoke` | One freshly built wheel installs and works offline in an isolated venv: schemas, `init`, `doctor`, `report`. |
| 8 | `version-check` | The manifest version, `__version__` and the smoked command's output agree. |
| 9 | `check-docs` | The documentation contract, spelling, Markdown and local links pass. |
| 10 | `check-agents` | The canonical instructions, adapters, skills and bridges satisfy their contract. |

After these ten gates, `check-clean` compares the worktree with the starting snapshot. A
green dirty baseline means the checks changed nothing; hand-back additionally requires a
committed clean worktree. Gate 3 also runs inside lint deliberately, so a failure has a
named place in the aggregate list.

## Evidence that checks can fail

A ruff run over nothing can pass, so py-lint requires the package in `--show-files`.
Its fixture must exist and fail with status 1 naming both F401 and E501; a tool error or
a different rule is insufficient. mypy's deliberate assignment error must return 1,
rather than status 2 for a usage error. The golden suite is the fidelity gate: a
snapshot that changes makes the diff visible in review, and a construct the converter
cannot carry is an `xfail` naming it, never a relaxed threshold.

The wheel smoke empties dist, requires one real wheel and installs only that artefact
with offline, no-index and no-deps flags into a venv that sees the pixi environment's
site-packages for the runtime dependencies. Python runs with `-I`.

## What the hook gate contains

Read-only hooks include TOML formatting, Python lint and types, documentation and agent
contracts, EditorConfig, markdownlint, typos, offline links, shellcheck, actionlint,
secret scanning and builtin file hygiene. The Python recipes run through just to inherit
the pinned tool PATH. Contract hooks use frozen pixi resolution. pytest and wheel builds
are deliberately outside commit hooks; the full gate and CI run them. Captured fixtures
and `examples/` are excluded from the hooks: they are evidence, not prose.

Remote hooks use full commit SHAs; lychee is the exception, pinned in `pyproject.toml`
and run from the pixi environment because its upstream hook installs through the GitHub
API at first run. `.pre-commit-fix.yaml` is the mutating counterpart,
never installed, run by `just fix`; its positive-control fixtures are excluded from repair.

## Continuous integration

CI runs the offline gates on Linux and macOS in the `python` job, installs the Linux
wheel on Python 3.12 in `wheel-smoke-py312`, and runs lint and the two contracts in
`documents`. The aggregate `check` job fails if any dependency fails, is cancelled or
skipped. The `live` and `oracle` jobs run only on a manual dispatch that asks for them:
they reach the target sites and are not gates.

## Related pages

- [Commands](commands.md)
- [Quality philosophy](../explanation/quality-philosophy.md)
