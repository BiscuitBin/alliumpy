---
title: "Decision 0019: The `alliumpy gate` script, its exit policy and its Typer dependency"
kind: "decision"
audience: ["user", "contributor", "maintainer", "agent"]
canonical_for: ["decision_gate_script"]
requires: []
---

# Decision 0019: The `alliumpy gate` script, its exit policy and its Typer dependency

## Context

A repository that adopts Allium wants one command for CI that fails on a broken
specification. Upstream's command offers two, and their exit statuses answer different
questions. `allium check` exits 1 when any file has an error or a warning. `allium
analyse` exits 1 only when a file has a finding, so an error with no finding exits 0.
Both exit 1 when a file cannot be read, and 2 when no `.allium` file is found. Running
both and combining the statuses by hand is the gate every adopter would otherwise write.

Upstream's language version 4 changes this: there, both commands exit 1 on any error
or warning. A version 3 specification keeps the rule above. The pin is 3.6.1, whose
command knows language versions 1 to 3.

[Decision 0009](0009-pypi-name-alliumpy.md) gave the wheel one script, `allium`, so
`uvx` needs `--from alliumpy`. S02's option 2 proposed a second script named after the
distribution, which `uvx alliumpy` finds with no `--from`.

## Decision

The wheel gains a second console script, `alliumpy`, with one subcommand, `gate`.
`alliumpy gate PATHS...` runs upstream's `check` and then `analyse` on the paths through
the Python API (`alliumpy.check` and `alliumpy.analyse`), in process. It prints one line
per diagnostic, `file:line:col: severity: message [code]`, each diagnostic once though
both commands report the parser's. It prints one line per finding, `file: finding type:
summary`, and ends with a one-line count.

The exit policy is this repository's, decided by the maintainer on 2026-11-23:

| Status | Meaning |
| --- | --- |
| 0 | Every file was read and no file has an error or a warning. |
| 1 | The gate failed: a file has an error or a warning, or a file cannot be read. |
| 2 | A usage error, a path that is not UTF-8, or no `.allium` file was found. |
| 3 | The checker could not report: it panicked, or printed something other than its reports. |

`info` diagnostics and `analyse` findings are printed and do not fail the gate by
default. An unreadable file fails it although the command gives it no report, because
the command's stderr names it. Typer gives a usage error status 2, as upstream's
command gives its own. Like the `allium` script, the gate restores SIGINT's default
action, so an interrupt ends the run at once instead of exiting 1 as a failed gate.

Two options let an adopter with existing diagnostics choose what fails; the defaults
are the policy above. `--fail-on error|warning|info`, default `warning`, fails on any
diagnostic at or above that severity. `--fail-on-findings`, default off, also fails on
any finding. An unreadable file fails under every choice. There is no baseline file:
S02 left that open. `--format github` prints each diagnostic as a GitHub Actions
workflow command, `::error`, `::warning` or `::notice` for error, warning and info,
with the file, line and column, and each finding as a file-only `::notice`, or
`::error` when findings fail the gate. An unreadable file becomes a bare `::error`
on stdout. Messages and properties are escaped as the workflow-command syntax
requires. `--format text`, the default, is the output above.

The gate is outside the parity invariant, which covers the `allium` script alone: its
output and its statuses are not upstream's, and `just parity` does not test them.
`allium` is unchanged. The policy does not follow the executable: a later pin whose
command applies the version 4 rule leaves the gate's statuses as the table gives them,
for every language version.

Typer is the wheel's first runtime dependency. [Decision 0004](0004-dependency-policy.md)
was written for crates; its note extends to Python here. The wheel's manifest declares
the caret range of the 0.x release, `typer>=0.29.2,<0.30`, and the root
`pyproject.toml` pins `typer ==0.29.2` from conda-forge, which `pixi.lock` locks. Every
gate tests that pinned copy. Typer is imported in `_gate.py` and nowhere else, so the
library and the `allium` script never load it, and a pytest case proves it. Renovate
([decision 0017](0017-renovate.md)) proposes the pin and the range in one pull request.

Typer 0.29.2 declares `pydantic>=2.5.3`, `rich>=13.8.0`, `shellingham>=1.3.0`,
`annotated-doc>=0.0.2`, and `colorama` on Windows. Through them an installer also brings
`pydantic-core`, a compiled package, `annotated-types`, `typing-inspection`,
`typing-extensions`, `markdown-it-py`, `mdurl` and `pygments`.

The local wheel smoke stays offline. Its venv is made with `--system-site-packages`
over the pixi interpreter, so Typer comes from the locked environment while the wheel
still installs `--no-deps` from `dist/`. The smoke proves that the wheel's metadata
declares Typer, that the pinned copy satisfies the range, and that `alliumpy` imports
from the venv rather than the editable copy. It runs both helps and the gate over the
two smoke fixtures. The CI job on Python 3.11 installs the wheel with its dependencies
from PyPI and runs the gate. The release workflow's smoke stays `--no-deps` and
exercises `allium` alone; the post-publish proof of the release that first carries the
gate runs `uvx alliumpy@<version> gate` from PyPI.

## Consequences

`uvx alliumpy gate specs/` works with no `--from`, and an adopter's CI needs one line.

Every install of the wheel now resolves Typer and the packages above, the library's
users included, who need none of them. That is the heaviest cost here: `pydantic-core`
is a native wheel per platform. The wheel stops being dependency-free, so an offline
install from a single wheel file no longer works without those packages beside it.

The gate's policy is a second policy to maintain beside upstream's. A user who reads
`allium analyse`'s status and the gate's will see them differ on an error with no
finding, by design.

Upstream's checker warns on an external entity that no rule names, in a module with no
`use` import, although its language reference documents the empty external entity as a
type placeholder that a consuming specification fills. Under the default policy a
specification using that pattern fails the gate unless `--fail-on error` is chosen.
`specs/allium-cli.allium`'s `CommandUser` is one such placeholder, so this repository
does not gate its own `specs/` yet: the adoption-gate ticket that would was handed
back to the maintainer on 2026-11-23.

Typer releases 0.x minors that may break, so the range stops below the next minor and
each minor is a Renovate pull request to review.

## What would reopen this

Upstream shipping a gate command of its own, or applying the version 4 exit rule to
every language version. A request from library users to install without Typer, which
an optional extra or a standard-library parser would answer. Typer changing its
dependencies again: its closure here is version 0.29.2's.

## Related pages

- [Decision 0004](0004-dependency-policy.md)
- [Decision 0009](0009-pypi-name-alliumpy.md)
- [Decision 0014](0014-cli-strategy.md)
- [Decision 0017](0017-renovate.md)
- [Install and run](../how-to/install-and-run.md)
