---
title: "Architecture decisions"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_index"]
requires: []
---

# Architecture decisions

This is a T00 stub; T07 replaces it.

This index will be the record of what was chosen for this repository, what it cost, and
what would have to change for each choice to be revisited. The series is this
repository's own and starts at 0001; records carried from the repository it was adapted
from say so under their heading and keep the topic slug they had. Lane T07 writes the
full index and records 0001 to 0013; T13 writes record 0014 from S01's decision. Until
then each record is a stub that names what it will say. This index is reshaped from
pachinko's decision index.

## The record

| Number | Decision |
| --- | --- |
| [0001](0001-one-wheel-two-crates.md) | One wheel from two crates: a thin pyo3 crate over a tested core |
| [0002](0002-hook-runner-and-checkers.md) | Hook runner and checkers |
| [0003](0003-apache-2-0-with-upstream-mit.md) | Apache-2.0 for this repository, upstream's MIT shipped beside it |
| [0004](0004-dependency-policy.md) | Dependency policy: caret ranges and `Cargo.lock` |
| [0005](0005-rust-quality-gate.md) | The Rust quality gate |
| [0006](0006-tool-manager.md) | Tool manager |
| [0007](0007-metrics-gate.md) | The metrics gate |
| [0008](0008-api-reference-on-github-pages.md) | The API reference on GitHub Pages, when the repository's visibility allows it |
| [0009](0009-pypi-name-alliumpy.md) | PyPI name `alliumpy`, console script `allium` |
| [0010](0010-version-tracks-upstream.md) | The wheel version tracks upstream, with `.postN` for packaging fixes |
| [0011](0011-exact-pin-on-allium-parser.md) | An exact pin on `allium-parser` |
| [0012](0012-abi3-wheels-and-platforms.md) | `abi3-py311` wheels and the five platforms |
| [0013](0013-no-spec-gate-no-allium-skills.md) | No specification gate and no Allium skills in this repository |
| [0014](0014-cli-strategy.md) | How the `allium` command gets into the wheel |

Records from 0015 onwards are written by wave-2 tickets, which register their
new pages and add a row here when the corresponding decision is taken.
