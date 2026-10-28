---
title: "Decision 0002: Hook runner and checkers"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_python_toolchain"]
requires: []
---

# Decision 0002: Hook runner and checkers

Carried from pachinko's decision 0004 at `bf51e0d`, which carried libpawdoku's decision 0004 at `ccdd001`.

## Context

The quality gate is the one every Biscuit Games repository runs: prek runs the hooks,
and the shared `biscuit-games-tooling` package supplies the documentation and agent
validators, the ordered gate with worktree snapshots, and the secret-checking wrapper. The contract validators have no house replacement, and this repository is Python
throughout.

## Decision

Keep the Python checkers and prek. The root `pyproject.toml` configures the shared
package and names the ten gate recipes in order. [Decision
0015](0015-docmirror-in-place-of-alliumpy.md) owns their installation through pixi; no
fork of the checkers lives here.

Until the required phrases become configurable, `AGENTS.md` carries honest explanations
for phrases the validator requires but this repository does not otherwise use; the
[agent contract](../reference/agent-contract.md) records that compatibility requirement.

## Consequences

The gate is the same gate the other house repositories run, from the same pinned
package. A fix to a checker arrives as a pin move rather than a local fork. Both
contracts are enforced mechanically from the foundation, which lets later lanes replace
registered pages, records and skills under a green gate.

The cost is interim agent contract wording for a checker shared with other stacks.
Python is also the delivered interface here, so the tooling environment costs nothing
extra.

## What would reopen this

The checkers being rewritten as binaries inside the shared package, or the validators
becoming simple enough that a rewrite is cheaper than an interpreter. A change must
replace the package's whole contract rather than only the ordered runner.

## Related pages

- [Decision 0015: docmirror in place of alliumpy, on its toolchain](0015-docmirror-in-place-of-alliumpy.md)
- [Quality gates](../reference/quality-gates.md)
- [Develop locally](../how-to/develop-locally.md)
