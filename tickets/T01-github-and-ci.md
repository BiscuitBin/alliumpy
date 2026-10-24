---
id: T01
title: "GitHub repository and CI: settings, branch protection, workflows, the abi3 floor"
status: done
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

Times are UTC. The settings evidence ran against the live repository between
2026-10-24T05:39Z and 06:24Z at `5b76af6` (the worktree clean, `origin/main` the same
commit). The workflow evidence ran at `5b76af6` with the step 8 changes uncommitted
(staged), and again at `463076e`, the commit that lands them after the rebase onto `a2dd325`. The branch is
`ticket/T01-github-and-ci`, the worktree tool's casing of the `branch:` field's
`ticket/t01-github-and-ci`.

### Baseline

`just check` on the untouched worktree, `5b76af6`, 05:59:44Z to 06:00:52Z: `All checks
passed and the worktree is unchanged.`, exit 0; `git status --short` printed nothing.

### Step 1: `check` on `main`

`gh api repos/BiscuitBin/alliumpy/commits/main/check-runs --jq '.check_runs[] | [.name,
.conclusion, .app.id]'` at 05:39:31Z printed `["check",null,15368]`: the merge's run
`https://github.com/BiscuitBin/alliumpy/actions/runs/40066796921` (push, `5b76af6`) was
still in progress. After `gh run watch` exited 0 it printed `["check","success",15368]`,
exit 0. That run's log (job `check`, saved as `ai_tmp/stub-run.log`):

- `Removing credentials config
  '/home/runner/work/_temp/git-credentials-3d501599-eb5b-453e-a2bf-5ef6efe4cf31.config'`
  (05:34:46.46Z), the checkout's last line before the setup action.
- setup-pixi: `Restoring project cache` / `Cache miss` (05:34:49.66Z), then `pixi
  install --locked ...` and `✔ The default environment has been installed.`
  (05:34:57.08Z). `pixi list --locked` lists `biscuit_games_tooling 0.3.0 pypi`. The
  setup action passes setup-pixi no token, and `pixi.lock` pins
  `git+https://github.com/steven-cutting/biscuit_games_tooling?tag=v0.3.0#6c5c07f6bec86e86b3930dfa41392e4b440e8c85`,
  with no credential in the URL.
- `just check` ended `All checks passed and the worktree is unchanged.` (05:40:32Z).

### State before (step 2, 2026-10-24T05:39:47Z, private)

| Read | Result |
| --- | --- |
| `.permissions.admin` | `true`, exit 0 |
| `orgs/BiscuitBin` | `{"members_can_create_pages":true,"plan":"free"}`, exit 0 |
| `{visibility, private}` | `{"private":true,"visibility":"private"}`, exit 0 |
| `gh repo view` | private, default `main`, `deleteBranchOnMerge: false`, merge, squash and rebase allowed, `hasWikiEnabled: false`, `hasProjectsEnabled: true` |
| protection | exit 1; HTTP 403, `Upgrade to GitHub Pro or make this repository public to enable this feature.` No before file. |
| Pages | HTTP 404 `Not Found`, exit 1 (no site; the read names no plan) |
| private vulnerability reporting | HTTP 404 `Not Found`, exit 1 |

The protection 403 is the protection half of claim 11's first half, and it holds. The
Pages read answered 404, not a plan message, so the Pages half is not shown by a read
here.

T's dry run at 05:40:11Z, while private, stopped at its step 2, as claim 22 predicted:
`gh: Upgrade to GitHub Pro or make this repository public to enable this feature. (HTTP
403)`, then `gh api repos/BiscuitBin/alliumpy/branches/main/protection --jq [...]
failed`, exit 1, nothing announced.

### Step 3: the maintainer's decision

Asked at about 05:41Z with the private reads above and three choices (defer, make
public, paid plan). The answer, recorded at 2026-10-24T05:55:21Z, was in the
maintainer's words: "it is public now". The maintainer ran the visibility change; this
ticket did not.

Step 2 rerun (05:55:21Z, public): admin `true`; plan `free`,
`members_can_create_pages: true`; `{"private":false,"visibility":"public"}`; `gh repo
view` as before except `visibility: PUBLIC`; Pages HTTP 404 `Not Found`; private
vulnerability reporting `false`, exit 0. The protection line of that rerun is void:
zsh's `noclobber` refused the redirect (`file exists: ai_tmp/protection-err.txt`), so
`gh` never ran and the block printed the private read's stale stderr. Reread at
05:55:31Z with the old files removed: exit 1, `{"message":"Branch not
protected",...,"status":"404"}` and `gh: Branch not protected (HTTP 404)`. That is the
before state; there is no `protection-before.json`.

### Dry run (step 4, 05:55:36Z)

`sh ai_tmp/bootstrap_repo.sh BiscuitBin/alliumpy --checks check --hygiene --no-pages`,
T's script at `2283589` copied into `ai_tmp/` (byte-identical to the pin). Three
changes, exit 0, as P's:

- 2: `state: not protected (HTTP 404)`, `wanted: false check false false false false
  false`, `would: gh api -X PUT .../branches/main/protection --input -` with
  `strict: false`, `checks: [{context: check}]`, `enforce_admins: false`, reviews and
  restrictions null, force pushes and deletions false.
- 4: `state: false`, `would: gh api -X PUT .../private-vulnerability-reporting`.
- 6: `state: false false true`, `would: gh repo edit BiscuitBin/alliumpy
  --delete-branch-on-merge --enable-wiki=false --enable-projects=false`.
- 3 skipped (no Chromatic token); 5 prints instructions only. `changed: 0 (dry run; 3
  would change)`.

The repository was public by then, so three, not two, as the ticket expects for a
public repository.

### Authorisations

| Action | Authorised | Ran |
| --- | --- | --- |
| Step 3: visibility | maintainer's own action, reported 05:55:21Z | not run by this ticket |
| Step 4: `--apply` with the dry run's flags | 06:23:17Z | `changed: 3`, exit 0 |
| Step 6: `gh api -X POST repos/BiscuitBin/alliumpy/pages -f build_type=workflow` | 06:24:15Z | returned the Pages object, exit 0 |
| Step 11: push, open the pull request, one follow-up evidence push | 2026-10-24T10:07:34Z | PR #7, this commit the follow-up |

Step 5 did not apply (protection was available, so the script applied hygiene).

### State after (step 7, 06:23:31Z) and claims 11 and 22

The second dry run (06:23:21Z, same flags) reported `already` for steps 2, 4 and 6 and
`changed: 0 (dry run; 0 would change)`, exit 0.

From `ai_tmp/protection-after.json` (`gh api ... | jq -S .`, both exits 0):

```text
{"checks":[{"app_id":15368,"context":"check"}],"strict":false,"contexts":["check"],
 "enforce_admins":false,"lock_branch":false,"fp":false,"del":false,"linear":false,
 "sigs":false,"conv":false,"block_creations":false,"fork_sync":false,
 "reviews":null,"restr":null}
```

- `required_status_checks --jq '[.checks[] | {context, app_id}]'`:
  `[{"app_id":15368,"context":"check"}]`, exit 0. `15368` is the app step 1 printed
  for `check` (GitHub Actions, the same as P's run).
- There is no diff: the before state was the 404 `Branch not protected`, so `diff`
  exits 2 for the missing before file. Every field the protection object now holds is
  either one the dry run announced or at GitHub's default; `lock_branch`, signatures,
  linear history, conversation resolution, `block_creations` and fork syncing all read
  false, and reviews and restrictions are absent. Nothing blocks a merge.
- Private vulnerability reporting: `true`, exit 0.
- `gh repo view`: `deleteBranchOnMerge: true`, `hasWikiEnabled: false`,
  `hasProjectsEnabled: false`; merge, squash and rebase still allowed; `PUBLIC`.
  Hygiene was applied by T's script, not by hand.
- Pages (06:24:15Z): `build_type: workflow`, `html_url:
  https://biscuitbin.github.io/alliumpy/`, `public: true`, `https_enforced: true`. The
  `github-pages` environment's deployment branch policy is custom.

Claim 22 holds in both halves: T's script fails at its step 2 on a private free-plan
repository, in the way the dry run showed, and on the public repository it applies
and reruns with no change. Claim 11: the protection half of the first half holds (the
403 while private); the Pages half was not shown by a read (404 while private); the
second half (the skipped deploy) cannot be shown, because the repository is now
public. The deploy's private-repository branch is therefore untested by a run.

### Workflows (step 8) as built

- `action.yml`: `name:` already read `Set up the alliumpy toolchain`, and the
  description's allium sentence was already gone (T00). The `.tools` comment names
  cargo-hack and rustqual only (T00 had dropped the allium clause but left one long
  line; it is rewrapped). The `PREK_HOME` comment reads `PREK_HOME is prek 0.5.3's
  cache variable.` Nothing else differs from P.
- `ci.yml`: `rust`'s `- run: just effects` is gone; its steps are §10's list. New
  `python` (`cache-key: python`, `timeout-minutes: 30`): `py-lint`, `py-typecheck`,
  `py-test`, `py-stubtest`, `wheel-smoke`, `version-check`, then `upload-artifact`
  `wheel-linux` from `dist/*.whl`, `if-no-files-found: error`, seven days. New
  `wheel-smoke-py311` (`needs: [python]`, `timeout-minutes: 10`): checkout without
  credentials, setup-python `3.11`, download-artifact `wheel-linux` into `dist`, one
  plain-shell step. That step carries `venv/bin/python --version`, which §10 lists
  and the ticket's step 8 omits; §10 wins where the two differ, so the log also shows
  `Python 3.11.x` from the venv. `documents` runs `lint`, `check-docs`,
  `check-agents`. Each of `rust`, `python`, `coverage`, `deny` and `documents` ends
  with `- run: just check-clean` (in `python` and `coverage`, after the upload). The
  comment above `jobs:` was rewritten: two crates and a wheel, six gate jobs, and why
  `wheel-smoke-py311` is off the setup action. `check.needs` is `[rust, python,
  wheel-smoke-py311, coverage, deny, documents]`.
- `pages.yml`: P's, except `deploy`'s `if:` is `github.ref == 'refs/heads/main' &&
  github.event.repository.private == false`, with a comment citing §1 fact 6. Which
  field, as step 8 asks: the GitHub contexts page documents `github.event` only as
  "The full event webhook payload", so the payload was read from GitHub's OpenAPI
  description (`github/rest-api-description` at `755ee33`). `webhook-push` requires
  `repository`, whose schema requires both `private` and `visibility`;
  `webhook-workflow-dispatch` requires `repository` (`repository-webhooks`), which
  requires `private` but only lists `visibility` (default `public`). So
  `github.event.repository.visibility` is not confirmed present on
  `workflow_dispatch`, and the ticket's equivalent, `private == false`, is used. The
  first draft used `visibility == 'public'`, chosen because GitHub's loose `==`
  coerces `null` and `false` both to 0, so `private == false` reads an absent field
  as public. Review finding T01-2 c1 showed the trade: `visibility` can be false on a
  public repository's manual dispatch, while `private` is required on both events, so
  its absent-field case is outside the schema. The fix was applied in triage.
- `audit.yml`: P's, verbatim.
- Permissions equal P's: `contents: read` at the top of each workflow, and `pages:
  write` plus `id-token: write` only on `pages.yml`'s `deploy`. The new jobs add none:
  `download-artifact` within a run needs no `actions: read`.

### Action pins (step 9), read 2026-10-24T05:56:40Z

| Action | Tag | Commit |
| --- | --- | --- |
| `actions/checkout` | v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| `actions/upload-artifact` | v7.0.1 | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` |
| `actions/upload-pages-artifact` | v5.0.0 | `fc324d3547104276b827a68afc52ff2a11cc49c9` |
| `actions/deploy-pages` | v5.0.1 | `368f82528645a54fb793d4d04e342629a3f51346` |
| `prefix-dev/setup-pixi` | v0.10.2 | `d3f436a425481402e6a95a1d1fc10331c708cd9e` |
| `Swatinem/rust-cache` | v2.9.2 (annotated `63fed3e2…`) | `6323deb102c322ba6fcbdcafc7e3dddab59af2b6` |
| `actions/cache` | v6.1.0 | `55cc8345863c7cc4c66a329aec7e433d2d1c52a9` |
| `actions/setup-python` (new) | v7.1.0, `releases/latest` | `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` |
| `actions/download-artifact` (new) | v8.0.2, `releases/latest` | `9000827ccba6bdab643e8b6fd33ac0654aef8333` |

P's seven are unchanged and none is withdrawn. Every tag but rust-cache's is
lightweight; rust-cache's was dereferenced through `git/tags/63fed3e2…`.
download-artifact v8 errors on a digest mismatch by default and no longer unzips a
non-zip download; the `wheel-linux` artefact is an ordinary zipped upload from
upload-artifact v7, and the PR run is the proof that the two interoperate.

### Verification (step 10)

`just lint` at `5b76af6` with the step 8 changes staged: exit 0, with `Lint GitHub
Actions workflow files....Passed`. The two new workflow files were untracked at first,
so `prek --all-files` could not see them; they were staged and actionlint rerun.
Positive control: `needs.nonexistent.result` added to `pages.yml`'s `deploy` `if:` made
actionlint exit 1 (`property "nonexistent" is not defined in object type {build: ...}
[expression]`); with the file restored it passed. `just check` at `5b76af6` with the
changes staged (06:26Z), and again after the review fix (10:00Z): `All checks passed
and the worktree is unchanged.`, exit 0.

`git fetch origin` then showed `origin/main` at `a2dd325` (T02, T03 and T05 merged;
none touches `.github/` or this ticket). The workflow commit was rebased onto it as
`463076e`. `main`'s own `check` on `a2dd325` reads `["check","success",15368]`.

At `463076e`, clean, 2026-10-24T10:00:56Z to 10:01:19Z:

```text
$ just check
All checks passed and the worktree is unchanged.                          exit 0
$ git status --short
(nothing)
$ gh api orgs/BiscuitBin --jq '{plan: .plan.name, members_can_create_pages}'
{"members_can_create_pages":true,"plan":"free"}                           exit 0
$ gh api repos/BiscuitBin/alliumpy --jq '{visibility, private, permissions}'   (admin shown)
{"admin":true,"private":false,"visibility":"public"}                      exit 0
$ gh api repos/BiscuitBin/alliumpy/branches/main/protection   (fields shown)
{"checks":[{"app_id":15368,"context":"check"}],"enforce_admins":false,"lock_branch":false,"strict":false}  exit 0
$ gh api .../protection/required_status_checks --jq '[.checks[] | {context, app_id}]'
[{"app_id":15368,"context":"check"}]                                      exit 0
$ diff ai_tmp/protection-before.json ai_tmp/protection-after.json
(no before file: the before state was the 404 Branch not protected)       exit 2
$ gh api repos/BiscuitBin/alliumpy/pages   (fields shown)
{"build_type":"workflow","html_url":"https://biscuitbin.github.io/alliumpy/"}  exit 0
$ gh repo view BiscuitBin/alliumpy --json deleteBranchOnMerge,...,hasProjectsEnabled
{"deleteBranchOnMerge":true,"hasProjectsEnabled":false,"hasWikiEnabled":false,
 "mergeCommitAllowed":true,"rebaseMergeAllowed":true,"squashMergeAllowed":true}  exit 0
$ sh ai_tmp/bootstrap_repo.sh BiscuitBin/alliumpy --checks check --hygiene --no-pages
changed: 0 (dry run; 0 would change)                                      exit 0
$ rg -n 'uses: ' .github > ai_tmp/uses.txt; echo "exit $?"; wc -l < ai_tmp/uses.txt
exit 0, 25
$ rg -v 'uses: \./' ai_tmp/uses.txt | rg -v '@[0-9a-f]{40} # v[0-9]+\.[0-9]+\.[0-9]+$'
(nothing)                                                                 exit 1
$ rg -c '^\s*- run: just check-clean\s*$' .github/workflows/ci.yml
5
$ awk ... .github/workflows/ci.yml   (on: keys ignored)
rust:       - run: just check-clean
python:       - run: just check-clean
wheel-smoke-py311:       - run: |
coverage:       - run: just check-clean
deny:       - run: just check-clean
documents:       - run: just check-clean
check:       - if: ${{ contains(needs.*.result, 'failure') || ... }}
```

### Pull request (steps 11 and 12)

PR: `https://github.com/BiscuitBin/alliumpy/pull/7`, head `e6cdbe4`. GitHub tested the
merge commit `da88305` (`HEAD is now at da88305 Merge e6cdbe4... into a2dd325...` in each
job's checkout). CI run `https://github.com/BiscuitBin/alliumpy/actions/runs/40084672655`
(10:07:39Z to 10:09:03Z, `run_duration_ms: 84000`); Audit run
`https://github.com/BiscuitBin/alliumpy/actions/runs/40084672650`.

```text
$ gh pr checks 7 --repo BiscuitBin/alliumpy
audit              pass  29s   .../actions/runs/40084672650/job/120845043409
check              pass   3s   .../actions/runs/40084672655/job/120845288781
coverage           pass  39s   .../actions/runs/40084672655/job/120845043722
deny               pass  34s   .../actions/runs/40084672655/job/120845043723
documents          pass  59s   .../actions/runs/40084672655/job/120845043563
python             pass  1m0s  .../actions/runs/40084672655/job/120845043684
rust               pass  59s   .../actions/runs/40084672655/job/120845043736
wheel-smoke-py311  pass  12s   .../actions/runs/40084672655/job/120845243463
exit 0
$ gh pr checks 7 --repo BiscuitBin/alliumpy --required
check              pass   3s   .../actions/runs/40084672655/job/120845288781
exit 0
```

`audit` ran and is not required. The job step lists match step 8. `rust` runs
`check-toolchain`, `lock-check`, `fmt-check`, `toml-check`, `clippy`, `metrics`,
`features`, `test`, `snapshots-check`, `doc`, `deps-unused`, `check-clean`; `documents`
runs `lint`, `check-docs`, `check-agents`, `check-clean`. Each of `rust`, `python`,
`coverage`, `deny` and `documents` printed `The Git worktree is clean.` at its last
step, so the setup action leaves nothing git sees. `coverage` printed `TOTAL ...
100.00%` under the 90% floor.

`python` (job `120845043684`):

- `📦 Built wheel for abi3 Python ≥ 3.11 to
  dist/alliumpy-3.6.1-cp311-abi3-manylinux_2_34_x86_64.whl` (10:08:37.49Z).
- `version-check: all five versions agree: 3.6.1` (10:08:37.81Z).
- `With the provided path, there will be 1 file uploaded`, then `Artifact wheel-linux
  has been successfully uploaded! Final size is 303974 bytes. Artifact ID is
  12556492915`.

`wheel-smoke-py311` (job `120845243463`), read from the unfiltered log:

- `Successfully set up CPython (3.11.17)` (10:08:47.43Z).
- download-artifact: `wheel-linux (ID: 12556492915, Size: 303974, Expected Digest:
  sha256:c969a9d2…)`, then `SHA256 digest of downloaded artifact is c969a9d2…` and
  `Total of 1 artifact(s) downloaded`. This is the artefact `python` uploaded, so
  download-artifact v8.0.2 reads upload-artifact v7.0.1's artefact.
- `venv/bin/pip install --no-index --no-deps dist/*.whl`, `Python 3.11.17`, `Processing
  ./dist/alliumpy-3.6.1-cp311-abi3-manylinux_2_34_x86_64.whl`, `Successfully installed
  alliumpy-3.6.1`.
- `allium 3.6.1 (language versions: 1, 2, 3)` (10:08:54.55Z).

Claim 10's evidence is step 1's stub run, where setup-pixi's cache missed and B's git
dependency was fetched with no credential (quoted above). In this run `python`'s
checkout printed `Removing credentials config
'/home/runner/work/_temp/git-credentials-3935855a-....config'`, then `Cache hit for:
pixi-linux-64-62307468e2b4...` and `✔ The default environment has been installed.`.
That is `main`'s cache, so B was not fetched here, and this line is not the proof.
Claim 10 holds on the stub run.

Billable minutes: `actions/runs/40084672655/timing` reports `total_ms: 0` for the seven
Ubuntu jobs. The repository is public, so standard runners are not billed; the run took
84 s of wall-clock time.

The wheel is tagged `manylinux_2_34`, the glibc floor of the runner that built it. The
release matrix's manylinux target is T14's to choose; this is noted for it.

### Pages after the merge (step 13)

At `844e9b6`, `main` after the maintainer merged the pull request (21:01:06Z), on top
of `5c46a20`. The notes follow-up was authorised by the maintainer.

```console
$ gh run view 40132356384 --repo BiscuitBin/alliumpy --json jobs --jq '.jobs[] | [.name, .conclusion]'
["build","success"]
["deploy","success"]
```

The run's event is `push`, so `deploy`'s `if:` was true on a public repository. Its log
shows `Created deployment for 844e9b64c6447bfa5d9ce27db1161540f57bd88d`, `Reported
success!` and `Evaluated environment url: https://biscuitbin.github.io/alliumpy/`.
`gh api repos/BiscuitBin/alliumpy/pages` still reads `build_type: workflow`.

Each page fetched from the site answered HTTP 200 with the expected `<title>`:

| Path | `<title>` |
| --- | --- |
| `/` | `alliumpy: API reference`, linking `alliumpy_core/index.html` and `alliumpy/index.html` |
| `/alliumpy_core/index.html` | `alliumpy_core - Rust`, version 3.6.1 |
| `/alliumpy/index.html` | `alliumpy - Rust`, version 3.6.1 |

The CI run on the same push (40132356469) passed all seven jobs: `check` and its six
`needs`. The skip on a private repository stays T11's, as handed back below.

### Review records (CONVENTIONS.md §14)

For both checkpoints the harness was codex-cli 0.163.0, running `codex exec -m
gpt-6-astra -s read-only`. One conformance reviewer and one breakage reviewer ran in
parallel, then a separate Claude Code subagent (Opus 5.5) triaged. Raw files are under
`ai_tmp/review/T01-<n>/`.

**Checkpoint 1, the dry run, before the step 4 apply request.** The live state was read
at 05:55Z and the worktree was at `5b76af6`. No file was involved.

| id | Verdict | Reason |
| --- | --- | --- |
| c1 | valid, low | The 05:55:21Z protection line was a `noclobber` failure printing stale stderr. Action: the 05:55:31Z 404 is quoted as the before state (above). |
| c2 | valid, low | The artefact lacked its commit heading. Action: the evidence is headed `5b76af6`, and the script copy is stated identical to T `2283589`. |
| b1 | valid, medium | The PUT names no `app_id` and the "already" compare reads names only. Action: step 7 asserted `[{"app_id":15368,"context":"check"}]`. |
| b2 | valid, low | The compare and the PUT omit `lock_branch` and the other lockout fields. Action: step 7 asserted each of them false. |
| b3 | valid, low | Any 404 from vulnerability reporting reads as "private". Action: step 7 required `enabled: true`. |

All five changed the authorisation request and the read-back, not a file. None was
high, so there was no second round.

**Checkpoint 2, the workflows, before step 11.** The changes were staged on
`5b76af6`. The first launch hung on stdin and produced nothing; it was killed and rerun
at about 09:56Z.

| id | Verdict | Reason |
| --- | --- | --- |
| c1 | valid, medium; applied | `visibility` is required on `push` but not on `workflow_dispatch`, so a public repository's manual deploy could be skipped. Action: `deploy`'s `if:` now reads `private == false`, the ticket's named equivalent, with the comment rewritten. |
| (breakage) | no findings | All nine pins match their tags' commits, rust-cache's annotated tag dereferenced. No delta from P beyond step 8. `check.needs` is complete. No wheel substitution and no checkout import. Permissions equal P's. `check-clean` is last in all five recipe jobs. |

The triage subagent applied c1 and reran `just lint`, which exited 0. Nothing was
high, so there was no second round. Afterwards `just check` was rerun at `5b76af6`
(staged) and at `463076e`, as above.

### Handed back

- To T07 and T11: the repository is public and the Pages URL is
  `https://biscuitbin.github.io/alliumpy/` (`build_type: workflow`), for T07's
  `deploy-to-github-pages.md` and decision 0008.
- To T11: claim 11's private-repository deploy skip was not exercised, because the
  repository became public before `pages.yml` landed.
- Actions minutes: the repository is public, so standard runners are not metered
  (§13's concern applied to the private repository); the first full run reported
  `total_ms: 0` billable and 84 s wall-clock.
- To T14: the CI wheel is `manylinux_2_34`, the build runner's glibc; the release
  matrix decides the published floor.

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
- The final code review (`/code-review` at medium effort over `origin/main...HEAD`, at
  `da101b6`) found no correctness defect in the deltas. It raised seven points that lie
  in P's design, which step 8 carries "and nothing else", so they are recorded here for
  T11 and the maintainer instead of being changed:
  - `audit.yml` runs the full setup action (tool installs, hook clones, lychee) when
    `just audit` needs only cargo-deny and the lockfile, so unrelated fetches can fail
    it.
  - `check-toolchain` runs only in `rust`; `python` and `coverage` build on their own
    runners without that proof.
  - The setup action's "After this step no step reaches the network" holds for the gate
    recipes but not for `audit`'s RustSec fetch.
  - `py-test` and `py-stubtest` each run `py-develop`, so the `python` job runs
    `maturin develop` twice before the release build.
  - `snapshots-check` depends on `lock-check`, so `rust` runs it twice, and the nextest
    suite runs in both `rust` and `coverage`.
  - Seven rust-cache keys, three of them for jobs that compile nothing, share the
    repository's 10 GB cache.
  - Neither `upload-artifact` step sets `overwrite: true`, so a "re-run failed jobs" may
    conflict with the first attempt's artefact (unverified).
