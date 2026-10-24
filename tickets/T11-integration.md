---
id: T11
title: "Integration: the first green `just check` from a fresh clone and in CI, protection read back"
status: open
depends_on: [T01, T02, T03, T05, T07, S01]
parallel_with: []
branch: ticket/t11-integration
estimated_size: M
---

# T11: Integration: the first green `just check` from a fresh clone and in CI, protection read back

## Context

Six lanes have run, five of them landing code on `main` and one, S01, landing only its
hand-back notes. Each lane was green on its own branch, and several will have handed back
follow-ups to frozen files (`CONVENTIONS.md` §11): a recipe flag T02 or T03 found wrong, a
`.gitignore` line, a manifest entry, a sentence another lane's page needed. This ticket is
where the pieces are proved to fit: the follow-ups reconciled on `main`, grouped by file
into small pull requests; every sentence written to the design checked against what
landed; the whole gate run from a fresh clone of the remote and in CI; branch protection
read back, failing closed; and the `CONVENTIONS.md` §12 claims wave 0 and wave 1 owned
given their recorded outcomes. The frozen list lifts only when this ticket is done
(`CONVENTIONS.md` §11, "Wave 2 shares files by rebasing"), so T13 and T15 wait for it.

P `tickets/T11-integration.md` at `bf51e0d` is the procedure; its steps carry over with
this repository's names, minus the effects and specification items, plus the Python gates
and the offline `wheel-smoke`. P `tickets/T01-github-and-ci.md`'s hand-back notes ("State
before", "State after") show the exact `gh api` read-back shapes and the one 404 message
that means absence on a public repository; here T01's own hand-back notes hold the 403 a
deferral rests on. This repository is private (`CONVENTIONS.md` §1 fact 6), so T01 may
have deferred branch protection rather than applied it; step 4 handles both outcomes.

## Goal

`main` on `BiscuitBin/alliumpy`, cloned fresh from GitHub into a shell with no pixi
activation, passes `just initialize` then `just check`, and `just check` passes there
again under `CONVENTIONS.md` §11's network denial, with `just wheel-smoke` repeated on an
empty `UV_CACHE_DIR`; CI on `main` is green with every job of `CONVENTIONS.md` §10
(`rust`, `python`, `wheel-smoke-py311`, `coverage`, `deny`, `documents`) feeding the
aggregate `check`; branch protection requires `check`, or its deferral is recorded with
the reason T01 gave; every `CONVENTIONS.md` §12 claim owned by T00 to T07 and S01 (claims
1, 3, 6, 8, 9, 10, 11, 13 to 17 and 19 to 22, and S01's part of claim 12: the
`cargo install allium-cli@3.6.1 --locked` build, the `--version` equality and whether
`allium-parser` exposes the language-version list) has a recorded outcome in §12's table;
every check a wave-0 or wave-1 hand-back says it did not run has a recorded disposition,
and each one left open has an owning ticket; and the handbook says what landed. Claims 2,
4, 5, 7 and 18, and T13's part of claim 12, belong to T13 and T14; T17 records them.

## Non-goals

- No new feature, recipe, page or dependency. A gap found here is a fix to what a lane
  delivered, or a new ticket.
- No wave-2 work: no CLI command, no parity recipe, no release workflow.
- No edit to `tickets/CONVENTIONS.md` outside §12's table. A design change a lane's
  evidence forces is named in the hand-back notes and goes through its own `main` pull
  request with the maintainer's approval, never folded into the outcomes commit.
- No change to repository settings. If protection was deferred, the decision stays the
  maintainer's (`CONVENTIONS.md` §10).

## Files touched

| Path | Class | Content |
| --- | --- | --- |
| `tickets/CONVENTIONS.md` | correction | §12 outcomes only, through a `main` pull request |
| `tickets/T18-verification-gaps.md` | new, only if an item stays open | one item per open row of step 5's second table |
| `tickets/README.md` | correction | T18's index row and graph entry, only if T18 is written |
| `<path>` (any lane file a hand-back names or step 6 surfaces) | correction | the reconciled sentence or line, one `main` pull request per file touched (step 2) |
| `tickets/T11-integration.md` | ticket | `status:` and hand-back notes |

## Steps

1. Create the worktree after T01, T02, T03, T05 and T07 have merged and S01's hand-back
   notes are on `main`. Run `just check` on the untouched worktree and quote its last
   line as the baseline (`CONVENTIONS.md` §11).
2. **Reconcile.** Read every lane's hand-back notes, S01's included. For each item handed
   back or written to the design, find it on `main` and make it true; list each with its
   resolution and the file it touches. Group the items by file: a follow-up to a frozen
   file (the `Justfile`, `pyproject.toml`, `.gitignore`, `docs/manifest.yml`, the hook
   configurations) is one `main` pull request per file, rebased on the last, with
   `just check` green on each. Also list every check a hand-back says it did not run,
   skipped, or ran only as a dry run (`just -n`, a documentation read, a scratch copy);
   step 5 disposes of them.

   **Adversarial review** (`CONVENTIONS.md` §14): the reconciliation list, with every
   lane's hand-back notes beside it in the brief instead of a diff, before the first
   follow-up pull request is asked for. Ask: which item handed back, or sentence written
   to the design, is missing from the list; which resolution is claimed but not on
   `main`; which two follow-ups edit the same line and must land in one pull request.

   **Authorisation required: push and open each follow-up pull request.** Stop and ask
   once with the whole list; each pull request is still its own push. Each follow-up
   lives on its own branch `fixup/t11-<file-slug>` created from `origin/main` after a
   fetch, in a sibling worktree as `README.md` "How to pick up a ticket" step 1
   describes, with `just initialize` there (network, authorised); the maintainer merges;
   after each merge, `git fetch origin` and rebase the ticket branch, so steps 3 to 7 run
   against the reconciled `main`.
3. **Fresh clone from the remote.** In a shell with no pixi activation and no
   `VIRTUAL_ENV` or `CONDA_PREFIX` set (`CONVENTIONS.md` §12 claim 9), shown by
   `env | rg '^PATH='; echo "exit $?"` (exit 0, the positive control) and
   `env | rg '^(PIXI_IN_SHELL|PIXI_PROJECT_|CONDA_PREFIX|VIRTUAL_ENV)='; echo "exit $?"`
   (prints nothing, exit 1), both quoted,
   `gh repo clone BiscuitBin/alliumpy ai_tmp/fresh` (network, authorised; `gh` carries
   the credential the private repository needs, `CONVENTIONS.md` §2), then
   `just initialize` (network, authorised) and `just check` there. Quote the whole
   `check` output, all twenty-two gates and `check-clean`. Then, in the same clone, run
   `just check` again under `CONVENTIONS.md` §11's network denial, as P's step 3 did, then
   `just wheel-smoke` alone under the same denial, and quote each with both
   negative-control exit codes. `wheel-smoke` is the recipe most likely to reach for the
   network by accident (`CONVENTIONS.md` §13); a cached `uv` download is not a pass, so
   the clone's `UV_CACHE_DIR` is set to an empty directory for that run. If a gate needs
   the network, that is a finding to hand back; do not edit a frozen file to make it
   pass.
4. **CI on `main`, and branch protection.** Dispatch `ci.yml` and `audit.yml` on `main`
   (network, authorised; metered minutes, `CONVENTIONS.md` §13) with
   `gh workflow run ci.yml --repo BiscuitBin/alliumpy --ref main` and the same for
   `audit.yml`, wait with `gh run watch <id> --repo BiscuitBin/alliumpy`, and read both
   runs with
   `gh run view <id> --repo BiscuitBin/alliumpy --json jobs --jq '.jobs[] | [.name, .status, .conclusion]'`
   and `rg -n -A1 'needs:' .github/workflows/ci.yml`: every job of `CONVENTIONS.md` §10
   present and green, `check` green, `audit` ran and is not required. Then read protection
   back, failing closed: first `gh api repos/BiscuitBin/alliumpy --jq .permissions.admin`
   must print `true`, because GitHub answers 404 to a token that may not read protection;
   then
   `gh api -i repos/BiscuitBin/alliumpy/branches/main/protection > ai_tmp/protection-now.raw 2> ai_tmp/protection-err.txt; echo "exit $?"`,
   quoting the exit (gh's, not `jq`'s), the first line of `ai_tmp/protection-now.raw` (the
   HTTP status) and `ai_tmp/protection-err.txt`; only on exit 0,
   `sed '1,/^\r\{0,1\}$/d' ai_tmp/protection-now.raw | jq -S . > ai_tmp/protection-now.json`.
   Exactly three outcomes are read, and nothing else is:
   - HTTP 200: protection exists. `gh api repos/BiscuitBin/alliumpy/branches/main/protection/required_status_checks --jq '[.checks[] | {context, app_id}]'`
     must print one entry, `check`, with the GitHub Actions `app_id` T01 recorded.
     `.contexts` is deprecated and is not the evidence. Paste the body T01's hand-back
     notes quote after its apply into `ai_tmp/protection-t01.json` and run
     `diff ai_tmp/protection-t01.json ai_tmp/protection-now.json; echo "exit $?"`; if T01
     quoted only a compacted summary, compare it field by field against
     `ai_tmp/protection-now.json` and record the comparison. A field whose live value
     differs is a finding, and a field T01 did not quote is listed as unverified, not as
     unchanged.
   - The HTTP status and message T01's hand-back notes quoted when they recorded
     protection as deferred because the repository is private on the free plan
     (`CONVENTIONS.md` §1 fact 6, §10; on such a repository an HTTP 403 whose message
     names the upgrade or the visibility, T01 step 2), reproduced exactly by this read:
     record the deferral with T01's reason, confirm with
     `gh pr checks <number> --repo BiscuitBin/alliumpy` on the most recently merged
     pull request (a step-2 follow-up if one landed, otherwise the last wave-1 lane's)
     that `check` still ran, and carry the deferral into step 5's second table
     as an open row owned by the maintainer. This is T01's recorded decision read back,
     not a reading of absence: a 404 `Branch not protected` is read as deferred only if
     that is the status and message T01 quoted.
   - Anything else (a status or message that differs from the one T01 quoted, a 403 or
     404 when T01 applied protection, a network error, an empty body): stop the step and
     hand it back. It is never read as "absent" or as a deferral.

   **Adversarial review** (`CONVENTIONS.md` §14): the protection read-back and the CI
   runs, before step 5 builds the claims table on them. Ask: whether a 403 or a 404 from
   a token without admin could have been read as absence; whether the `app_id` is GitHub
   Actions' and not another app's; whether every §10 job is in `check`'s `needs` and ran
   on the dispatched run rather than being skipped; whether the deferral, if any, is
   T01's recorded decision and not this ticket's inference.
5. **The claims table.** One row per `CONVENTIONS.md` §12 claim 1, 3, 6, 8, 9, 10, 11, 13
   to 17 and 19 to 22 with its outcome, the ticket that checked it and where the evidence
   is quoted; claim 12 is recorded as partial from S01's hand-back notes, with T13's part
   left open for T17; claims 2, 4, 5, 7 and 18 stay open, marked as T17's. A claim whose
   owner's hand-back shows no evidence is marked open, not inferred from a green gate.
   Then a second table, "Checks the hand-backs did not run", from step 2's list: Source
   ticket, Item, Disposition. A disposition is Closed (cite where the evidence is quoted)
   or Open. A green `just check` or CI run is cited only for an item it actually executes.
   Likely rows, as examples and not a checklist: the primary checkout's hook shim refusing
   a bad commit; `snapshots-review` and `snapshots-accept`, which have nothing to act on
   before the first snapshot; `just py-develop` from a shell with no pixi activation
   (claim 9) if T00 ran it only from an activated one; initialization with no cache
   reused; `audit.yml` on `main`; the deferred protection of step 4. Open rows that no
   existing ticket owns go into one new ticket, `tickets/T18-verification-gaps.md` (T18,
   the first id after T17, so that the numbering stays comparable with pachinko's, whose
   gaps `README.md` explains; confirm on `main` that it is unused in the README index), in
   this directory's ticket format, with one item per row stating exactly what evidence
   closes it, and recording it as open rather than inferring success from an unrelated
   green gate. It depends on T11 and is off the critical path. Carry the claims table into
   `CONVENTIONS.md` §12 by adding two columns to its existing table, `Outcome` (`holds`,
   `fails`, `deferred`, `partial` or `open (T17)`) and `Evidence` (the ticket id and the
   hand-back section the quote is in), one line per row and no other §12 edit, and add T18
   to the README index and graph, through one `main` pull request, after the review below.

   **Adversarial review** (`CONVENTIONS.md` §14): the claims table, before its `main`
   pull request is asked for. Ask: which outcome is not backed by evidence quoted in a
   ticket's hand-back notes; which outcome claims more than its quoted evidence shows
   (an offline run with no negative control, a `wheel-smoke` that passed on a warm
   cache); which check a hand-back did not run is missing from the second table; which
   disposition cites a gate that does not run it.

   **Authorisation required: push and open the §12 pull request.** Stop and ask. It
   lives on `fixup/t11-conventions-s12` from `origin/main`, as step 2's follow-ups do;
   after the maintainer merges, fetch and rebase the ticket branch.
6. **Cleanliness.** `rg -n -i '\bstubs?\b|lands with T|arrives? with T|\bTODO\b'` over
   `docs/`, `AGENTS.md`, `.agents/`, `crates/` and `scripts/` prints only sentences that
   name a wave-2 ticket (T12, T13, T14, T15, T17) or decision 0014, which stays a stub
   until T13 (`CONVENTIONS.md` §8), or that refer to the typing stub `_alliumpy.pyi`,
   `py-stubtest` or the stubtest allowlist (`CONVENTIONS.md` §3, §9);
   `rg -n -i --hidden --glob '!.git/**' 'pachinko|pawdoku|sudoku|wasm|docs/specs|install-allium'`
   outside `tickets/` (dotfiles and `.github/` included) prints only carried-from
   sentences, `AGENTS.md`'s Provenance sentences, the `docs/specs/` sentence
   `CONVENTIONS.md` §1 fact 1 requires, and the sentences of
   `docs/decisions/0013-no-spec-gate-no-allium-skills.md` that say what this repository
   does not carry (`CONVENTIONS.md` §1 decision 5). A surviving line outside this set is a
   finding: it joins step 2's reconciliation list as a follow-up to its owning lane's
   file, through that file's `main` pull request, never an edit on this branch.
7. Delete `ai_tmp/fresh`, `just check`, the final adversarial review, `just check` again
   if fixes landed, set `status: done`, commit.

   **Adversarial review** (`CONVENTIONS.md` §14): the lane's diff and the hand-back notes.
   Ask: which acceptance criterion is asserted but not shown; which quoted output is
   headed by a commit that a later follow-up pull request made stale.

## Acceptance criteria

- The fresh-clone `just check` is green and quoted in full, from a shell with no pixi
  activation.
- `just check` and then `just wheel-smoke` are green in the fresh clone under
  `CONVENTIONS.md` §11's network denial, with both negative-control probes failing and
  `UV_CACHE_DIR` on an empty directory.
- CI on `main` is green with every `CONVENTIONS.md` §10 job present in `check`'s
  `needs`; `audit` ran and is not required.
- Branch protection requires `check`, read back from `.checks` with the GitHub Actions
  `app_id`, after an admin check; or its deferral is recorded with T01's reason, the
  read returns the HTTP status and message T01's hand-back quoted, and `check` is shown
  running on a merged pull request. No other response was read as absence or as
  deferral.
- Every follow-up a wave-0 or wave-1 hand-back named is on `main`, each through the
  per-file follow-up pull request of step 2, listed with its resolution and pull request
  number.
- Every `CONVENTIONS.md` §12 claim 1, 3, 6, 8, 9, 10, 11, 13 to 17 and 19 to 22 has an
  outcome in §12's table on `main`, and claim 12 a partial one from S01's hand-back notes;
  claims 2, 4, 5, 7 and 18, and T13's part of claim 12, are marked open for T17.
- Every check a T00 to T07 or S01 hand-back did not run has a row in step 5's second
  table; no green gate is cited for an item it does not run; open rows without an owner
  are items in `tickets/T18-verification-gaps.md`, which is in the README index.
- Step 6's searches print only what Step 6 permits: sentences naming a wave-2 ticket or
  decision 0014, sentences about the typing stub `_alliumpy.pyi`, `py-stubtest` or the
  stubtest allowlist, the carried-from, Provenance and `docs/specs/` sentences, and
  decision 0013's not-carried sentences; each surviving line is quoted in the hand-back
  notes.
- `just check` is green on the ticket branch rebased onto `main`.
- The adversarial reviews in Steps ran (`CONVENTIONS.md` §14), and every valid finding is
  fixed or handed back.

## Verification

```sh
just check
cd ai_tmp/fresh  # after just initialize there; macOS; on Linux, unshare -rn in place of sandbox-exec (CONVENTIONS.md §11)
env | rg '^PATH='; echo "exit $?"
env | rg '^(PIXI_IN_SHELL|PIXI_PROJECT_|CONDA_PREFIX|VIRTUAL_ENV)='; echo "exit $?"
deny='(version 1)(allow default)(deny network*)'
sandbox-exec -p "$deny" curl -fsS --max-time 10 https://static.rust-lang.org; echo "exit $?"
sandbox-exec -p "$deny" curl --noproxy '*' -fsS --max-time 10 https://1.1.1.1; echo "exit $?"
sandbox-exec -p "$deny" just check; echo "exit $?"
UV_CACHE_DIR=$(mktemp -d) sandbox-exec -p "$deny" just wheel-smoke; echo "exit $?"
cd ../..  # back to the worktree
gh workflow run ci.yml --repo BiscuitBin/alliumpy --ref main; echo "exit $?"
gh workflow run audit.yml --repo BiscuitBin/alliumpy --ref main; echo "exit $?"
gh run list --repo BiscuitBin/alliumpy --workflow ci.yml --branch main --limit 1 --json databaseId,headSha,conclusion,url; echo "exit $?"
gh run list --repo BiscuitBin/alliumpy --workflow audit.yml --branch main --limit 1 --json databaseId,headSha,conclusion,url; echo "exit $?"
gh run view <ci-run-id> --repo BiscuitBin/alliumpy --json jobs --jq '.jobs[] | [.name, .status, .conclusion]'; echo "exit $?"
gh run view <audit-run-id> --repo BiscuitBin/alliumpy --json jobs --jq '.jobs[] | [.name, .status, .conclusion]'; echo "exit $?"
rg -n -A1 'needs:' .github/workflows/ci.yml; echo "exit $?"
gh api repos/BiscuitBin/alliumpy --jq .permissions.admin; echo "exit $?"
gh api -i repos/BiscuitBin/alliumpy/branches/main/protection > ai_tmp/protection-now.raw 2> ai_tmp/protection-err.txt; echo "exit $?"
sed '1,/^\r\{0,1\}$/d' ai_tmp/protection-now.raw | jq -S . > ai_tmp/protection-now.json   # only on exit 0
gh api repos/BiscuitBin/alliumpy/branches/main/protection/required_status_checks --jq '[.checks[] | {context, app_id}]'; echo "exit $?"
diff ai_tmp/protection-t01.json ai_tmp/protection-now.json; echo "exit $?"  # HTTP 200 path only
gh pr checks <number> --repo BiscuitBin/alliumpy; echo "exit $?"  # deferral path: the most recently merged pull request
rg -n -i '\bstubs?\b|lands with T|arrives? with T|\bTODO\b' docs AGENTS.md .agents crates scripts; echo "exit $?"
rg -n -i --hidden --glob '!.git/**' --glob '!tickets/**' 'pachinko|pawdoku|sudoku|wasm|docs/specs|install-allium' .; echo "exit $?"
git status --short; echo "exit $?"
```

The protection read's HTTP status is the first line of `ai_tmp/protection-now.raw` and its
message is `ai_tmp/protection-err.txt`; both are quoted with the exit status, and a
non-zero exit on the protection read is quoted as such and never summarised as "no
protection", and is recorded as deferred only when its status and message match the ones
T01's hand-back quoted.

## Hand-back notes

To be written by the executing agent: the baseline; the reconciliation list with each
follow-up's pull request number and merge commit; the fresh-clone output; the offline
`check` and `wheel-smoke` output and both probe exits; the run URLs and the commits they
tested; the protection read-back with its HTTP status, its diff against T01's or the
recorded deferral; the claims table as carried into `CONVENTIONS.md` §12 and its pull
request number; the table of checks the hand-backs did not run and T18's id if one was
opened; and the review record for each of the four checkpoints (`CONVENTIONS.md` §14).

## Open points

- If protection was deferred, whether the maintainer wants T18 to carry the item or a
  standing note in `docs/operations/maintenance.md` instead. Default: T18.
