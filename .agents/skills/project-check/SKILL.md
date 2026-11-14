---
name: project-check
description: Bring a workspace to a state where the full gate runs, and interpret what it reports.
---

# Run the full gate

1. Read `AGENTS.md`. The `Justfile` is the supported interface to the checks; use its
   recipes rather than assembling an equivalent pipeline by hand.
2. Check prerequisites: Nix with flakes, and every recipe run inside the flake's dev
   shell (`nix develop`, or direnv), which holds the pinned compiler with its
   components, every tool the gates call, Python with pytest and mypy, and the parity
   reference. Outside it the `Justfile` refuses to load, naming the way in.
   `just check-toolchain` proves the compiler is the pinned one from the Nix store.
   Entering the shell downloads whatever `flake.lock` names and the store lacks;
   `just initialize`, inside it, fetches the crates and installs hooks only in the
   primary checkout. Both reach the network, so they need explicit authorization
   unless the task already grants it.
3. Run `just check`. It runs the 23 gates in `tickets/CONVENTIONS.md` §4 order and
   snapshots the worktree between them: 1 toolchain, 2 locks, 3 hooks, 4–5 formatting,
   6 clippy, 7 metrics, 8 features, 9 doctests, 10 core coverage, 11 rustdoc,
   12 dependency policy, 13 unused dependencies, 14 Python lint, 15 Python typing,
   16 pytest, 17 stubtest, 18 installed wheel smoke, 19 versions, 20 documentation,
   21 agents, 22 snapshots, 23 Nix files; then `check-clean`.
4. Read only the first failure and rerun the named recipe. Later failures often follow
   from earlier ones. Gates 16–19 build the extension in debug for pytest and stubtest
   and in release for the wheel smoke: both artefacts are intentional evidence.
5. A recipe that changes the worktree is defective: checks are read-only; `just fix`
   is where mutation belongs.
6. Hand a failing gate to `fix-quality` rather than working around it.
7. Report success only when `just check` ends with
   `All checks passed and the worktree is unchanged.` and `git status --short` prints
   nothing after the commit. Quote outputs against the commit actually tested, marking
   uncommitted changes when present, with exit status and any outstanding findings.
