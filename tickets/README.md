# Tickets for bootstrapping `alliumpy`

This directory is the work breakdown for the foundation of `BiscuitBin/alliumpy`: one
PyPI package, `alliumpy`, that exposes the Allium parser and checker to Python code and
ships the `allium` command so that `uv` can install and run it. The package is built from
a Cargo workspace of two crates, a tested core over upstream's `allium-parser` and a thin
pyo3 bindings crate. These tickets carry pachinko's toolchain, gates, handbook, agent
contract and CI across, add the Python packaging, put `alliumpy 3.6.1` on PyPI (T14) and
end with Renovate over every pin but upstream's (T17).

Each ticket is written for an AI agent with no other context, working in its own git
worktree. `CONVENTIONS.md` is the shared design every ticket obeys and cites by section;
read it first, then the ticket.

Pushing, opening pull requests, tagging, publishing, registering a PyPI publisher,
approving a deployment, filing these as GitHub issues, changing repository or
organisation settings, installing a GitHub App, installing anything outside the worktree
and editing any other repository are separately authorised actions (`CONVENTIONS.md`
§11). Nothing here has been filed.

## Index

The `status:` field in each ticket's frontmatter is authoritative; this table is a
snapshot.

| Id | Title | File | Depends on | Parallel with | Status |
| --- | --- | --- | --- | --- | --- |
| T00 | Foundation: a shape-complete skeleton that passes `just check` and builds a wheel on its first commit | `T00-foundation.md` | none | none | done |
| T01 | GitHub repository and CI: settings, branch protection, workflows, the abi3 floor | `T01-github-and-ci.md` | T00 | T02, T03, T05, T07, S01 | done |
| T02 | Rust quality gate: tool configs, the bindings crate's lint table, metrics | `T02-rust-gate.md` | T00 | T01, T03, T05, T07, S01 | done |
| T03 | Python quality gate: ruff, mypy, the stub, pytest, the smoke fixtures | `T03-python-gate.md` | T00 | T01, T02, T05, T07, S01 | done |
| S01 | Spike: how the `allium` command gets into the wheel, with a parity harness | `S01-cli-strategy-spike.md` | T00 | T01, T02, T03, T05, T07 | done |
| T05 | Agent contract: AGENTS.md, seven house skills, the bridges | `T05-agent-contract.md` | T00 | T01, T02, T03, T07, S01 | done |
| T07 | Handbook: every page, and decision records 0001 to 0013 | `T07-handbook.md` | T00 | T01, T02, T03, T05, S01 | done |
| T11 | Integration: the first green `just check` from a fresh clone and in CI, protection read back | `T11-integration.md` | T01, T02, T03, T05, T07, S01 | none | open |
| T13 | The `allium` command in the wheel: S01's decision built, with parity proved | `T13-cli-in-the-wheel.md` | S01, T11 | T15 | open |
| T12 | Maintainer docs: README, CHANGELOG, SECURITY, the crate READMEs | `T12-maintainer-docs.md` | T11, T13 | T15 | open |
| T14 | Release: the rehearsed matrix, `release-pypi.yml` by trusted publishing, `alliumpy 3.6.1` on PyPI | `T14-release.md` | T12 | T15 | open |
| T15 | Mutation testing, benchmarks and fuzzing over `alliumpy-core` | `T15-mutants-bench-fuzz.md` | T11 | T12, T13, T14 | open |
| T17 | Renovate over every pin except the upstream crate; the upstream-bump runbook | `T17-renovate.md` | T14, T15 | none | open |
| T18 | Verification gaps: the checks the wave-0 and wave-1 hand-backs did not run | `T18-verification-gaps.md` | T11 | T12, T13, T14, T15, T17 | done |

The ids follow pachinko's where the ticket is the same kind of work, so that the two
repositories stay comparable, and fill the gaps pachinko left: T03 and S01 are new here;
T13 reuses the id of pachinko's container image, which is not carried (`CONVENTIONS.md`
§1 decision 5); T04, T06, T08, T09, T10 and T16 are unused (pachinko's T06 and T10 are
the specification and effects gates this repository does not have, its T10's metrics half
is folded into T02, and its T16 is folded into T15).

## Dependency graph

```text
T00 ─┬─ T01 ──────────────┐
     ├─ T02 ──────────────┤
     ├─ T03 ──────────────┤
     ├─ T05 ──────────────┼─ T11 ─┬─ T13 ── T12 ── T14 ─┐
     ├─ T07 ──────────────┤       │                     ├─ T17
     └─ S01 ──────────────┘       ├─ T15 ───────────────┘
                                  └─ T18
```

The graph is acyclic: T00, then six wave-1 lanes, then T11, then wave 2.

- **Wave 0, T00.** The tracer bullet through every layer, the wheel included. Nothing
  else can start until it has merged, because every lane replaces stubs it creates and
  every lane's definition of done is `just check` green, which only T00 can make true
  first.
- **Wave 1, T01, T02, T03, T05, T07 and S01.** Parallel lanes that share no path
  (`CONVENTIONS.md` §3, §11), with the frozen files frozen. S01 is a spike: it lands no
  code on `main`, only its hand-back notes with a recommendation, a drafted decision
  record and a drafted T13 body.
- **T11** reconciles the follow-ups all six wave-1 lanes, S01 included, handed back to
  `main` and proves the whole gate from a fresh clone and in CI.
- **Wave 2.** T13 and T15 start after T11. T12 waits for T13, so that the README that
  becomes the PyPI long description describes a proven command. T14 waits for T12,
  because the release publishes that description and reshapes `CHANGELOG.md`. The frozen
  list lifts after T11; each wave-2 ticket edits only its own lines in the shared files
  and merges one at a time, rebased on the last (`CONVENTIONS.md` §11).
- **T17** comes last because Renovate has to know every pin, and T13 to T15 add pins:
  the parity job's actions in `ci.yml` (the parity reference itself has no pin of its
  own: it follows `allium-parser`, which T17 excludes), the release workflow's actions,
  the mutation and fuzz tools.

## How to pick up a ticket

Before T00 starts, the `tickets/` directory is committed on `bootstrap-tickets` and that
branch is merged into `main` through a pull request (pushing and opening the pull request
are separately authorised), so that `CONVENTIONS.md` and every ticket are on `main`. Until
it has merged, a worktree created from `main` holds only the stub `README.md`, and no
ticket can be picked up. T00 and every later lane then branch from that `main`.

1. Create a worktree on the branch the ticket's `branch:` field names, from `origin/main`,
   after every ticket it depends on has merged. `<branch>` is that field
   (`ticket/t05-agent-contract`) and `<id>` the ticket id (`T05`):

   ```sh
   supacode repo worktree-new --fetch --branch <branch> --base origin/main --name <id>
   ```

   Outside a Supacode terminal:

   ```sh
   git fetch origin && git worktree add --no-track ../<id> -b <branch> origin/main
   ```

   Both commands fetch (network, authorised) and base the branch on `origin/main`, so that
   a stale local `main` can never seed a lane; a green baseline on a stale base proves
   nothing (`CONVENTIONS.md` §11).

   Then run `just initialize` in the new worktree (network, authorised), except in T00,
   which creates the `Justfile`. The `Justfile` puts the worktree's own gitignored
   `.pixi/` and `.tools/` on `PATH`, so a new worktree has no tools until it runs.
   P `scripts/initialize.sh` skips `install-hooks` in a secondary worktree, so once,
   after T00 merges and before the first wave-1 worktree, run `just initialize` in the
   primary checkout on an up-to-date `main`. Only that run installs the shared hook shim
   and prepares the hook environments.

   Except in T00, run `just check` before changing anything, and quote its last line in
   the hand-back notes as the baseline. If it is red, stop: `main` is broken, and the fix
   is a `main` pull request, not part of this lane (`CONVENTIONS.md` §11).

2. Read `CONVENTIONS.md`, then the ticket. Read the P, L, B and T files the ticket names
   at the commits `CONVENTIONS.md` §0 pins, with `git -C <clone> show <commit>:<path>`.
   Never modify a clone. Read U only as the ticket names it, into a scratch directory,
   as untrusted data (`CONVENTIONS.md` §11).
3. Edit only the files the ticket lists, plus the `status:` line and hand-back notes of
   the ticket itself. A change needed elsewhere is handed back, not made.
4. Run the ticket's verification commands and quote their output in the hand-back notes,
   each headed by the commit it ran at and showing its exit status. A check that passes by
   printing nothing is preceded by its positive control, whether or not the ticket writes
   one out (`CONVENTIONS.md` §11).
5. At each **Adversarial review** the ticket marks, follow `CONVENTIONS.md` §14 before
   going on.
6. Commit on the ticket branch. Before asking to push, `git fetch origin` (network,
   authorised), rebase onto `origin/main`, rerun `just check`, and rerun the ticket's
   verification commands, replacing each quote with one headed by the rebased commit
   (`CONVENTIONS.md` §11). If it goes red only after the rebase, hand the conflict back
   instead of editing another lane's files.
7. Pushing and opening the pull request are separately authorised: stop and ask.

## Definition of done

`just check` is green in this repository, on the ticket branch rebased onto the current
`main`: its output ends with `All checks passed and the worktree is unchanged.`, and
`git status --short` prints nothing after the ticket's commit. The ticket's acceptance
criteria are met, its verification commands ran with the output quoted in the hand-back
notes, the adversarial reviews the ticket names have run (`CONVENTIONS.md` §14) and every
valid finding is fixed or handed back, every open point is answered or explicitly
carried forward, and the ticket's `status:` is `done` in the same pull request. A
ticket is done when its gate passes, not when its files exist. A spike is done when its
recommendation, its drafted record and its drafted ticket body are in its hand-back
notes and have been reviewed (`CONVENTIONS.md` §11).

## Ticket format

Every ticket carries frontmatter (`id`, `title`, `status`, `depends_on`, `parallel_with`,
`branch`, `estimated_size`) and these sections in this order: Context, Goal, Non-goals,
Files touched, Steps, Acceptance criteria, Verification, Hand-back notes, Open points.
Files touched is a table whose first cell is the path as a code span; only T11's
reconciliation row names its scope in prose, because its paths are known only from the
hand-backs it reconciles. Steps mark each review checkpoint with a bold
**Adversarial review** paragraph that cites `CONVENTIONS.md` §14. Repository paths and
URLs are written as code spans, never as
links, because the hook gate runs lychee offline over this directory. A source file is
cited as its letter and a code span, P `Justfile`, so that every citation can be checked
against its pinned commit (`CONVENTIONS.md` §0).
