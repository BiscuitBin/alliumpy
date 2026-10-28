---
name: project-check
description: Bring a workspace to a state where the full gate runs, and interpret what it reports.
---

# Run the full gate

1. Read `AGENTS.md`. The `Justfile` is the supported interface to the checks; use its
   recipes rather than assembling an equivalent pipeline by hand.
2. Check prerequisites: the pixi environment at `.pixi/envs/default/bin` with just,
   prek, taplo, uv, hatchling, pytest, ruff, mypy, the `bg-*` scripts and the package
   installed editable; `pixi.lock`. `just initialize` creates missing prerequisites and
   skips hook installation in a secondary worktree. It downloads, so it needs explicit
   authorization unless the task already grants it. The browser tier is not a
   prerequisite of the gate: `just install-browser` serves the live suite only.
3. Run `just check`. It runs the ten gates in order and snapshots the worktree between
   them: 1 locks, 2 hooks, 3 TOML, 4 Python lint, 5 Python typing, 6 pytest (unit and
   golden), 7 installed wheel smoke, 8 versions, 9 documentation, 10 agents; then
   `check-clean`.
4. Read only the first failure and rerun the named recipe. Later failures often follow
   from earlier ones.
5. A recipe that changes the worktree is defective: checks are read-only; `just fix`
   is where mutation belongs.
6. Hand a failing gate to `fix-quality` rather than working around it.
7. Report success only when `just check` ends with
   `All checks passed and the worktree is unchanged.` and `git status --short` prints
   nothing after the commit. Quote outputs against the commit actually tested, marking
   uncommitted changes when present, with exit status and any outstanding findings.
