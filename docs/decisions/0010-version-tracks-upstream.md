---
title: "Decision 0010: The wheel version tracks upstream, with `.postN` for packaging fixes"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_version_policy"]
requires: []
---

# Decision 0010: The wheel version tracks upstream, with `.postN` for packaging fixes

## Context

Users need the installed distribution to identify the upstream parser and command
behaviour it packages. Packaging fixes also need releases without implying that upstream
changed. Cargo cannot express Python's `.postN` suffix, so deriving the wheel version
only from Cargo would lose that distinction.

## Decision

Track upstream: the wheel version is `3.6.1` for upstream 3.6.1, with `3.6.1.postN` for
packaging-only releases. The wheel's `[project] version` stays static, never `dynamic =
["version"]`. The command prints upstream's version string, not the post-release suffix.
[Python packaging](../explanation/packaging.md) owns the copies.

`just version-check` checks the base version against the workspace version, upstream
pin, core constant and smoke-installed command. Package `__version__` uses installed
metadata so it includes the suffix. T14 owns release mechanics.

## Consequences

A user can identify the upstream release from the distribution version, and a packaging
repair remains distinguishable. Several static copies must move together; the gate
checks their agreement, not whether the selected upstream release is the right one. An
upstream update therefore requires reviewed behaviour and parity evidence too.

## What would reopen this

An upstream change that this repository must ship ahead of or behind upstream's release
version, making the current one-to-one version promise inaccurate.

## Related pages

- [Python packaging](../explanation/packaging.md)
- [Maintain dependencies](../how-to/maintain-dependencies.md)
- [API reference](../reference/api.md)
