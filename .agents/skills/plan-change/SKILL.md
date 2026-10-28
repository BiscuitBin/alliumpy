---
name: plan-change
description: Plan a change when the scope, affected fidelity rules, risks, or validation need evidence before any code is written.
---

# Plan a change

1. Read `AGENTS.md` and the build prompt's section for the behaviour in question.
   Separate what you read from what you are guessing; a selector or a site behaviour is
   a guess until `docs/site-notes.md` or a fetched page under `ai_tmp/` confirms it.
2. Inspect the worktree before proposing anything, and preserve work you did not author.
3. Write down the observable outcome and explicit non-goals, so the scope can be reviewed.
4. Identify which invariant the change touches: a fidelity rule needs a golden fixture;
   a profile change needs a live verification and a site-notes entry; a published
   artefact change moves its pydantic model, schema and a test together.
5. Name the risks and the evidence that would settle them, and say which actions need
   authorization the agent does not already have: live crawls, `just lock`,
   `just install-browser` and anything that leaves the worktree.
6. Split into independently verifiable steps, each pairing behaviour, test and documentation.
7. Present the plan with open questions marked as open, or, where the build prompt says
   not to ask, record the choice in `docs/decisions.md`. Confirm the work runs green
   with `just check` before treating it as done.
