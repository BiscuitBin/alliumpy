---
title: "Decision 0001: One wheel from two crates: a thin pyo3 crate over a tested core"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_one_wheel"]
requires: []
---

# Decision 0001: One wheel from two crates: a thin pyo3 crate over a tested core

## Context

The distribution must expose upstream's parser to Python and provide the `allium`
command in one installation. A cdylib alone cannot carry the inherited Rust evidence:
excluding the binding from nextest leaves zero tests, doctests run nothing, and coverage
reads zero. Testing only Python cannot measure the Rust conversion layer's floor.

## Decision

Build one wheel from two crates. The interpreter-independent core owns conversion and
Rust tests; the thin pyo3 binding exposes it through the Python package and console
shim. [Architecture](../explanation/architecture.md) owns placement and [Python
packaging](../explanation/packaging.md) owns the distribution mechanics. S01 selects the
command route; that open choice does not change this crate boundary.

## Consequences

Rust tests and the coverage denominator remain meaningful without a Python loader. Users
resolve one distribution rather than synchronising an API package and a command. The
cost is two manifests and a conversion boundary to maintain, with pytest, stubtest and
the installed-wheel smoke still needed to prove the Python side.

## What would reopen this

A second consumer needing the core without Python, or a CLI-only package whose users
should not install Python, would reopen the distribution shape.

## Related pages

- [Architecture](../explanation/architecture.md)
- [Python packaging](../explanation/packaging.md)
- [CLI strategy](0014-cli-strategy.md)
