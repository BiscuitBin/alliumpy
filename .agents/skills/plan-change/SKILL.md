---
name: plan-change
description: Plan a change when the scope, affected specifications, risks, or validation need evidence before any code is written.
---

# Plan a change

1. Read `AGENTS.md` and upstream's documentation for the behaviour in question at the
   pinned version. Separate what you read from what you are guessing.
2. Inspect the worktree before proposing anything, and preserve work you did not author.
3. Write down the observable outcome and explicit non-goals, so the scope can be reviewed.
4. Identify whether behaviour changes. Behaviour is upstream's to change: a difference
   from `allium-cli` at the pin is a defect here unless a decision record says otherwise
   (invariant 1). Identify the upstream result to reproduce before planning an adaptation.
5. Identify the boundaries crossed: the crate direction of invariant 2, the Python API's
   shape (`crates/alliumpy/python/alliumpy/_alliumpy.pyi` is canonical), and a new topic's
   owning page in `docs/manifest.yml`. An exposed API change moves the stub, the Rust
   binding and a pytest case together.
6. Name the risks and evidence that would settle them, and say which actions need
   authorization the agent does not already have.
7. Split into independently verifiable steps, each pairing behaviour, test and documentation.
8. Present the plan with open questions marked as open. Confirm the work runs green
   with `just check` before treating it as done.
