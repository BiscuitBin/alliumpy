---
title: "Documentation map"
kind: "project"
audience: [user, contributor, maintainer, operator, agent]
canonical_for: [documentation_navigation]
requires: []
---

# Documentation map

Every page below is registered in `manifest.yml`, owns at least one topic, and is
reachable from here. That is the whole of the arrangement; the rules behind it are in
the documentation contract, listed under Look up.

This repository is a Cargo workspace of two crates: `crates/alliumpy-core`,
the interpreter-independent parser conversion layer, and `crates/alliumpy`,
the thin pyo3 bindings. Together they build one Python wheel, `alliumpy`,
which also provides the `allium` console script.

## Start here

- [Install and run](how-to/install-and-run.md) — install the wheel and use its Python API.

- [Purpose and scope](project/purpose-and-scope.md) — what the workspace is for, and what it is not.
- [Repository map](project/repository-map.md) — where everything lives.
- [Terminology](project/terminology.md) — the words this repository uses precisely.
- [Make your first change](tutorials/first-change.md) — clone to green gate, through one small change and its tests.

## How to

- [Develop locally](how-to/develop-locally.md)
- [Test and debug](how-to/test-and-debug.md)
- [Maintain dependencies](how-to/maintain-dependencies.md)
- [Deploy to GitHub Pages](how-to/deploy-to-github-pages.md)

## Understand

- [Python packaging](explanation/packaging.md) — the wheel, manifests and ABI floor.

- [Architecture](explanation/architecture.md) — how the core, bindings and console script fit together.
- [Layering and dependency direction](explanation/layering.md) — which crate and module may depend on which.
- [Security model](explanation/security-model.md) — the supply chain and the treatment of untrusted parser inputs.
- [Quality philosophy](explanation/quality-philosophy.md) — why each gate exists.

## Look up

- [Commands](reference/commands.md)
- [Configuration](reference/configuration.md)
- [Testing](reference/testing.md)
- [Quality gates](reference/quality-gates.md)
- [Documentation contract](reference/documentation-contract.md)
- [Agent contract](reference/agent-contract.md)
- [API reference](reference/api.md)

## Run it

- [Maintenance](operations/maintenance.md)
- [Troubleshooting](operations/troubleshooting.md)

## Decisions

- [Architecture decisions](decisions/README.md) — the record of what was chosen and why.
