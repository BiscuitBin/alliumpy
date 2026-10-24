---
title: "Decision 0012: `abi3-py311` wheels and the five platforms"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_wheel_platforms"]
requires: []
---

# Decision 0012: `abi3-py311` wheels and the five platforms

## Context

A Python parser API backed by Rust needs a native wheel for each supported platform. One
wheel per Python minor would multiply builds and releases, while free-threaded Python
has a separate ABI. The local gate cannot stand in for release evidence across all
operating systems.

## Decision

Use pyo3 `abi3-py311` for CPython 3.11 and newer, plus the separate `cp314t` wheel for
free-threaded Python 3.14. T14 verifies what maturin's generator emits and rehearses the
release matrix: Linux x86_64 and aarch64, each with manylinux and musllinux; macOS arm64
and x86_64; Windows x86_64.

[Python packaging](../explanation/packaging.md) owns the matrix and build mechanics. The
Justfile is POSIX-only, and pixi supports `linux-64` and `osx-arm64` here. Local `just
check` builds one developer wheel; T01 adds the CI Python 3.11 floor smoke. Other
targets are release-matrix builds, and T14's rehearsal is the Windows proof. T13 proves
parity on POSIX only.

## Consequences

The stable ABI reduces per-Python builds without lowering the floor below 3.11. A green
local check does not certify macOS x86_64, Windows, musllinux or free-threaded Python.
Release automation must supply that evidence, including console launchers and exit
codes. Unsupported platforms may raise the sdist question, still pending S01.

## What would reopen this

A concrete request for another platform or a new Python floor, accompanied by build and
smoke evidence for the proposed matrix.

## Related pages

- [Python packaging](../explanation/packaging.md)
- [Testing](../reference/testing.md)
- [Install and run](../how-to/install-and-run.md)
