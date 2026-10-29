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

This repository holds `docmirror`, a command-line tool that mirrors a documentation
website into a local, interlinked Markdown knowledge base. The product itself is
documented in the root `README.md` (installation, quick start, configuration, exit codes
and what is lossy); this handbook covers how the repository is built and checked.

## Start here

- [Purpose and scope](project/purpose-and-scope.md) — what the tool is for, and what it is not.
- [Site notes](site-notes.md) — what the target sites actually do, selector by selector.
- [Build decisions](decisions.md) — the choices the build prompt left open, and what was chosen.

## How to

- [Develop locally](how-to/develop-locally.md)

## Understand

- [Quality philosophy](explanation/quality-philosophy.md) — why each gate exists.

## Look up

- [Commands](reference/commands.md)
- [Quality gates](reference/quality-gates.md)
- [Documentation contract](reference/documentation-contract.md)
- [Agent contract](reference/agent-contract.md)
- [Behavioural specification](specs/README.md) — the Allium spec distilled from the code.

## Run it

- [Troubleshooting](operations/troubleshooting.md)

## Decisions

- [Architecture decisions](decisions/README.md) — the record of what was chosen and why.
