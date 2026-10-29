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

These are decisions about how this repository is built and checked. The smaller choices
the build prompt left open are logged in [Build decisions](../decisions.md); a choice
with lasting consequences for the repository gets a numbered record here.

## The record

| Number | Decision |
| --- | --- |
| [0002](0002-hook-runner-and-checkers.md) | Hook runner and checkers |
| [0015](0015-docmirror-in-place-of-alliumpy.md) | docmirror in place of alliumpy, on its toolchain |
| [0016](0016-keep-a-distilled-allium-spec.md) | Keep a distilled Allium spec |

Records 0001 and 0003 to 0014 belonged to `alliumpy` and were removed with the Rust
crates, 0006 among them because its tool list was the Rust one; their numbers stay retired so that a citation in the hosting repository's
history still means one thing.

## The numbering

This series is the hosting repository's own and starts at 0001. Record 0002 carries the
chain from the pinned source repositories and keeps its topic slug; its opening names
both source commits so its argument can be checked. New records have no carried-from
chain. [Decision 0015](0015-docmirror-in-place-of-alliumpy.md) owns the tool manager
and dependency policy that the retired records 0004 and 0006 used to.

## Writing a new one

Copy the shape of an existing entry: context, the decision, the consequences including
the ones that hurt, and what would reopen it. Add the file, add a manifest entry, add a
row above. A decision nobody can find is not recorded.

## Related pages

- [Documentation map](../README.md)
- [Build decisions](../decisions.md)
