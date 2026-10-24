---
title: "Decision 0013: No specification gate and no Allium skills in this repository"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_no_spec_gate"]
requires: []
---

# Decision 0013: No specification gate and no Allium skills in this repository

## Context

This repository builds the `allium` command other repositories use to check their Allium
specifications. Installing another project-managed allium for a specification gate here
would shadow the wheel's command or be shadowed by it. A passing invocation could then
test the wrong executable.

## Decision

Do not carry the specification gate, its installer, its runner or the vendored Allium
skills into this repository. Keep the seven house skills, including the Python change
skill, and the shared documentation and agent contracts. Upstream decides parser and
command behaviour; this repository tests its packaging and conversion against upstream.
[Agent contract](../reference/agent-contract.md) owns the inventory.

## Consequences

There is one command under test, with no independently installed checker competing for
its name on PATH. Contributors do not have the language-specific skill inventory used by
repositories that author specifications. The handbook names upstream's language
documentation rather than restating it.

## What would reopen this

A way to run a specification gate through this repository's own installed wheel, proving
the selected executable and retaining an offline, reproducible gate.

## Related pages

- [Agent contract](../reference/agent-contract.md)
- [Security model](../explanation/security-model.md)
- [Purpose and scope](../project/purpose-and-scope.md)
