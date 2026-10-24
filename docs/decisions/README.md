---
title: "Architecture decisions"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_index"]
requires: []
---

# Architecture decisions

A record of what was chosen, what it cost, and what would have to change for the choice
to be revisited. Each entry is numbered and never renumbered; a decision that is
superseded is marked rather than deleted, because the reasoning is what makes the
successor legible.

These are decisions about how this repository is built and distributed. Upstream decides
parser and command behaviour; unresolved packaging choices live in their spike or ticket
until evidence supports a decision.

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

Records 0015, 0016 and 0017 are written by T14, T15 and T17 respectively, which register
their new pages and add rows when those decisions are taken. Record 0014 remains S01's
draft for T13 to land; this lane leaves its stub untouched.

## The numbering

This series is the repository's own and starts at 0001. Records 0002 to 0008 carry the
chain from the pinned source repositories and keep their topic slugs. Each opening names
both source commits so its argument can be checked. New records have no carried-from
chain. [Decision 0006](0006-tool-manager.md) replaces the older installation details
behind [decision 0002](0002-hook-runner-and-checkers.md), while keeping its choice of
runner and shared checkers.

## Writing a new one

Copy the shape of an existing entry: context, the decision, the consequences including
the ones that hurt, and what would reopen it. Add the file, add a manifest entry, add a
row above. A decision nobody can find is not recorded. Follow-up tickets own additions
outside this lane's frozen inventory.

## Related pages

- [Documentation map](../README.md)
- [Architecture](../explanation/architecture.md)
