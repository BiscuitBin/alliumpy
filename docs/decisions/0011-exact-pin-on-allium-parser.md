---
title: "Decision 0011: An exact pin on `allium-parser`"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_upstream_pin"]
requires: []
---

# Decision 0011: An exact pin on `allium-parser`

## Context

Upstream's README carries a pre-release notice. Its cross-module function signatures
have grown between releases, and the recorded cadence is two to five releases a month.
This repository packages upstream behaviour rather than defining a compatible parser of
its own: resolving a different release can change the product without a reviewed release
here.

## Decision

Use `allium-parser = "=3.6.1"` in the workspace dependency table. This is the one
exception to [decision 0004](0004-dependency-policy.md)'s caret-range policy.
`Cargo.lock` still pins the whole resolution and every resolving Cargo gate uses it.

An upstream bump is a release: update the pin, re-vendor if S01 selects that route, run
T13's parity when available, align the wheel version, then follow T14's release process.
T17 adds the runbook and configures Renovate to leave this pin alone. No updater exists
on this main yet.

## Consequences

Unexpected compatible-range resolution cannot silently change parser behaviour. The cost
is deliberate manual release work and an ageing upstream version until that work
happens. An exact pin is no guarantee that upstream is secure or correct; it makes the
reviewed version reproducible.

## What would reopen this

An upstream stability promise covering API signatures and behaviour across compatible
versions, with evidence that the promise fits this wrapper's parity requirements.

## Related pages

- [Dependency policy](0004-dependency-policy.md)
- [Version tracks upstream](0010-version-tracks-upstream.md)
- [Maintenance](../operations/maintenance.md)
