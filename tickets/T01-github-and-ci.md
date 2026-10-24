---
id: T01
title: "GitHub repository and CI: settings, branch protection, workflows, the abi3 floor"
status: open
depends_on: [T00]
parallel_with: [T02, T03, T05, T07, S01]
branch: ticket/t01-github-and-ci
estimated_size: M
---

# T01: GitHub repository and CI: settings, branch protection, workflows, the abi3 floor

## Context

`BiscuitBin/alliumpy` already exists: **private**, on the free organisation plan, with
`origin` set and one `first commit` on `main`. Nothing is created and there is no first
push to make here; T00 reaches `main` through its own pull request. What is missing is
everything a file cannot carry: branch protection with `check` required, merge hygiene,
and the Pages source. Steps 1 to 7 find out which of those the plan allows and set the
ones it does.

The visibility is the difference from P. Branch protection and GitHub Pages are
public-repository features on the free organisation plan (`CONVENTIONS.md` §1 fact 6);
GitHub is expected to answer a protection read on such a repository with an HTTP 403
whose message names the upgrade, not a 404 (`CONVENTIONS.md` §12 claim 22; step 2
records what it actually returned). T `scripts/bootstrap_repo.sh` treats any non-404
error as a failure and stops (its `gh_read` function), so on a private free-plan
repository the script cannot run to completion and must not be patched. This ticket
reads the plan and the visibility first, hands the maintainer the choice as an
authorisation stop, and records what was deferred as deferred, never as done.

P `tickets/T01-github-and-ci.md` is the procedure: dry run, apply, read back, each apply
separately authorised; its hand-back notes record what P's live runs proved about the
script's announcements, the `app_id` GitHub binds to a required check, the action pins
and the caches. Read its Steps and its hand-back notes in full. T
`scripts/bootstrap_repo.sh` does the settings work through `gh api`; read its usage block
its flags (`--checks`, `--no-pages`, `--hygiene`) and its six numbered steps before
running it. This repository passes exactly `--checks check` (`CONVENTIONS.md` §10).

T00 left a one-job `ci.yml` named `check` running `just check`. Steps 8 to 13 write the
real workflows: P's at `bf51e0d`, with the deltas `CONVENTIONS.md` §10 names, and two
new jobs that are this repository's own: `python`, which runs the six Python gates and
uploads the wheel, and `wheel-smoke-py311`, which installs that wheel on Python 3.11, the
`abi3-py311` floor that no local run ever exercises because pixi's interpreter is 3.14
(`CONVENTIONS.md` §9, "The release matrix versus the gate").

## Goal

The maintainer has decided, on evidence this ticket read back, whether `main` is
protected now, after a visibility or plan change, or not yet; whatever was applied
(protection with `check` the one required check, the merge-hygiene settings, the Pages
source) was authorised before it was made and read back afterwards, and whatever was
not is recorded as deferred with the reason. A pull request runs `rust`, `python`,
`wheel-smoke-py311`, `coverage`, `deny`, `documents` and the aggregate `check`, all
green; `audit.yml` runs and is not required; `pages.yml` builds on a push to `main` and
deploys only when the repository is public; every remote `uses:` is pinned to a full SHA
with a version comment read on the day; and every gate job that runs recipes (all but
`wheel-smoke-py311`) ends with `just check-clean`.

## Non-goals

- No repository file changes beyond the setup action, the workflows and this ticket's
  `status:` and hand-back notes.
- No required check but `check`, and no change to its name (`CONVENTIONS.md` §10).
- No secret and no GitHub App. `GITHUB_TOKEN` is the run's own.
- No change to `BiscuitBin`'s organisation settings, plan or the repository's
  visibility by this ticket. Each is the maintainer's to make; this ticket asks and
  records the answer.
- No edit to T's script. A flag it lacks, or a case it cannot handle, is recorded, not
  patched.
- No `release-pypi.yml`, `mutants.yml` or `fuzz.yml` (wave 2), and no `parity` job (T13).
- No `Justfile` change; a recipe CI needs differently is a T00 follow-up.
- No `just` on the Python 3.11 runner: that job is plain shell on purpose, so that the
  abi3 proof does not depend on pixi.

## Files touched

| Path | Class | Content |
| --- | --- | --- |
| `.github/actions/setup/action.yml` | final | P's composite action named for alliumpy; description without the allium sentence; the `.tools` and `PREK_HOME` comments reworded |
| `.github/workflows/ci.yml` | final | P's jobs with `rust`'s `effects` step removed, plus `python`, `wheel-smoke-py311` and the `check-clean` steps |
| `.github/workflows/audit.yml` | new | P's, verbatim |
| `.github/workflows/pages.yml` | new | P's, deploy conditional on visibility |
| `tickets/T01-github-and-ci.md` | ticket | `status:` and hand-back notes |

## Steps

1. Create the worktree after T00 has merged to `main`, so that the `check` job exists on
   `main` and its name can be required. Confirm it exists and passed with
   `gh api repos/BiscuitBin/alliumpy/commits/main/check-runs --jq '.check_runs[] | [.name, .conclusion, .app.id]'`.
   That run is the first time B's git dependency installed on a `BiscuitBin` runner for
   this repository (`CONVENTIONS.md` §12 claim 10); quote its setup step's log. If
   `check` did not conclude `success`, stop: requiring a red check blocks every lane
   (`CONVENTIONS.md` §13). Hand the failure back as a T00 follow-up.

2. Read the current state, read-only, and quote it. First confirm
   `gh api repos/BiscuitBin/alliumpy --jq .permissions.admin` prints `true`; if not, stop,
   because GitHub answers 404 to a token that may not read protection. Then, in this
   order: `gh api orgs/BiscuitBin --jq '{plan: .plan.name, members_can_create_pages}'`;
   `gh api repos/BiscuitBin/alliumpy --jq '{visibility, private}'`;
   `gh repo view BiscuitBin/alliumpy --json visibility,defaultBranchRef,deleteBranchOnMerge,mergeCommitAllowed,squashMergeAllowed,rebaseMergeAllowed,hasWikiEnabled,hasProjectsEnabled`;
   `mkdir -p ai_tmp; gh api repos/BiscuitBin/alliumpy/branches/main/protection > ai_tmp/protection-raw.json 2>ai_tmp/protection-err.txt; echo "exit $?"`,
   then, only on exit 0,
   `jq -S . ai_tmp/protection-raw.json > ai_tmp/protection-before.json`
   (the quoted exit is `gh`'s: on any other exit `gh` has written the error body to
   stdout, so the raw file is discarded and no before file exists; never pipe the read
   into `jq`, whose exit status would replace `gh`'s), quoting stderr too (only an HTTP
   404 whose message is `Branch not protected` means none; an HTTP 403 whose message
   names an upgrade or the repository's visibility is the protection part of
   `CONVENTIONS.md` §12 claim 11's first half, and is the state step 3 reports; any
   other error stops the step); `gh api repos/BiscuitBin/alliumpy/pages` (a 404 means no
   site; a 403 or a message about the plan is the Pages part of the same half; the
   claim's second half, the skipped deploy, is step 13's);
   `gh api repos/BiscuitBin/alliumpy/private-vulnerability-reporting --jq .enabled`.

3. **Authorisation required: the visibility and plan decision.** Stop and ask, showing
   step 2's output. The maintainer chooses one of:
   - **make the repository public** (`gh repo edit BiscuitBin/alliumpy --visibility public
     --accept-visibility-change-consequences`, run by the maintainer, never by this
     ticket), then step 2 rerun in full and quoted (that read, now a 404
     `Branch not protected`, is the before state step 7 diffs against), after which
     steps 4 to 7 run as P's did;
   - **a paid plan**, applied by the maintainer, then step 2 rerun and quoted as above,
     after which steps 4 to 7 run as P's did. The repository stays private, so
     `pages.yml`'s deploy, keyed on visibility (`CONVENTIONS.md` §10), is still skipped:
     the Pages source is set and the hand-back notes record that the deploy waits on a
     visibility change;
   - **defer protection and Pages.** Step 4's apply and step 6 are then not run (step 4's
     dry run still is). Step 5 applies the hygiene settings by hand, and the hand-back
     notes record protection and Pages as *deferred*, naming the HTTP status and message
     that blocked each, so that T11 reads them back as deferred and the maintainer sees
     the gap on every later ticket.
     `check` is still the aggregate job every pull request runs; nothing requires it.
   Record the choice, the time and the exact words in the hand-back notes.

4. **The settings dry run** (in every branch: it is read-only; only the apply below
   waits for step 3 to have made protection available). Copy T
   `scripts/bootstrap_repo.sh` at `2283589` into `ai_tmp/` (never run it from the clone)
   and dry-run it: `sh ai_tmp/bootstrap_repo.sh BiscuitBin/alliumpy --checks check
   --hygiene --no-pages`. `--no-pages` is passed so that step 6 can be authorised on its
   own, as P's T01 did; quote the whole output. P's run announced three changes (the
   protection PUT with `strict: false`, `enforce_admins: false`, one check; private
   vulnerability reporting; the hygiene `gh repo edit`); expect three on a public
   repository and two on a private one (T's step 4 announces nothing when its read
   returns 404), and explain any other difference. Where step 3 deferred protection,
   expect instead that the script stops at its step 2: the protection read's stderr,
   then `gh api repos/BiscuitBin/alliumpy/branches/main/protection failed`, exit 1, with
   nothing announced. Quote that output as `CONVENTIONS.md` §12 claim 22's evidence and
   go to step 5.

   **Adversarial review** (`CONVENTIONS.md` §14): the dry run, before the apply is
   requested. The settings steps change no repository file, so a valid finding changes
   the request, not a file, and the review goes into the authorisation request. Ask:
   whether the script will require `check` and nothing else; what in it would lock a lane
   out of merging; which setting needs an organisation owner; whether private
   vulnerability reporting is available to this repository at its visibility, and what
   the script does if it is not.

   **Authorisation required: apply** (only when step 3 made protection available). Stop
   and ask, showing the dry run. On approval,
   rerun with `--apply`, then rerun the dry run and confirm it reports no change
   (`CONVENTIONS.md` §12 claim 22).

5. **Hygiene by hand** (only when step 3 deferred protection, as step 4's dry run
   showed: the script stops at its step 2 on the protection read). The request is the
   line T's script would announce at its step 6 (Hygiene), which it never reaches here,
   so read it from T `scripts/bootstrap_repo.sh`'s source and quote it:
   `gh repo edit BiscuitBin/alliumpy --delete-branch-on-merge --enable-wiki=false --enable-projects=false`.

   **Adversarial review** (`CONVENTIONS.md` §14): the one line, before the stop; step 4's
   review, which is for the apply, does not run on this route. Ask: what else
   `gh repo edit` with those three flags changes; whether the deferral record quotes the
   403 and its message for protection and for Pages.

   **Authorisation required: hygiene.** Stop and ask. On approval run that one line
   verbatim, then read back with step 2's `gh repo view` and confirm `deleteBranchOnMerge`
   is true and wiki and projects are off. Record that T's script was not applied and why.

6. **The Pages source** (only when step 3 made Pages available). **Authorisation
   required.** Stop and ask. On approval:
   `gh api -X POST repos/BiscuitBin/alliumpy/pages -f build_type=workflow`, or `-X PUT`
   if Pages already exists. Read it back with `gh api repos/BiscuitBin/alliumpy/pages`.

7. Read every setting back (step 2's commands) and quote the output. Where protection
   was applied, save the response as `ai_tmp/protection-after.json`, diff it against
   `ai_tmp/protection-before.json` (or state that the before state was a 404), list every
   field that changed, and confirm each is one the dry run announced; T's apply is a
   full PUT, so a field it leaves out returns to GitHub's default (a true `lock_branch`
   blocks every merge). Read the required check from `.checks`, not the deprecated
   `.contexts`, and record its `app_id` against the one step 1 printed for `check`
   (P's run bound `15368`, GitHub Actions). If they differ, hand it back; do not patch
   T's script. Where protection or Pages was deferred, quote the 403 or the plan
   message again here, so the deferral is evidence and not an omission.

8. **The setup action and the workflows.** Copy P `.github/actions/setup/action.yml`, P
   `.github/workflows/ci.yml`, P `.github/workflows/audit.yml` and P
   `.github/workflows/pages.yml` at `bf51e0d`, then apply `CONVENTIONS.md` §10 and these
   deltas, and nothing else:
   - `action.yml`: `name:` reads `Set up the alliumpy toolchain`, as T00's stub must
     already have it (T00's acceptance grep forbids `pachinko`); the description's last
     sentence about the allium binary goes (T00's stub already dropped it: confirm); the
     `.tools` cache comment names cargo-hack and rustqual only; the `PREK_HOME` comment
     drops `T03 confirms` (L's ticket; here T03 is the Python gate) and reads
     `PREK_HOME is prek 0.5.3's cache variable`. Everything else is P's.
   - `ci.yml`, job `rust`: the `- run: just effects` step goes; the step list is §10's.
   - `ci.yml`, new job `python` after `rust`: checkout and the setup action
     (`cache-key: python`), then one step per recipe, `just py-lint`, `just py-typecheck`,
     `just py-test`, `just py-stubtest`, `just wheel-smoke`, `just version-check`, then
     `actions/upload-artifact` with `name: wheel-linux`, `path: dist/*.whl`,
     `if-no-files-found: error`, `retention-days: 7`. `timeout-minutes: 30`: it builds
     the extension twice.
   - `ci.yml`, new job `wheel-smoke-py311` with `needs: [python]` and
     `timeout-minutes: 10`: `actions/checkout`
     (`persist-credentials: false`), `actions/setup-python` with
     `python-version: '3.11'`, `actions/download-artifact` with `name: wheel-linux`,
     `path: dist`, then one `run:` step in plain shell:
     `python -m venv venv && venv/bin/pip install --no-index --no-deps dist/*.whl &&
     venv/bin/python -I tests/fixtures/smoke/smoke.py && venv/bin/allium --version`.
     No setup action and no `just`: this job proves the wheel on an interpreter pixi
     does not have, and must not depend on the environment that built it. A comment
     says this is the one pre-release proof of the abi3 floor (`CONVENTIONS.md` §9).
   - `ci.yml`, job `documents`: the steps are `just lint`, `just check-docs`,
     `just check-agents`. No `install-allium`, no `check-specs`, no `analyse-specs`; the
     comments that explained them go.
   - `ci.yml`, every job that runs recipes (`rust`, `python`, `coverage`, `deny`,
     `documents`): a final `- run: just check-clean` step. P's T01 found that CI never
     ran it, so a recipe that rewrote a tracked file passed in CI and failed locally
     (P `tickets/T01-github-and-ci.md`, Open points). This is a delta beyond P's
     `ci.yml`; `CONVENTIONS.md` §10 is this repository's to define, and the comment
     above the step says why it is there. `coverage`'s step goes after the artefact
     upload, so a failure there still leaves the lcov file to read.
   - `ci.yml`, job `check`: `needs: [rust, python, wheel-smoke-py311, coverage, deny,
     documents]`, everything else P's. The comment above `jobs:` is rewritten to stay
     true: two crates and a wheel, six gate jobs, and why `wheel-smoke-py311` is the one
     job not on the setup action.
   - `pages.yml`, job `build`: unchanged (it keeps `cache-key: pages`). Job `deploy`: the
     `if:` becomes
     `github.ref == 'refs/heads/main' && github.event.repository.visibility == 'public'`,
     with a comment citing `CONVENTIONS.md` §1 fact 6: on a private repository the run
     builds and uploads and the deploy is skipped, never failed. Confirm from the
     GitHub Actions context documentation on the day that
     `github.event.repository.visibility` is present on `push` and `workflow_dispatch`
     events; if it is not, use the equivalent (`github.event.repository.private == false`)
     and record which.
   - `audit.yml`: P's, verbatim.

9. Re-read every action's tag SHA (`gh api repos/<owner>/<repo>/git/ref/tags/<tag>`,
   then `gh api repos/<owner>/<repo>/git/tags/<sha>` to dereference an annotated tag).
   Keep P's versions unless one is withdrawn; a newer version is Renovate's to propose
   (T17). Two actions are new here and have no P pin: `actions/setup-python` and
   `actions/download-artifact`. For each, read the newest release with
   `gh api repos/actions/<name>/releases/latest --jq .tag_name`, then its commit as
   above, and pin it with the version comment. Every `uses:` carries a 40-character SHA
   and a `# vX.Y.Z` comment.

10. `just lint` (actionlint runs over the workflows), then `just check`.

    **Adversarial review** (`CONVENTIONS.md` §14): the workflows and the setup action,
    before step 11 pushes them. Ask: which delta from P goes beyond `CONVENTIONS.md` §10
    and this ticket's step 8; whether every SHA is its tag's commit, with annotated tags
    dereferenced; whether `check`'s `needs` lists every gate job and nothing optional;
    whether `wheel-smoke-py311` could pass against a wheel other than the one `python`
    built (the artefact name, `--no-index --no-deps`, a cached pip); whether `smoke.py`
    could import the worktree's `python/alliumpy/` instead of the installed wheel;
    whether the `deploy` condition can be true on a private repository or false on a
    public one; whether any job's permissions exceed P's; whether `check-clean` runs
    after every recipe step in every gate job.

11. **Authorisation required: push and open a pull request.** Stop and ask. On approval,
    push the branch and open a pull request against `main`. Wait for the run.

12. Read the result: every gate job and `check` green; `gh pr checks` lists `check`,
    and `--required` lists it only if protection was applied; `audit` ran and is not
    required. Read the `python` job's log and quote the wheel filename it uploaded and
    the `version-check` line; read `wheel-smoke-py311`'s log and quote the Python version
    `setup-python` installed, the `pip install` line and the `allium --version` output.
    Claim 10's evidence (`CONVENTIONS.md` §12 claim 10) is step 1's stub run, where the
    pixi cache missed and B's git dependency was fetched: quote from it the checkout's
    `Removing credentials config` line and the install's success, as P's T01 hand-back
    notes do. This run is expected to restore `main`'s pixi cache (setup-pixi keys it on
    `pixi.lock`), so B is not fetched here; record its `Cache hit for: pixi-linux-64-…`
    line as such, not as proof. If it misses instead, quote this run's B install too.

13. After the merge, which the maintainer performs, read the `pages.yml` run on `main`:
    `build` succeeded, and `deploy` either deployed (public) or was skipped (private),
    never failed. Quote the job conclusions. If it deployed, fetch the Pages URL and
    confirm both crates' pages load from the root index. This evidence post-dates the pull
    request that set `status: done`, so it lands as a notes-only commit to this file on a
    new branch, pushed and opened as a follow-up pull request under one more stop
    (**Authorisation required: the notes follow-up**, `CONVENTIONS.md` §11); `status:`
    stays `done`, and until it merges the notes say step 13 is pending. If the maintainer
    prefers, hand step 13 to T11 instead and record that.

## Acceptance criteria

- Step 2's reads are quoted with their HTTP statuses, and step 3's authorisation records
  the maintainer's choice in their words.
- Where protection was applied:
  `gh api repos/BiscuitBin/alliumpy/branches/main/protection/required_status_checks --jq '[.checks[] | {context, app_id}]'`
  prints exactly one entry, `check`, whose `app_id` is the one step 1 recorded; the
  protection diff lists only changes the dry run announced; a second dry run reports no
  change. Where protection was deferred: the hand-back notes quote the 403 and its
  message, and say "deferred", and nothing claims protection.
- Where Pages was applied: `gh api repos/BiscuitBin/alliumpy/pages --jq .build_type`
  prints `workflow`, and the `pages.yml` run on `main` deployed if the repository is
  public. Where the repository is private (Pages deferred, or applied on a paid plan):
  the `pages.yml` run on `main` shows `build` succeeded and `deploy` skipped. Either is
  recorded by step 13's notes follow-up (or by T11, if handed over).
- The hygiene settings read back as applied (`deleteBranchOnMerge: true`, wiki and
  projects off), by the script or by step 5's one line, and the notes say which.
- Every apply was authorised before it ran; the hand-back notes say when.
- The pull request's checks are green; `check`'s `needs` names `rust`, `python`,
  `wheel-smoke-py311`, `coverage`, `deny` and `documents`.
- `wheel-smoke-py311`'s log shows setup-python's `Successfully set up CPython (3.11.x)`
  line (the plain-shell step prints no version), an install from `dist/` with
  `--no-index --no-deps`, and `allium 3.6.1 (language versions: 1, 2, 3)`.
- Every gate job that runs recipes (`rust`, `python`, `coverage`, `deny`, `documents`)
  has `just check-clean` as its last step; `wheel-smoke-py311` runs no recipe, by
  design.
- Every remote `uses:` names a 40-character SHA with a version comment; the local
  `uses: ./.github/actions/setup` has none.
- `just check` is green.
- The adversarial reviews in Steps ran (`CONVENTIONS.md` §14), and every valid finding is
  fixed or handed back.

## Verification

```sh
gh api orgs/BiscuitBin --jq '{plan: .plan.name, members_can_create_pages}'
gh api repos/BiscuitBin/alliumpy --jq '{visibility, private, permissions}'
gh api repos/BiscuitBin/alliumpy/branches/main/protection; echo "exit $?"
gh api repos/BiscuitBin/alliumpy/branches/main/protection/required_status_checks --jq '[.checks[] | {context, app_id}]'; echo "exit $?"
diff ai_tmp/protection-before.json ai_tmp/protection-after.json; echo "exit $?"
gh api repos/BiscuitBin/alliumpy/pages; echo "exit $?"
gh repo view BiscuitBin/alliumpy --json deleteBranchOnMerge,mergeCommitAllowed,squashMergeAllowed,rebaseMergeAllowed,hasWikiEnabled,hasProjectsEnabled
sh ai_tmp/bootstrap_repo.sh BiscuitBin/alliumpy --checks check --hygiene --no-pages; echo "exit $?"
just lint
gh pr checks <number> --repo BiscuitBin/alliumpy
gh pr checks <number> --repo BiscuitBin/alliumpy --required
gh run view <ci-run-id> --repo BiscuitBin/alliumpy --job <wheel-smoke-py311-job-id> --log | rg 'Successfully set up CPython \(3\.11|pip install|allium 3\.6\.1'
gh run list --repo BiscuitBin/alliumpy --workflow pages.yml --limit 1
gh run view <pages-run-id> --repo BiscuitBin/alliumpy --json jobs --jq '.jobs[] | [.name, .conclusion]'
rg -n 'uses: ' .github > ai_tmp/uses.txt; echo "exit $?"; wc -l < ai_tmp/uses.txt
rg -v 'uses: \./' ai_tmp/uses.txt | rg -v '@[0-9a-f]{40} # v[0-9]+\.[0-9]+\.[0-9]+$'
rg -c '^\s*- run: just check-clean\s*$' .github/workflows/ci.yml
awk '/^  [A-Za-z0-9_-]+:$/{if(j)print j" "l; j=$1; l=""} /^      - /{l=$0} END{print j" "l}' .github/workflows/ci.yml
just check
```

The first `rg` line must exit 0 with a count above zero; the second must print nothing and
exits 1, which is `rg` reporting no match (P's notes record `(nothing) exit 1`); the third
must print `5` (step lines only; the comments above them may name the recipe); the `awk`
line prints each two-space key with the last six-space list item under it, which for
`rust:`, `python:`, `coverage:`, `deny:` and `documents:` must be
`- run: just check-clean` (a count of five alone would pass with two in one job and none
in another; the `on:` keys print too and are ignored; if `ci.yml` is not indented as P's,
quote each job's last step from the actionlint-validated file instead). The
`bootstrap_repo.sh` dry run exits 0 with
`changed: 0 (dry run; 0 would change)` where protection was applied, and exits 1 at
its step 2 with the protection read's error on stderr where it was deferred; either is
quoted as the result for that branch. The `gh run view --log` line is filtered, so the
unfiltered `--log` is read first and the three matches are quoted from it. The
`protection`, `required_status_checks`, `diff` and `pages` lines are the applied-path
lines; where protection or Pages was deferred, run them anyway and quote the 403 or 404
and `diff`'s exit 2 (there is no `protection-after.json`, because nothing was applied)
as the deferral evidence, not as a failure. `gh pr checks --required` prints `check`
and exits 0 where protection was applied; where it was deferred it prints
`no required checks reported on the '<branch>' branch` and exits 1, which is the
expected result and is quoted as such.

## Hand-back notes

To be written by the executing agent, as P `tickets/T01-github-and-ci.md`'s are: the
state before, with every HTTP status; the maintainer's step 3 decision, quoted and timed;
the dry run (or why it could not run); each authorisation, when, and what ran; the state
after, and `CONVENTIONS.md` §12 claims 10, 11 and 22 each marked holds, fails or deferred
with the evidence; every action pin as a table of action, tag and commit, the two new
pins marked; the delta list of step 8 as built, including the `check-clean` steps; the
pull request, its run URLs and the merge commit the run tested; the `wheel-smoke-py311`
quotes; the `pages.yml` result after the merge; the review record for each checkpoint
(`CONVENTIONS.md` §14); what was handed back to which lane.

## Open points

- Whether administrators are included in protection (`enforce_admins`). P's T01 applied
  `false`, as L did; follow it unless the maintainer says otherwise.
- Private vulnerability reporting: T's script enables it; on a private repository it may
  be unavailable or need GitHub Advanced Security. Record what the API said; `SECURITY.md`
  (T12) points at whatever exists.
- If the maintainer makes the repository public, the Pages URL will be
  `https://biscuitbin.github.io/alliumpy/`; T07's `deploy-to-github-pages.md` and decision
  0008 need to know, so hand the outcome to T07 and T11.
- Actions minutes on a private repository are metered (`CONVENTIONS.md` §13). The
  `python` job builds the extension twice on every pull request; if the monthly quota
  becomes a problem before T14's release matrix lands, the maintainer decides between a
  paid plan and a public repository, and this ticket's hand-back notes record the
  minutes the first full run consumed as the baseline.
