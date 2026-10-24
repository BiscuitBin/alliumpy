---
name: project-check
description: Bring a workspace to a state where the full gate runs, and interpret what it reports.
---

# Run the full gate

1. Read `AGENTS.md`. The `Justfile` is the supported interface to the checks; use its
   recipes rather than assembling an equivalent pipeline by hand.
2. Check prerequisites: rustup's cargo first on `PATH` (`just check-toolchain` proves
   it); the pixi environment at `.pixi/envs/default/bin` with nextest, llvm-cov, deny,
   shear, taplo, prek, just, the `bg-*` scripts, maturin, uv, pytest, ruff and mypy;
   `.tools/bin/cargo-hack`, `.tools/bin/rustqual`, `Cargo.lock` and `pixi.lock`.
   `just initialize` creates missing prerequisites and skips hook installation in a
   secondary worktree. It downloads, so it needs explicit authorization unless the
   task already grants it. `just install-tools` provisions only the two tool lists
   under the same authorization rule. Rustqual is needed for gate 7, cargo-hack for
   gate 8; the Python tools serve gates 14–19. No reference `allium` belongs in
   `.tools/bin`: it would shadow the wheel's command.
3. Run `just check`. It runs the 22 gates in `tickets/CONVENTIONS.md` §4 order and
   snapshots the worktree between them: 1 toolchain, 2 locks, 3 hooks, 4–5 formatting,
   6 clippy, 7 metrics, 8 features, 9 doctests, 10 core coverage, 11 rustdoc,
   12 dependency policy, 13 unused dependencies, 14 Python lint, 15 Python typing,
   16 pytest, 17 stubtest, 18 installed wheel smoke, 19 versions, 20 documentation,
   21 agents, 22 snapshots; then `check-clean`.
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
