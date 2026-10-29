---
id: T18
title: "Verification gaps: the checks the wave-0 and wave-1 hand-backs did not run"
status: open
depends_on: [T11]
parallel_with: [T12, T13, T14, T15, T17]
branch: ticket/t18-verification-gaps
estimated_size: M
---

# T18: Verification gaps: the checks the wave-0 and wave-1 hand-backs did not run

## Context

T11 read every wave-0 and wave-1 hand-back (T00, T01, T02, T03, T05, T07 and S01) and
listed the checks they did not run in its second table, "Checks the hand-backs did not
run" (T11's hand-back notes). Rows that T11 closed, or that an existing ticket owns, are
not here. Each item below is a row that no existing ticket owns: an enforcement gap in a
frozen file, a recipe nobody exercised, or a `CONVENTIONS.md` §12 claim that T11
recorded as `partial` because one half was never shown. None is known to be broken;
each is unproven. A green `just check` or CI run closes an item only if it runs the
thing the item names (`CONVENTIONS.md` §12, §14).

This ticket is off the critical path: no wave-2 ticket waits for it, and it waits only
for T11. Wave-2 rules apply (`CONVENTIONS.md` §11): the frozen list has lifted, every
shared file is edited on its own lines, and this ticket merges rebased on whatever
wave-2 ticket merged before it.

## Goal

Every item below is closed with the evidence its row names, or is recorded as a
maintainer ruling with its reason. No item is closed by inference from an unrelated
green gate.

## Non-goals

- Anything T12 to T17 owns: the sdist assertions and the release matrix (T14), the
  vendored CLI and parity (T13), `SECURITY.md` (T12), and claims 2, 4, 5, 7 and 18 and
  T13's and T14's parts of claims 1, 12 and 19 (T17).
- Re-litigating T01's design points beyond what item 10 asks: a point the maintainer
  rules out stays out.

## Files touched

A path is edited only on the route its item takes; a route that a maintainer ruling
closes edits nothing. A route that needs a path not listed here stops and is handed back
(`CONVENTIONS.md` §14, "Scope guard").

| Path | Class | Content |
| --- | --- | --- |
| `scripts/version_check.py` | shared, own lines | item 1: each member crate's inherited or explicit version |
| `Justfile` | shared, own lines | item 2: the `check-toolchain` recipe only |
| `docs/reference/commands.md` | shared, own lines | item 2: the `check-toolchain` row |
| `docs/reference/quality-gates.md` | shared, own lines | item 2: the `check-toolchain` row |
| `.github/workflows/ci.yml` | shared, own lines | item 10: only the points the maintainer accepts |
| `.github/workflows/audit.yml` | shared, own lines | item 10: only the points the maintainer accepts |
| `.github/actions/setup/action.yml` | shared, own lines | item 10: only the points the maintainer accepts |
| `crates/alliumpy/pyproject.toml` | shared, own lines | item 11: a `[tool.maturin]` exclusion, only if bytecode ships and the maintainer wants it out |
| `tickets/CONVENTIONS.md` | shared, own lines | item 12: one sentence in §14, only after the maintainer approves its text |
| `tickets/README.md` | shared, own lines | this ticket's status cell; item 12's sentence in "Ticket format" instead of §14, if the maintainer approves that route |
| `tickets/T18-verification-gaps.md` | ticket | `status:` and hand-back notes |

## Steps

Each item names its source (ticket and lines, as T11 cited them), what is unproven, and
the evidence that closes it. Run `just check` on the untouched worktree first and quote
its last line.

1. **Member-crate versions (T05:434-438; T07:518-521).** `scripts/version_check.py`
   reads the workspace version only, so invariant 9 is not proved for each crate
   manifest. Closed by a checker that reads each member's inherited or explicit
   version, with a scratch-copy control: an explicit wrong `version` in one member
   makes `just version-check` exit non-zero, quoted, then restored.
2. **`check-toolchain` against the pin (T07:518-521).** The recipe checks that `cargo`
   is rustup's proxy, not that the selected toolchain equals `rust-toolchain.toml`.
   Closed by a recipe change plus a control: `RUSTUP_TOOLCHAIN=<another installed
   version> just check-toolchain` exits non-zero, quoted.
3. **The primary checkout's hook shim (T00, not stated).** No hand-back shows the
   installed hook refusing a commit. Closed by a commit attempt with a deliberate
   violation in the primary checkout (hooks are never installed from a secondary
   worktree, `AGENTS.md`), quoting the refusal and its exit, then the clean state.
4. **`snapshots-review` and `snapshots-accept` (T00, not stated).** Never run: there
   was no snapshot to act on, and the workspace has no `insta` dependency (T02:345-347:
   the first ticket that takes a real snapshot adds it). A run with nothing pending
   proves nothing: `snapshots-accept` exits 0 with nothing to accept, and its
   `--unreferenced delete` removes an orphan `.snap` (`Justfile`). Closed in a scratch
   copy that adds `insta` as a core dev-dependency and one test whose assertion
   produces a pending `.snap.new`, all restored afterwards and never committed
   (invariant 8; resolving `insta` into the scratch `Cargo.lock` runs `just lock`, a
   network recipe the maintainer authorises first). Each recipe gets its own fresh
   pending snapshot. For `snapshots-accept`: exit 0, the `.snap.new` gone and the
   accepted `.snap` holding the expected content, quoted. For `snapshots-review`, which
   needs a terminal: its prompt naming that snapshot, the accept chosen there and its
   exit, quoted. Then `git status --short` empty. Or by a maintainer ruling that the
   first ticket to take a real snapshot runs both and quotes the same evidence; no
   ticket in this directory does yet.
5. **Claim 8, `PYO3_BUILD_EXTENSION_MODULE` (T00, T02).** No hand-back shows maturin
   setting it during `py-develop`. Closed by `py-develop` output at a verbosity that
   prints the cargo invocation and shows the variable set, quoted with its commit.
6. **Claim 9, the installer (T00:507, T00:538; T11 step 3).** T11 showed `maturin
   develop` finding the pixi environment through `CONDA_PREFIX` from an unactivated
   shell, but no output names the installer or shows it is `uv 0.13.5`. Closed by
   output that names the installer and its version during `py-develop`.
7. **Initialization with no global cache (T00:620).** Every `just initialize` so far
   reused the cargo registry, rustup, pixi or uv caches. Closed by a run with each of
   those cache locations pointed at an empty directory, quoting `just initialize` and
   then `just check`, or by a maintainer ruling that CI's cold runners are the proof
   (cite the run).
8. **Claim 10, the full run (T01:681-685; `CONVENTIONS.md` §12).** T01's full CI run hit
   `main`'s pixi cache, so B was not fetched there; T11's dispatch would hit it too.
   Closed by a full `ci.yml` run on `main` whose setup-pixi cache misses and fetches B
   with no credential, quoting the cache-miss line and the fetch.
9. **Claim 11, the Pages half and the private skip (T01:416-418, 505-507, 759-760).**
   The Pages read gave 404, not a plan message, and the conditional deploy never ran on
   a private repository. The repository has been public since 2026-10-24, so the skip
   cannot be run as built. The two halves close separately; closing one leaves the
   other open.
   - Pages availability on the free organisation plan: closed by a read on a private
     repository whose answer shows availability either way (a plan message or a Pages
     object, not a bare 404), quoted with its exit, or by a maintainer ruling with
     its date that it is moot while the repository is public. A skipped deploy does
     not close it.
   - The private skip: closed by a `pages.yml` run on `refs/heads/main` of a private
     repository, quoting the event's `repository.private` as `true`, the build job
     green and the deploy job `skipped`. A run on another branch does not count: the
     `if:` (`.github/workflows/pages.yml`) also requires `main`, so it would skip for
     the wrong reason. Or by a maintainer ruling with its date that it is moot while
     the repository is public.
10. **T01's seven review points (T01:782-800).** The full setup in `audit`;
    `check-toolchain` only in `rust`; the setup action's "no step reaches the network"
    comment against `audit`'s RustSec fetch; `py-develop` twice in `python`;
    `snapshots-check` and nextest run twice; seven rust-cache keys; no
    `overwrite: true` on the uploads (unverified). Each point closes by a maintainer
    ruling with its reason, or by a change and the run that executes it. `audit.yml` is
    its own workflow and is not in `ci.yml`'s `check` `needs`, so the two `audit`
    points (the full setup, the RustSec fetch) close only by a green `audit.yml` run
    after the change, quoted. The `overwrite: true` point closes only by rerunning
    an uploading job in the same `ci.yml` run after its first attempt uploaded the
    artefact, quoting the attempt numbers and the rerun's upload step; a fresh dispatch
    never reaches the conflict. The other four close by a green dispatched `ci.yml` run
    after the change, quoting the job whose behaviour changed.
11. **Python bytecode in the wheel (T00:558-560).** Closed by a wheel listing
    (`python -m zipfile -l`) that shows whether `__pycache__` or `.pyc` entries ship,
    and a maintainer ruling or a manifest change if they do.
12. **The verification-template rule (T05:439-443).** T05's B2: a filter can return its
    expected exit after the producer failed. Closed by a sentence in `CONVENTIONS.md`
    §14 or in `tickets/README.md`, "Ticket format", that splits producers from filters,
    checks each exit and keeps a nonempty positive control. That is a change to the
    rules every ticket obeys: the maintainer approves the sentence's text and its place
    before it is written, and this ticket does not grant that approval itself. Quote
    the approval with its date, then the commit that adds the sentence.
13. `just check`, the final adversarial review, `just check` again if fixes landed, then
    commit. **Authorisation required: push and open a pull request.** A dispatched or
    rerun CI run that items 8 and 10 name runs after the merge, each separately
    authorised, and its evidence follows in one evidence commit, reviewed as below
    before its own push.

    **Adversarial review** (`CONVENTIONS.md` §14): the lane's diff and every item's
    closing evidence or ruling, before the push. Ask: which item is closed by a gate or
    run that does not execute the thing it names; which item 9 half is closed by the
    other half's evidence, or by a skip on a branch other than `main`; whether item 1's
    checker and item 2's recipe fail on their scratch controls and pass once restored;
    whether item 4's accept ran against a referenced pending snapshot and not an empty
    set; whether item 10's artefact point rests on a same-run rerun and its `audit`
    points on an `audit.yml` run; whether each ruling records its reason and date;
    whether every scratch edit, including item 4's `insta` dependency, was restored.

## Acceptance criteria

- Each of the twelve items is closed with the evidence its step names, quoted with its
  commit, or carries a maintainer ruling with its reason.
- No item is closed by citing a gate that does not run it.
- `just check` ends with `All checks passed and the worktree is unchanged.` and
  `git status --short` is empty.

## Verification

```sh
just check
just version-check; echo "exit $?"     # item 1, before and after the scratch control
just check-toolchain; echo "exit $?"   # item 2, before and after the scratch control
git status --short; echo "exit $?"
```

The other items' commands depend on the route each takes; quote each with its exit.

## Hand-back notes

To be written by the executing agent: the baseline, then one entry per item with its
evidence or ruling, and the review record (`CONVENTIONS.md` §14).

## Open points

- Items 3, 4, 7, 9, 10 and 12 may close by a maintainer ruling instead of a run; the
  maintainer says which before the work starts.
- Item 12 changes the rules every ticket obeys. Whether the sentence goes in
  `CONVENTIONS.md` §14 or in `tickets/README.md`, "Ticket format", and its wording, are
  the maintainer's decision; T11 did not make it, and no line is written before it.
