---
title: "Layering and dependency direction"
kind: "explanation"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["dependency_boundaries"]
requires: []
---

# Layering and dependency direction

Cargo enforces the crate direction:

```text
Python package -> alliumpy -> alliumpy-core -> allium-parser
```

`alliumpy` depends on `alliumpy-core`, which depends on `allium-parser`; never the
reverse. pyo3 appears only in `crates/alliumpy`. The core can therefore compile and run
its tests without a Python interpreter. The [architecture](architecture.md) owns the
allocation of responsibilities to those crates.

## Why the direction matters

The rule is not tidiness. Conversion can be tested against known source spans without
loading Python. A Python wrapper that calculates language behaviour would leave that
behaviour outside the core's measured tests and give two layers authority over one rule.
Move such logic into the core and keep the wrapper a conversion.

Python source lives under the bindings crate's `python/` and `tests/`, root `tests/`
for smoke and future parity harnesses, and `scripts/` for tooling. Rust tests belong
in the core; pytest exercises the native binding.

## Enforcement

Cargo's dependency graph prevents a crate cycle, and manifest review keeps pyo3 confined
to the binding. The core currently has no internal module graph to constrain.
`rustqual.toml` keeps the carried complexity, cohesion and coupling thresholds;
module-boundary patterns wait until modules exist. A pattern must arrive with a positive
control that proves it fires. Review also checks aliases, relative paths and re-exports:
textual path rules cannot establish every possible dependency relationship.

## Related pages

- [Testing](../reference/testing.md)
- [Decision 0007](../decisions/0007-metrics-gate.md)
