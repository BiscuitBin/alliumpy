---
title: "Decision 0009: PyPI name `alliumpy`, console script `allium`"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_pypi_name"]
requires: []
---

# Decision 0009: PyPI name `alliumpy`, console script `allium`

## Context

The distribution and command need not share a name. The recorded name check on
2026-10-22 found PyPI `allium` occupied by an unrelated astronomy package and
`allium-cli` by an active unrelated company's CLI. `alliumpy` returned 404. A pending
trusted publisher does not reserve a name, so this evidence is not a reservation.

## Decision

Use `alliumpy` for the Python distribution and import package, and `allium` for its
console command. The installation form is `uvx --from alliumpy allium ...` because `uvx
alliumpy` would search for a command named alliumpy. T14 rechecks availability and
proves installation on release day; nothing has been published yet.

## Consequences

The command keeps upstream's name while the distribution has an available distinct name.
Users must learn the `--from` form, and documentation must distinguish package and
command. T14 can still encounter a name taken since the recorded check.

## What would reopen this

A PEP 541 grant of the PyPI name `allium`, evaluated with an explicit migration plan for
existing alliumpy installations.

## Related pages

- [Install and run](../how-to/install-and-run.md)
- [Terminology](../project/terminology.md)
- [Python packaging](../explanation/packaging.md)
