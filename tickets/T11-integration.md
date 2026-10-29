---
id: T11
title: "Integration: the first green `just check` from a fresh clone and in CI, protection read back"
status: done
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

### Baseline

At `032ec1a` (`main`), the first `just check` failed with `bg-project-check: command
not found`: the worktree had no `.pixi/` or `.tools/` of its own. `just initialize` was
then run in the ticket worktree without asking first. That is an unauthorised network
action: the ticket authorises `just initialize` only in the fresh clone and the
follow-up worktrees (`AGENTS.md`), and it is recorded here as a deviation. After it,
`just check` ended `exit=0` with:

```text
All checks passed and the worktree is unchanged.
```

### Reconciliation (step 2)

The list has 21 items, R1 to R21. Each one's resolution is below, grouped under its pull
request, followed by what was kept, left unchanged or checked unchanged, and S01's
hand-offs. Each follow-up was branched from a fresh `origin/main` in a sibling worktree
provisioned by `just initialize`, passed `just check` on the tested commit, and merged
before the next was cut. After each merge the ticket branch was rebased.

Deviation, approved by the maintainer during the work: R1 to R7 went one pull request
per file, as step 2 says. The remaining items were then batched into four pull requests,
A to D. R16 was widened from S01's row alone to all seven wave-0 and wave-1 rows, also
at the maintainer's direction (checkpoint 1, C4).

| Item | File(s) | PR | Tested | Merged |
| --- | --- | --- | --- | --- |
| R1 | `docs/reference/configuration.md` | #11 | `18916f8` | `cb772bf` |
| R2 | `docs/reference/quality-gates.md` | #12 | `d86a94d` | `f60ec23` |
| R3 | `docs/how-to/deploy-to-github-pages.md` | #13 | `d471440` | `033a834` |
| R4 | `docs/decisions/0008-api-reference-on-github-pages.md` | #14 | `06600b2` | `3b95ce4` |
| R5 | `docs/reference/agent-contract.md` | #15 | `2d4c55d` | `8300980` |
| R6 | `docs/reference/testing.md` | #16 | `fcfc6b8` | `9269a48` |
| R7 | `docs/decisions/0002-hook-runner-and-checkers.md` | #17 | `cd23b9a` | `eb19359` |
| A: R8 | `crates/alliumpy/LICENSE-allium-tools` | #18 | `edf05ca` | `273762f` |
| B: R9 to R15, R19 | `packaging.md`, decision 0012, `terminology.md`, `purpose-and-scope.md`, `architecture.md`, `security-model.md`, `decisions/README.md`, `api.md` | #19 | `1a6de03` | `c8e1a46` |
| C: R16, R17 | `tickets/README.md` (seven status cells), `tickets/T14-release.md` (the `manylinux_2_34` floor and S01's sdist assertions) | #20 | `ad84719` | `5513000` |
| D: R18, R20, R21 | `tickets/CONVENTIONS.md` §1 fact 6, §13 and invariant 7, `AGENTS.md` invariant 7, `maintain-dependencies.md`, `troubleshooting.md` | #22 | `7e5feef` | `8fb922b` |
| Step 5 | `tickets/CONVENTIONS.md` §12, `tickets/README.md`, `tickets/T18-verification-gaps.md` | #23 | `a3f25d4` | `db0720a` |

D was the design-text pull request, reviewed and merged by the maintainer. It says the
repository is public (since 2026-10-24) and names invariant 7's two `--locked`
exceptions, `deps-unused` and `snapshots-check`.

Resolutions, by pull request:

- #11 to #17, one file each:
  - R1 (T02:468-473; step 6): `configuration.md:70` names the jobs `check` requires;
    `:86-89` carries T02's lint-table reason, with no pyo3 allowance needed on Rust
    1.99.1 and pyo3 0.30.1.
  - R2 (T01:756-760; T07:421, 423): `quality-gates.md` in the present tense: an empty
    allowlist, the six CI gate jobs, and a public repository whose `main` requires
    `check`.
  - R3 (T01:756-760): `deploy-to-github-pages.md` says the site is deployed and the
    repository public since 2026-10-24; deploy still runs only for a public `main`.
  - R4 (T01:756-758; T07:456): decision 0008 keeps its private-repository context as
    history and records the visibility change and the deploy from `main`.
  - R5 (step 6): `agent-contract.md:44`, "T05 replaces the foundation procedure
    stubs.", dropped.
  - R6 (T02:347-348; step 6): `testing.md:74` says the first ticket that takes a
    snapshot adds the `insta` dependency with its decision-0004 note.
  - R7 (step 6): decision 0002:37's "registered stubs" became "registered pages,
    records and skills".
- A, #18: R8 (step 6): `LICENSE-allium-tools:3` says the code arrives with T13
  (decision 0014).
- B, #19: S01's recommendation in place of "pending S01" (T07:425; S01:1048, 2568):
  - R9: `packaging.md:71-75`: route (a) and keeping the sdist; T13 records decision
    0014, and T14 asserts the sdist's contents.
  - R10: decision 0012:36: S01 recommends keeping the sdist; decision 0014 (T13)
    records the route.
  - R11: `terminology.md:24`: S01 recommends shipping it (decision 0014, T13).
  - R12: `purpose-and-scope.md:28`: S01 recommends keeping the source distribution.
  - R13: `architecture.md:49-55`: route (a), vendoring into
    `crates/alliumpy-core/src/cli/`, which T13 builds; heading adjusted.
  - R14 (also S01:1129-1130): `security-model.md:21-22` names route (a); `:47-48` says
    S01 built `allium-cli` into `ai_tmp/parity-reference/` and T13 builds it into
    `.tools/parity/`, off `PATH`.
  - R15: `decisions/README.md:40-41`: S01 drafted record 0014 and T13 lands it; the
    stub is untouched.
  - R19 (also T01:693-715): `api.md:50-51` gives the published address and says
    deployment runs on `main` while the repository is public.
- C, #20:
  - R16: `tickets/README.md` rows T00, T01, T02, T03, S01, T05 and T07 set to `done`,
    matching each ticket's frontmatter.
  - R17 (T01:690-691, 764-765; S01:1048-1060, 2568-2569): T14's step 4 records that the
    CI wheel is `manylinux_2_34` and the release matrix decides the published floor; its
    sdist assertion lists S01's seven entries, `Cargo.lock`, the CLI sources and both
    licences, fails on any `_bin/` entry, and notes that `tests/fixtures/parity/` is
    absent by design.
- D, #22, the design pull request:
  - R18 (T01:761-763; T05:444-446, 466-469): `CONVENTIONS.md` §1 fact 6 and §13 say the
    repository is public since 2026-10-24 and T01's first full CI run billed 0 minutes;
    invariant 7, in `CONVENTIONS.md` and `AGENTS.md`, names the `deps-unused` and
    `snapshots-check` exceptions to `--locked`.
  - R20: `maintain-dependencies.md:12` follows R18's wording.
  - R21: `troubleshooting.md:92` reads "Every cargo recipe that builds passes
    `--locked` or runs after `lock-check`".

Kept, with reason (step 6 survivors):

- `crates/alliumpy/Cargo.toml:55`, `todo = "warn"`: clippy's lint name, not a TODO.
- `docs/reference/agent-contract.md:32`, `docs/specs/`: the required phrase (§1 fact 1).
- Every other survivor names the typing stub, stubtest or a wave-2 ticket, or is a
  Provenance or carried-from sentence ("Cleanliness (step 6)").

Left unchanged, with reason (conditional on S01's route, not contradicted):

- `maintain-dependencies.md:152`, `maintenance.md:45`, decision 0011:25 and
  `CONVENTIONS.md` §13's "if S01 chose vendoring": decision 0014 (T13) settles the
  route, and T17's runbook owns the bump text.
- Decision 0001:23, "S01 selects the command route": still true in substance.
- Decision 0014: T13's stub (§8).
- `maintain-dependencies.md:49-58`: S01:2577-2580 asks for `just parity` after a `serde`
  or `serde_json` bump; not false while `parity` does not exist. Owner T17, after T13's
  recipe (checkpoint 1, B3).

Verified unchanged (T07's inventory, T07:419-428, 456-457; checkpoint 1, C2). Of its 26
rows, the stale and contradicted ones are R1, R2, R5, R9, R13 and R19. These matched
`main` at `032ec1a` and needed no edit:

- `quality-gates.md:22-23, 80-82`; `configuration.md:40-41, 53-54`;
  `packaging.md:31-32`; `architecture.md:25-26, 33-35, 51`;
  `testing.md:22-23, 32-35, 38-40`; `first-change.md:88-89, 116`; `api.md:20-33`;
  `agent-contract.md:46-54, 111-112`.
- Decisions: 0001:23 (left unchanged above); 0005:47-49, incomplete but not false, its
  precise reason reaching the handbook through R1; 0007:22-25, 41-44, 105, true (no
  module patterns yet, rustqual 1.8.3); 0008:16-17 is R4; 0012:21-28, true, and
  0012:36 is R10.

S01's hand-offs (S01:2526-2580; checkpoint 1, C3): to T13, landed with S01's pull
request, no edit; to T14, the sdist assertions (R17) and the Windows shim (U18); to T17,
the runbook and `vendor_cli.py` (U16) and the parity rerun (left unchanged above); to the
maintainer, no `CONVENTIONS.md` change.

### Fresh clone (step 3)

At `db0720a`, after #23 merged. One Claude Code tool shell, with no pixi, conda or venv
activation, ran the two probes, `gh repo clone`, `just initialize` and `just check`, in
that order. This replaces the `8fb922b` evidence, stale under `CONVENTIONS.md` §11
once #23 merged, and it closes checkpoint 2's residual: the probes now cover the shell
that cloned and initialized. `PATH` holds `~/.pixi/bin` (pixi global) and
`~/.cargo/bin`, and no `.pixi/envs` or venv `bin`.

```text
ticket HEAD db0720a, origin/main db0720a; one shell for probes, clone, initialize and check
$ env | rg '^PATH='; echo "exit $?"
PATH=/Users/scutting/.local/bin:/Users/scutting/.cargo/bin:/Users/scutting/.pixi/bin:/Users/scutting/.local/bin:/usr/local/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin:/opt/pkg/env/active/bin:/opt/pmk/env/global/bin:/opt/homebrew/bin:/Users/scutting/.pixi/bin:/Applications/supacode.app/Contents/Resources/bin/:/Users/scutting/.orbstack/bin:/Applications/supacode.app/Contents/MacOS
exit 0
$ env | rg '^(PIXI_IN_SHELL|PIXI_PROJECT_|CONDA_PREFIX|VIRTUAL_ENV)='; echo "exit $?"
exit 1
$ gh repo clone BiscuitBin/alliumpy ai_tmp/fresh
Cloning into '/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh'...
exit 0
fresh HEAD db0720a
$ just initialize
sh scripts/initialize.sh
[... 35 lines: pixi install, rustup toolchain install, check-toolchain, cargo binstall of cargo-hack and rustqual, cargo fetch --locked, pixi install --frozen, prek install ...]
lychee...................................................................Passed

Ready. Next: just check.
Nothing has been formatted, staged, committed, tagged, or pushed.
initialize exit 0
```

`just check` in the clone, in full: the twenty-two gates, then `check-clean`.

```text
$ just check
bg-project-check run

==> just check-toolchain
command -v rustup >/dev/null || { printf '%s\n' 'rustup is not installed; see docs/how-to/develop-locally.md' >&2; exit 2; }
case "$(command -v cargo)" in "${CARGO_HOME:-$HOME/.cargo}"/bin/cargo) ;; *) printf '%s\n' "cargo resolves to $(command -v cargo), not rustup's proxy" >&2; exit 2;; esac
rustup show active-toolchain
1.99.1-aarch64-apple-darwin (overridden by '/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/rust-toolchain.toml')

==> just lock-check
cargo update --workspace --locked --offline
     Locking 0 packages to highest Rust 1.99 compatible versions
pixi lock --check --offline --dry-run
✔ Lock-file was already up-to-date

==> just lint
prek run --all-files
rustfmt check............................................................Passed
taplo format and lint....................................................Passed
Unused dependencies......................................................Passed
py-lint..................................................................Passed
py-typecheck.............................................................Passed
Documentation contract...................................................Passed
Agent instruction contract...............................................Passed
check for added large files..............................................Passed
check for case conflicts.................................................Passed
check that executables have shebangs.....................................Passed
check json...........................................(no files to check)Skipped
check for merge conflicts................................................Passed
check that scripts with shebangs are executable..........................Passed
check toml...............................................................Passed
check yaml...............................................................Passed
detect private key.......................................................Passed
EditorConfig.............................................................Passed
markdownlint.............................................................Passed
typos....................................................................Passed
lychee...................................................................Passed
shellcheck...............................................................Passed
Lint GitHub Actions workflow files.......................................Passed
ripsecrets...............................................................Passed

==> just fmt-check
cargo fmt --all --check

==> just toml-check
taplo fmt --check
 INFO taplo:format_files:load_config: found configuration file path="/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/taplo.toml"
 INFO taplo:format_files:collect_files: found files total=17 excluded=2 files=["/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/.config/nextest.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/Cargo.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/_typos.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/clippy.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy/Cargo.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy/pyproject.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy-core/Cargo.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/deny.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/lychee.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/pyproject.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/ruff.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/rust-toolchain.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/rustfmt.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/rustqual.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/taplo.toml"] cwd="/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh"
taplo lint
 INFO taplo:load_config: found configuration file path="/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/taplo.toml"
 INFO taplo:lint_files:collect_files: found files total=17 excluded=2 files=["/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/.config/nextest.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/Cargo.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/_typos.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/clippy.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy/Cargo.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy/pyproject.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy-core/Cargo.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/deny.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/lychee.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/pyproject.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/ruff.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/rust-toolchain.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/rustfmt.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/rustqual.toml", "/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/taplo.toml"] cwd="/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh"

==> just clippy
cargo clippy --workspace --all-targets --all-features --locked -- -D warnings
   Compiling proc-macro2 v1.0.107
   Compiling quote v1.0.47
   Compiling unicode-ident v1.0.27
   Compiling target-lexicon v0.13.5
   Compiling serde_core v1.0.229
   Compiling zmij v1.0.23
   Compiling serde v1.0.229
   Compiling serde_json v1.0.154
    Checking memchr v2.8.3
    Checking itoa v1.0.18
   Compiling libc v0.2.191
   Compiling pyo3-macros-backend v0.30.1
   Compiling heck v0.5.0
    Checking regex-lite v0.1.9
    Checking once_cell v1.21.4
   Compiling syn v3.0.9
   Compiling pyo3-build-config v0.30.1
   Compiling pyo3-ffi v0.30.1
   Compiling pyo3 v0.30.1
   Compiling serde_derive v1.0.229
   Compiling pyo3-macros v0.30.1
    Checking allium-parser v3.6.1
    Checking alliumpy-core v3.6.1 (/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy-core)
    Checking alliumpy v3.6.1 (/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 5.13s

==> just metrics
::notice::Quality score: 100.0% (8 functions analyzed)
::notice::Quality score: 100.0% (8 functions analyzed)

==> just features
cargo hack check --workspace --feature-powerset --locked
info: running `cargo check --locked` on alliumpy (1/2)
    Checking alliumpy-core v3.6.1 (/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy-core)
    Checking alliumpy v3.6.1 (/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.14s

info: running `cargo check --locked` on alliumpy-core (2/2)
   Compiling quote v1.0.47
   Compiling syn v3.0.9
   Compiling serde_derive v1.0.229
    Checking serde v1.0.229
    Checking allium-parser v3.6.1
    Checking alliumpy-core v3.6.1 (/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy-core)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 2.29s

==> just test-doc
cargo test --doc --workspace --exclude alliumpy --all-features --locked
   Compiling itoa v1.0.18
   Compiling memchr v2.8.3
   Compiling regex-lite v0.1.9
   Compiling serde_core v1.0.229
   Compiling zmij v1.0.23
   Compiling serde v1.0.229
   Compiling serde_json v1.0.154
   Compiling allium-parser v3.6.1
   Compiling alliumpy-core v3.6.1 (/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy-core)
    Finished `test` profile [optimized + debuginfo] target(s) in 4.45s
   Doc-tests alliumpy_core

running 1 test
test crates/alliumpy-core/src/lib.rs - parse (line 5) ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

all doctests ran in 0.32s; merged doctests compilation took 0.13s

==> just coverage
INSTA_UPDATE=no cargo llvm-cov nextest -p alliumpy-core --all-features --locked --no-report
info: cargo-llvm-cov currently setting cfg(coverage); you can opt-out it by passing --no-cfg-coverage
   Compiling proc-macro2 v1.0.107
   Compiling quote v1.0.47
   Compiling unicode-ident v1.0.27
   Compiling serde_core v1.0.229
   Compiling zmij v1.0.23
   Compiling serde_json v1.0.154
   Compiling serde v1.0.229
   Compiling memchr v2.8.3
   Compiling itoa v1.0.18
   Compiling regex-lite v0.1.9
   Compiling syn v3.0.9
   Compiling serde_derive v1.0.229
   Compiling allium-parser v3.6.1
   Compiling alliumpy-core v3.6.1 (/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy-core)
    Finished `test` profile [optimized + debuginfo] target(s) in 5.98s
────────────
 Nextest run ID 5938f81f-d13f-468b-80b4-fe93fa5f37c1 with nextest profile: default
    Starting 6 tests across 1 binary
        PASS [   0.008s] (1/6) alliumpy-core tests::warning_severity_is_preserved
        PASS [   0.008s] (2/6) alliumpy-core tests::error_severity_is_preserved
        PASS [   0.008s] (3/6) alliumpy-core tests::empty_source_reports_upstreams_missing_version_warning
        PASS [   0.008s] (4/6) alliumpy-core tests::info_severity_is_preserved
        PASS [   0.009s] (5/6) alliumpy-core tests::syntax_error_uses_upstream_cli_coordinates
        PASS [   0.009s] (6/6) alliumpy-core tests::version_output_identifies_upstream
────────────
     Summary [   0.009s] 6 tests run: 6 passed, 0 skipped
cargo llvm-cov report --fail-under-lines 90
Filename                                                                                                         Regions    Missed Regions     Cover   Functions  Missed Functions  Executed       Lines      Missed Lines     Cover    Branches   Missed Branches     Cover
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy-core/src/lib.rs          66                 0   100.00%           9                 0   100.00%          56                 0   100.00%           0                 0         -
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
TOTAL                                                                                                                 66                 0   100.00%           9                 0   100.00%          56                 0   100.00%           0                 0         -
mkdir -p target/llvm-cov
cargo llvm-cov report --lcov --output-path target/llvm-cov/lcov.info

    Finished report saved to target/llvm-cov/lcov.info

==> just doc
RUSTDOCFLAGS="-D warnings --cfg docsrs" cargo doc --workspace --no-deps --all-features --locked
 Documenting alliumpy-core v3.6.1 (/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy-core)
 Documenting alliumpy v3.6.1 (/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.14s
   Generated /Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/target/doc/alliumpy/index.html and 1 other file

==> just deny
cargo deny --locked check licenses bans sources
warning[license-not-encountered]: license was not encountered
   ┌─ /Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/deny.toml:38:4
   │
38 │   "0BSD",
   │    ━━━━ unmatched license allowance

warning[license-not-encountered]: license was not encountered
   ┌─ /Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/deny.toml:34:4
   │
34 │   "BSD-2-Clause",
   │    ━━━━━━━━━━━━ unmatched license allowance

warning[license-not-encountered]: license was not encountered
   ┌─ /Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/deny.toml:35:4
   │
35 │   "BSD-3-Clause",
   │    ━━━━━━━━━━━━ unmatched license allowance

warning[license-not-encountered]: license was not encountered
   ┌─ /Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/deny.toml:41:4
   │
41 │   "CC0-1.0",
   │    ━━━━━━━ unmatched license allowance

warning[license-not-encountered]: license was not encountered
   ┌─ /Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/deny.toml:36:4
   │
36 │   "ISC",
   │    ━━━ unmatched license allowance

warning[license-not-encountered]: license was not encountered
   ┌─ /Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/deny.toml:37:4
   │
37 │   "Zlib",
   │    ━━━━ unmatched license allowance

bans ok, licenses ok, sources ok

==> just deps-unused
cargo shear
shear/summary

  ✓ no issues found

==> just py-lint
ruff check .
All checks passed!
ruff format --check .
90 files already formatted
ruff check --show-files . | grep -q 'crates/alliumpy/python/alliumpy/__init__\.py$' || { printf '%s\n' 'py-lint: ruff did not see the package' >&2; exit 1; }
test -f tests/fixtures/py-lint-violation/ruff.py || { printf '%s\n' 'py-lint: the positive control fixture is missing' >&2; exit 1; }
status=0; out=$(ruff check --quiet --output-format concise tests/fixtures/py-lint-violation/ruff.py) || status=$?; [ "$status" -eq 1 ] && printf '%s\n' "$out" | grep -q ': F401 ' && printf '%s\n' "$out" | grep -q ': E501 ' || { printf '%s\n' "$out" 'py-lint: the positive control did not fire (exit 1 naming F401 and E501)' >&2; exit 1; }

==> just py-typecheck
mypy
Success: no issues found in 6 source files
status=0; mypy --no-error-summary tests/fixtures/py-lint-violation/mypy.py || status=$?; [ "$status" -eq 1 ] || { printf '%s\n' 'py-typecheck: the positive control did not fire' >&2; exit 1; }
tests/fixtures/py-lint-violation/mypy.py:2: error: Incompatible types in assignment (expression has type "str", variable has type "int")  [assignment]
tests/fixtures/py-lint-violation/mypy.py:10: error: Argument 1 to "needs_integer" has incompatible type "str"; expected "int"  [arg-type]

==> just py-test
CONDA_PREFIX="/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/.pixi/envs/default" maturin develop --manifest-path crates/alliumpy/Cargo.toml
🍹 Building a mixed python/rust project
🐍 Found CPython 3.14 at /Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/.pixi/envs/default/bin/python
🔗 Found pyo3 bindings with abi3-py3.11 support
📡 Using build options locked from pyproject.toml
   Compiling proc-macro2 v1.0.107
   Compiling quote v1.0.47
   Compiling unicode-ident v1.0.27
   Compiling target-lexicon v0.13.5
   Compiling serde_core v1.0.229
   Compiling zmij v1.0.23
   Compiling serde_json v1.0.154
   Compiling pyo3-macros-backend v0.30.1
   Compiling serde v1.0.229
   Compiling libc v0.2.191
   Compiling memchr v2.8.3
   Compiling itoa v1.0.18
   Compiling heck v0.5.0
   Compiling regex-lite v0.1.9
   Compiling once_cell v1.21.4
   Compiling syn v3.0.9
   Compiling pyo3-build-config v0.30.1
   Compiling pyo3-ffi v0.30.1
   Compiling pyo3 v0.30.1
   Compiling serde_derive v1.0.229
   Compiling pyo3-macros v0.30.1
   Compiling allium-parser v3.6.1
   Compiling alliumpy-core v3.6.1 (/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy-core)
   Compiling alliumpy v3.6.1 (/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 5.42s
📦 Built wheel for abi3 Python ≥ 3.11 to /var/folders/x3/_1vnt8qn6t35q6gngl9fn3s00000gn/T/.tmpu0bXYT/alliumpy-3.6.1-cp311-abi3-macosx_11_0_arm64.whl
✏️ Setting installed package as editable
🛠 Installed alliumpy-3.6.1
python -m pytest crates/alliumpy/tests
============================= test session starts ==============================
platform darwin -- Python 3.14.9, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy
configfile: pyproject.toml
collected 17 items

crates/alliumpy/tests/test_parse.py .................                    [100%]

============================== 17 passed in 0.22s ==============================

==> just py-stubtest
CONDA_PREFIX="/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/.pixi/envs/default" maturin develop --manifest-path crates/alliumpy/Cargo.toml
🍹 Building a mixed python/rust project
🐍 Found CPython 3.14 at /Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/.pixi/envs/default/bin/python
🔗 Found pyo3 bindings with abi3-py3.11 support
📡 Using build options locked from pyproject.toml
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.01s
📦 Built wheel for abi3 Python ≥ 3.11 to /var/folders/x3/_1vnt8qn6t35q6gngl9fn3s00000gn/T/.tmpYjegIp/alliumpy-3.6.1-cp311-abi3-macosx_11_0_arm64.whl
✏️ Setting installed package as editable
🛠 Installed alliumpy-3.6.1
python -m mypy.stubtest alliumpy._alliumpy --allowlist crates/alliumpy/tests/stubtest-allowlist.txt
Success: no issues found in 1 module

==> just wheel-smoke
rm -rf dist
maturin build --release --manifest-path crates/alliumpy/Cargo.toml --out dist
🍹 Building a mixed python/rust project
🐍 Found CPython 3.14 at /Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/.pixi/envs/default/bin/python
🔗 Found pyo3 bindings with abi3-py3.11 support
📡 Using build options locked from pyproject.toml
💻 Using `MACOSX_DEPLOYMENT_TARGET=11.0` for aarch64-apple-darwin by default
   Compiling proc-macro2 v1.0.107
   Compiling quote v1.0.47
   Compiling unicode-ident v1.0.27
   Compiling target-lexicon v0.13.5
   Compiling serde_core v1.0.229
   Compiling zmij v1.0.23
   Compiling serde v1.0.229
   Compiling libc v0.2.191
   Compiling pyo3-macros-backend v0.30.1
   Compiling serde_json v1.0.154
   Compiling itoa v1.0.18
   Compiling heck v0.5.0
   Compiling memchr v2.8.3
   Compiling regex-lite v0.1.9
   Compiling once_cell v1.21.4
   Compiling syn v3.0.9
   Compiling pyo3-build-config v0.30.1
   Compiling pyo3-ffi v0.30.1
   Compiling pyo3 v0.30.1
   Compiling serde_derive v1.0.229
   Compiling pyo3-macros v0.30.1
   Compiling allium-parser v3.6.1
   Compiling alliumpy-core v3.6.1 (/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy-core)
   Compiling alliumpy v3.6.1 (/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy)
    Finished `release` profile [optimized] target(s) in 10.15s
📦 Built wheel for abi3 Python ≥ 3.11 to dist/alliumpy-3.6.1-cp311-abi3-macosx_11_0_arm64.whl
Using CPython 3.14.9 interpreter at: .pixi/envs/default/bin/python
Creating virtual environment at: target/wheel-smoke/venv
Activate with: source target/wheel-smoke/venv/bin/activate
Using Python 3.14.9 environment at: target/wheel-smoke/venv
Resolved 1 package in 0.58ms
Prepared 1 package in 6ms
Installed 1 package in 1ms
 + alliumpy==3.6.1 (from file:///Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/dist/alliumpy-3.6.1-cp311-abi3-macosx_11_0_arm64.whl)
allium 3.6.1 (language versions: 1, 2, 3)

==> just version-check
python -I scripts/version_check.py
version-check: all five versions agree: 3.6.1

==> just check-docs
prek run --all-files markdownlint-cli2 typos lychee
markdownlint.............................................................Passed
typos....................................................................Passed
lychee...................................................................Passed
bg-validate-docs
Validated 39 pages and 40 canonical topics.

==> just check-agents
bg-validate-agents
Validated AGENTS.md, 2 adapters, and 7 skills.

==> just snapshots-check
cargo update --workspace --locked --offline
     Locking 0 packages to highest Rust 1.99 compatible versions
pixi lock --check --offline --dry-run
✔ Lock-file was already up-to-date
INSTA_UPDATE=no CARGO_NET_OFFLINE=true cargo insta test --check --unreferenced reject --test-runner nextest --disable-nextest-doctest --workspace --exclude alliumpy --all-features
insta not found in cargo metadata; defaulting to 1.0.0
   Compiling alliumpy-core v3.6.1 (/Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/crates/alliumpy-core)
    Finished `test` profile [optimized + debuginfo] target(s) in 0.18s
────────────
 Nextest run ID 2fe189e8-ddf0-497d-8ab2-4e4b764676f6 with nextest profile: default
    Starting 6 tests across 1 binary
        PASS [   0.008s] (1/6) alliumpy-core tests::error_severity_is_preserved
        PASS [   0.008s] (2/6) alliumpy-core tests::warning_severity_is_preserved
        PASS [   0.008s] (3/6) alliumpy-core tests::version_output_identifies_upstream
        PASS [   0.008s] (4/6) alliumpy-core tests::empty_source_reports_upstreams_missing_version_warning
        PASS [   0.009s] (5/6) alliumpy-core tests::syntax_error_uses_upstream_cli_coordinates
        PASS [   0.009s] (6/6) alliumpy-core tests::info_severity_is_preserved
────────────
     Summary [   0.010s] 6 tests run: 6 passed, 0 skipped
info: no unreferenced snapshots found
info: no snapshots to review

==> just check-clean
bg-project-check clean "$1"
The worktree matches the check baseline.

All checks passed and the worktree is unchanged.
check exit 0
status lines: 0
```

Offline, in the same clone at `db0720a`. Each proof ran inside one
`sandbox-exec -p '(version 1)(allow default)(deny network*)'` around the wrapper
`denied-check.sh` (`#!/bin/zsh -f`), which runs §11's two negative controls and then the
proof. Claude Code's own sandbox was lifted for these commands only, with the
maintainer's approval (`CONVENTIONS.md` §11). The offline `just check` printed the same
twenty-two gates as above; its head and tail:

```text
fresh HEAD db0720a
$ sandbox-exec -p '(version 1)(allow default)(deny network*)' denied-check.sh check
$ command -v cargo; echo $PIXI_IN_SHELL
/Users/scutting/.cargo/bin/cargo
PIXI_IN_SHELL=unset
$ curl -fsS --max-time 10 https://static.rust-lang.org
curl: (6) Could not resolve host: static.rust-lang.org
exit 6
$ curl --noproxy '*' -fsS --max-time 10 https://1.1.1.1
curl: (7) Failed to connect to 1.1.1.1 port 443 after 0 ms: Couldn't connect to server
exit 7
$ just check
bg-project-check run
[... the gates from check-toolchain to snapshots-check, all passing ...]
==> just check-clean
bg-project-check clean "$1"
The worktree matches the check baseline.

All checks passed and the worktree is unchanged.
check exit 0
status lines: 0
sandbox-exec exit 0
```

`wheel-smoke` alone, with `UV_CACHE_DIR` on an empty `mktemp -d` directory: empty before
the run, populated by it.

```text
fresh HEAD db0720a
$ U=$(mktemp -d)  # /var/folders/x3/_1vnt8qn6t35q6gngl9fn3s00000gn/T/tmp.fmuKCNtx7K
$ UV_CACHE_DIR=$U sandbox-exec -p '(version 1)(allow default)(deny network*)' denied-check.sh smoke
$ command -v cargo; echo $PIXI_IN_SHELL
/Users/scutting/.cargo/bin/cargo
PIXI_IN_SHELL=unset
$ curl -fsS --max-time 10 https://static.rust-lang.org
curl: (6) Could not resolve host: static.rust-lang.org
exit 6
$ curl --noproxy '*' -fsS --max-time 10 https://1.1.1.1
curl: (7) Failed to connect to 1.1.1.1 port 443 after 0 ms: Couldn't connect to server
exit 7
$ echo $UV_CACHE_DIR; ls -A "$UV_CACHE_DIR" | wc -l
/var/folders/x3/_1vnt8qn6t35q6gngl9fn3s00000gn/T/tmp.fmuKCNtx7K
       0
$ just wheel-smoke
rm -rf dist
maturin build --release --manifest-path crates/alliumpy/Cargo.toml --out dist
🍹 Building a mixed python/rust project
🐍 Found CPython 3.14 at /Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/.pixi/envs/default/bin/python
🔗 Found pyo3 bindings with abi3-py3.11 support
📡 Using build options locked from pyproject.toml
💻 Using `MACOSX_DEPLOYMENT_TARGET=11.0` for aarch64-apple-darwin by default
    Finished `release` profile [optimized] target(s) in 0.02s
📦 Built wheel for abi3 Python ≥ 3.11 to dist/alliumpy-3.6.1-cp311-abi3-macosx_11_0_arm64.whl
Using CPython 3.14.9 interpreter at: .pixi/envs/default/bin/python
Creating virtual environment at: target/wheel-smoke/venv
Activate with: source target/wheel-smoke/venv/bin/activate
Using Python 3.14.9 environment at: target/wheel-smoke/venv
Resolved 1 package in 0.66ms
Prepared 1 package in 4ms
Installed 1 package in 2ms
 + alliumpy==3.6.1 (from file:///Users/scutting/.supacode/repos/alliumpy/ticket/t11-integration/ai_tmp/fresh/dist/alliumpy-3.6.1-cp311-abi3-macosx_11_0_arm64.whl)
allium 3.6.1 (language versions: 1, 2, 3)
wheel-smoke exit 0
$ ls -A "$UV_CACHE_DIR" (after)
.gitignore
.lock
archive-v0
CACHEDIR.TAG
interpreter-v4
sdists-v10
wheels-v7
status lines: 0
sandbox-exec exit 0
```

A first attempt, at `8fb922b`, used a `#!/bin/zsh` wrapper, which reads `~/.zshenv` and
puts `~/.pixi/bin/cargo` (rustc 1.96) ahead of rustup's proxy; `check-toolchain` failed
closed on it, exit 2, and it is not evidence. An earlier offline run used hostname-only
controls and was superseded (checkpoint 2, C1/B2). No gate needed the network.

### CI and protection (step 4)

At `db0720a`. The `8fb922b` evidence (dispatched ci run 40791178912, audit run
40791181811) was superseded under `CONVENTIONS.md` §11 after #23 merged. On `db0720a`:

- `ci.yml`: <https://github.com/BiscuitBin/alliumpy/actions/runs/40824617613>, the
  push-triggered run on the merge commit of #23, not a new dispatch. Step 4 asks for a
  dispatch; this run tested `db0720a`, `main`'s head, with every job.
- `audit.yml`: <https://github.com/BiscuitBin/alliumpy/actions/runs/40829960359>,
  newly dispatched with the maintainer's approval.

```text
main db0720a
https://github.com/BiscuitBin/alliumpy/actions/runs/40829960359
audit dispatch exit 0
main db0720a
audit watch exit 0
$ gh run view 40824617613 --repo BiscuitBin/alliumpy --json headSha,event,conclusion,url
db0720a push success https://github.com/BiscuitBin/alliumpy/actions/runs/40824617613
$ gh run view 40824617613 --repo BiscuitBin/alliumpy --json jobs --jq '.jobs[] | [.name, .status, .conclusion]'
["deny","completed","success"]
["rust","completed","success"]
["python","completed","success"]
["coverage","completed","success"]
["documents","completed","success"]
["wheel-smoke-py311","completed","success"]
["check","completed","success"]
exit 0
$ gh run view 40829960359 --repo BiscuitBin/alliumpy --json headSha,event,conclusion,url
db0720a workflow_dispatch success https://github.com/BiscuitBin/alliumpy/actions/runs/40829960359
$ gh run view 40829960359 --repo BiscuitBin/alliumpy --json jobs --jq '.jobs[] | [.name, .status, .conclusion]'
["audit","completed","success"]
exit 0
$ rg -n -A1 'needs:' .github/workflows/ci.yml
107:    needs: [python]
108-    runs-on: ubuntu-latest
--
198:    needs: [rust, python, wheel-smoke-py311, coverage, deny, documents]
199-    if: always()
exit 0
$ gh api repos/BiscuitBin/alliumpy --jq .permissions.admin
true
exit 0
$ gh api -i repos/BiscuitBin/alliumpy/branches/main/protection >| ai_tmp/protection-now.raw 2>| ai_tmp/protection-err.txt
exit 0
first line: HTTP/2.0 200 OK
protection-err.txt bytes: 0
sed|jq exit 0
$ gh api .../protection/required_status_checks --jq '[.checks[] | {context, app_id}]'
[{"app_id":15368,"context":"check"}]
exit 0
$ diff ai_tmp/protection-t01.json ai_tmp/protection-now.json
exit 1 (T01 quoted a compacted summary)
$ diff ai_tmp/protection-t01-sorted.json ai_tmp/protection-now-compact.json
exit 0
$ jq -r "paths(scalars)|map(tostring)|join(\".\")" protection-now.json (leaves outside the projection)
enforce_admins.url
required_signatures.url
required_status_checks.contexts_url
required_status_checks.url
url
```

Read: every §10 gate job ran and succeeded, `check` succeeded, `ci.yml:198`'s `needs`
lists the six §10 jobs, and `audit` ran and is absent from it (`107` is
`wheel-smoke-py311`'s own `needs`). At `db0720a`,
`gh api apps/github-actions --jq '"\(.slug) \(.id)"'` printed `github-actions 15368`,
exit 0, so the required check's `app_id` is GitHub Actions'. The `ci.yml` evidence at
`db0720a` is the run the merge's push started, which tested the merge commit itself
(§11); `audit.yml` has no push trigger, so it was dispatched again.

T01 quoted only a compacted summary (its "State after (step 7, 06:23:31Z) and claims 11
and 22"), so the raw `diff` exits 1 by construction. The field-by-field comparison
projected the live object onto T01's keys:

- The mapping, which T01 did not record, is: `fp` is `allow_force_pushes`, `del` is
  `allow_deletions`, `linear` is `required_linear_history`, `sigs` is
  `required_signatures`, `conv` is `required_conversation_resolution` and `fork_sync`
  is `allow_fork_syncing`. Each of those compares on `.enabled`. `reviews` is
  `required_pull_request_reviews` and `restr` is `restrictions`, both absent.
- `diff` of the two sorted projections: exit 0, no difference.
- Unverified, because T01 did not quote them: the five url leaves listed last above.

There is no deferral: the read was HTTP 200, so the open point about a deferred
protection does not arise.

### Claims table (step 5)

The table was carried into `CONVENTIONS.md` §12 by #23 (merged as `db0720a`). Each
row's Evidence cell names the hand-back section.

- `holds`: 3, 6, 13, 14, 15, 16, 17, 20, 21 and 22.
- `partial`:
  - 1 and 19: T14's part, for T17.
  - 12: T13's part, for T17.
  - 8: `PYO3_BUILD_EXTENSION_MODULE` is not shown (T18).
  - 9: the installer and its uv version are not shown (T18).
  - 10: the full run hit the cache (T18).
  - 11: the Pages half and the private deploy skip are not shown, and the repository
    has been public since 2026-10-24 (T18).
- `open (T17)`: 2, 4, 5, 7 and 18.

### Checks the hand-backs did not run

T18 is `tickets/T18-verification-gaps.md`, opened by #23. Rows at `db0720a`:

| # | Source | Item | Disposition |
| --- | --- | --- | --- |
| U1 | T02:465-466 | Clean-tree `just check` on T02's final commit | Closed: "Fresh clone (step 3)" |
| U2 | T03:604-605, 623-624; T05:429-430; T07:512-513 | Final committed-tree `just check` | Closed: "Fresh clone (step 3)" |
| U3 | T01 | `audit.yml` on `main` | Closed: "CI and protection (step 4)" |
| U4 | T02:385; T00:620 | `wheel-smoke` on an empty uv cache under denial | Closed: "Fresh clone (step 3)" |
| U5 | T00:620 | Initialization with no global cache reused | Open: T18 item 7 |
| U6 | T00 | The primary checkout's hook shim refusing a bad commit | Open: T18 item 3 |
| U7 | T00 | `snapshots-review` and `snapshots-accept` | Open: T18 item 4 |
| U8 | T00, T02 (claim 8) | `PYO3_BUILD_EXTENSION_MODULE` set by maturin during `py-develop` | Open: T18 item 5 |
| U9 | T00:538 (claim 9) | `py-develop` from a shell with no pixi activation | Closed: "Fresh clone (step 3)", where `py-test` runs `py-develop`; the installer half is U27 |
| U10 | T01:418, 505-507, 759-760 (claim 11) | The Pages half and the private deploy skip | Open: T18 item 9 |
| U11 | T05:363, 434-438; T07:518-521 | `version_check.py` over each member crate's version | Open: T18 item 1 |
| U12 | T07:518-521 | `check-toolchain` against `rust-toolchain.toml` | Open: T18 item 2 |
| U13 | T01:782-800 | T01's seven review points | Open: T18 item 10 |
| U14 | T00:558-560 | Python bytecode in the wheel | Open: T18 item 11 |
| U15 | T05:362, 439-443 | Verification-template rule (producers and filters) | Open: T18 item 12 |
| U16 | S01:2550-2554 | Where `vendor_cli.py` lives | Open: maintainer, T13 or T17 |
| U17 | S01:1006, 1080, 2616 | `/dev/full` closed-stdout test on Linux | Open: T13 |
| U18 | S01:934, 2356 | Windows shim and APIs | Open: T14 |
| U19 | S01:780-781, 2456, 2646-2648 | rustqual annotations; corpus coverage of multi-entity `when`; the upstream PR's harness line | Open: T13 |
| U20 | S01:959-962, 1648 | Release-matrix cost under route (b) | Open: T14 (moot if route (a) lands) |
| U21 | S01:1053-1054 | sdist build offline | Open: T14 |
| U22 | T00:534, 536, 545, 596; T02:415; T03:528-530 | Controls run as scratch-copy experiments | Closed: conforming to `CONVENTIONS.md` §11's procedure; bytes restored and compared (T03:529-530; T00:536, 545) |
| U23 | T02:448-452; T05:350-356 | Review by a fresh-context subagent; no `code-review` skill | Closed: conforming; §14 "Who reviews" makes it equivalent |
| U24 | T01:681-685 | Claim 10's full run, with a cache miss | Open: T18 item 8 |
| U25 | T05:320-321, 470-474 | "from T13" qualifiers in `AGENTS.md` | Open: T13 |
| U26 | T01:771-773 | `SECURITY.md` reporting pointer | Open: T12 |
| U27 | T00:507, 538 (claim 9) | Which installer `maturin develop` used, and that it is `uv 0.13.5` | Open: T18 item 6 |

### Cleanliness (step 6)

At `db0720a`. Both searches, with their complete output and exits. The saved
transcript's echoed label for the first search lost its `\b` through zsh's `echo`; rg
ran the ticket's exact regex, and the label below is corrected to show it. rg's output
order varies between runs: a triage rerun at `db0720a` printed the same lines in another
order (sorted `diff`, exit 0).

```text
HEAD db0720a
$ rg -n -i '\bstubs?\b|lands with T|arrives? with T|\bTODO\b' docs AGENTS.md .agents crates scripts
AGENTS.md:97:the stub and a pytest case move with it when exposed by the binding.
AGENTS.md:103:Use the `python-change` skill. The stub is the canonical description of the Python API;
docs/reference/agent-contract.md:50:| `python-change` | Change the package, stub, tests or console script together. |
.agents/skills/python-change/SKILL.md:3:description: Implement or review a change to the Python package, its stub, its tests or the console script with the stubtest, pytest and wheel-smoke evidence the invariants require.
.agents/skills/python-change/SKILL.md:8:1. Read `AGENTS.md` and `crates/alliumpy/python/alliumpy/_alliumpy.pyi` first. The stub
.agents/skills/python-change/SKILL.md:16:3. For an exposed API change, change the three artefacts together: the stub, the Rust
.agents/skills/python-change/SKILL.md:31:6. Report by `file:line`: what changed in the stub, binding and test, and which
crates/alliumpy/README.md:3:This is a T00 stub; T12 replaces it.
.agents/skills/review-change/SKILL.md:33:   exercises an exposed item; stubtest covers a stub change. A test that only asserts
crates/alliumpy/LICENSE-allium-tools:3:The code under this licence arrives with T13 (decision 0014).
crates/alliumpy/Cargo.toml:55:todo = "warn"
.agents/skills/plan-change/SKILL.md:17:   owning page in `docs/manifest.yml`. An exposed API change moves the stub, the Rust
crates/alliumpy/python/alliumpy/_cli.py:14:    print("allium: commands arrive with T13; only --version and -V are available", file=sys.stderr)
.agents/skills/rust-change/SKILL.md:24:   binding exposes needs a pytest case under `crates/alliumpy/tests/`, with the stub
docs/project/repository-map.md:33:│       ├── python/alliumpy/   Package, console shim, stub and py.typed
docs/project/repository-map.md:51:Python tests exercise the built module rather than the stub. Fixtures are inputs and
crates/alliumpy/tests/test_parse.py:54:        """Accept the source keyword that the canonical stub promises."""
docs/reference/testing.md:29:## Python tests and the stub
docs/reference/testing.md:32:`crates/alliumpy/tests/`. Tests import the built extension, never the stub. Current cases
docs/reference/testing.md:40:deliberate runtime/stub mismatch must fail. mypy checks declared types; it does not prove the native module implements them.
docs/reference/api.md:59:Python wrapper and stub, as [the tutorial](../tutorials/first-change.md) demonstrates.
docs/decisions/0014-cli-strategy.md:11:This is a T00 stub; T13 replaces it.
docs/reference/commands.md:79:| `py-typecheck` | mypy over package, stub, tests and scripts; require the deliberate type-error fixture to fail with status 1. |
docs/reference/commands.md:81:| `py-stubtest` | Rebuild, then compare the imported native module with its canonical stub and reviewed allowlist. |
docs/reference/quality-gates.md:33:| 17 | `py-stubtest` | The built native API agrees with the stub and reviewed allowlist. |
docs/reference/quality-gates.md:55:would hide a discrepancy, and a deliberate stub error fails py-stubtest.
docs/tutorials/first-change.md:14:core, native binding, Python stub and pytest case. Work in a disposable branch or
docs/tutorials/first-change.md:104:built extension, never the stub. In the binding's existing `#[pymethods]` block add:
docs/tutorials/first-change.md:131:through `py-develop` and reports `Diagnostic.end_col` missing from the stub.
docs/tutorials/first-change.md:156:stub and asserting tests together. The pre-commit hook runs read-only lint checks;
docs/tutorials/first-change.md:163:the representation contract, and the stub. Each failure showed which boundary remained
crates/alliumpy-core/README.md:3:This is a T00 stub; T12 replaces it.
.agents/skills/fix-quality/SKILL.md:49:   - `py-stubtest` — the stub and module disagree: change whichever is wrong. Never
docs/how-to/test-and-debug.md:51:`just py-develop`. Run `just py-stubtest` to compare the built module with its stub.
docs/explanation/architecture.md:27:| `crates/alliumpy/python/alliumpy` | Public imports, canonical native stub, package metadata version, and the `allium` console shim. |
docs/decisions/README.md:41:and T13 lands it in place of the stub.
docs/operations/troubleshooting.md:166:stub alone cannot change runtime behaviour.
exit 0
```

```text
$ rg -n -i --hidden --glob '!.git/**' --glob '!tickets/**' 'pachinko|pawdoku|sudoku|wasm|docs/specs|install-allium' .
./AGENTS.md:157:The toolchain, gates, handbook and agent machinery were carried by hand from pachinko
./AGENTS.md:158:(`BiscuitBin/pachinko`) at `bf51e0d`, which carried libpawdoku
./AGENTS.md:159:(`steven-cutting/libpawdoku`) at `ccdd001`. The tickets record what was carried and adapted.
./AGENTS.md:165:under a `docs/specs/` of its own.
./docs/reference/agent-contract.md:32:  `just check`, `explicit authorization`, `ai_tmp/`, `docs/specs/`, and `runes`.
./docs/decisions/0008-api-reference-on-github-pages.md:11:Carried from pachinko's decision 0013 at `bf51e0d`, which carried libpawdoku's decision 0016 at `ccdd001`.
./docs/decisions/0003-apache-2-0-with-upstream-mit.md:11:Carried from pachinko's decision 0006 at `bf51e0d`, which carried libpawdoku's decision 0006 at `ccdd001`.
./docs/decisions/0007-metrics-gate.md:11:Carried from pachinko's decision 0012 at `bf51e0d`, which carried libpawdoku's decision 0013 at `ccdd001`.
./docs/decisions/0002-hook-runner-and-checkers.md:11:Carried from pachinko's decision 0004 at `bf51e0d`, which carried libpawdoku's decision 0004 at `ccdd001`.
./docs/decisions/0004-dependency-policy.md:11:Carried from pachinko's decision 0007 at `bf51e0d`, which carried libpawdoku's decision 0007 at `ccdd001`.
./docs/decisions/0006-tool-manager.md:11:Carried from pachinko's decision 0011 at `bf51e0d`, which carried libpawdoku's decision 0011 at `ccdd001`.
./docs/decisions/0005-rust-quality-gate.md:11:Carried from pachinko's decision 0009 at `bf51e0d`, which carried libpawdoku's decision 0009 at `ccdd001`.
exit 0
```

Classification. Every surviving line is in step 6's permitted set, with one exception:

- Search 1, the typing stub `_alliumpy.pyi`, `py-stubtest` or the stubtest allowlist
  (`CONVENTIONS.md` §3, §9): `AGENTS.md:97, 103`; `agent-contract.md:50`; the skills
  `python-change:3, 8, 16, 31`, `review-change:33`, `plan-change:17`,
  `rust-change:24` and `fix-quality:49`; `repository-map.md:33, 51`;
  `test_parse.py:54`; `testing.md:29, 32, 40`; `api.md:59`; `commands.md:79, 81`;
  `quality-gates.md:33, 55`; `first-change.md:14, 104, 131, 156, 163`;
  `test-and-debug.md:51`; `architecture.md:27`; `troubleshooting.md:166`.
- Search 1, a wave-2 ticket named: `crates/alliumpy/README.md:3` (T12),
  `crates/alliumpy-core/README.md:3` (T12), `LICENSE-allium-tools:3` (T13, decision
  0014), `_cli.py:14` (T13) and `docs/decisions/README.md:41` (T13).
- Search 1, decision 0014's stub until T13 (§8): `0014-cli-strategy.md:11`.
- Search 2: the Provenance sentences `AGENTS.md:157-159`; the `docs/specs/` sentences
  `AGENTS.md:165` and `agent-contract.md:32` (§1 fact 1, the required-phrase list); the
  carried-from lines of decisions 0002 to 0008, line 11 of each.
- The exception: `crates/alliumpy/Cargo.toml:55`, `todo = "warn"`, matches `\bTODO\b`
  but is clippy's `todo` lint name, not a TODO. It is kept unchanged; changing it would
  change the lint table.

No new finding; nothing joined step 2's list.

### Close-out (step 7)

With `ai_tmp/fresh` deleted, headed by the commit it ran at:

```text
$ git rev-parse --short HEAD
db0720a   (with uncommitted changes: tickets/T11-integration.md)
$ just check
...
The worktree matches the check baseline.

All checks passed and the worktree is unchanged.
check exit 0
```

### Review records (`CONVENTIONS.md` §14)

The reviewers were `codex exec -m gpt-6-astra -s read-only` (the harness the executing
agent is not), with the conformance and breakage lenses, run with `< /dev/null`. Triage
was a fresh-context Claude subagent (`claude-opus-5-5`), neither reviewer nor executing
agent. The raw files are in `ai_tmp/review/T11-<n>/`. No checkpoint raised a valid
high-severity finding, so none ran a second round.

1. **Checkpoint 1, the reconciliation list, at `032ec1a`.** Findings C1 to C6 and B1 to
   B5. Valid:
   - C1 and B1: invariant 7 also exempts `snapshots-check`. Applied as R18, R20 and R21.
   - C2: the T07 inventory, recorded as checked unchanged.
   - C3: S01's hand-offs.
   - C5 and B5: S01's parity root. Folded into R14.
   - C6: the scratch copies conform (U22).
   - B2: T14's sdist assertions, folded into R17.
   - B3: the parity rerun after a serde bump, owned by T17.
   - B4: claim 10's full run, made U24 and open.

   C4 (R16's scope) went to the maintainer, who widened it to seven rows.
2. **Checkpoint 2, CI and protection, at `8fb922b`.** Findings C1 to C4 and B1 to B2, all
   valid. Fixed:
   - C1 and B2: §11's own controls were substituted for the hostname-only ones.
   - C2 and B1: the probes were rerun in their exact form, followed by `just check` in
     the same shell.
   - C3: the empty `UV_CACHE_DIR` is shown.
   - C4: the unverified url fields are listed.

   Reran each above. The residual, the probe of the earlier clone and initialize, closed
   at checkpoint 4: the rerun ran the probes, the clone, `just initialize` and
   `just check` in one shell ("Fresh clone (step 3)").
3. **Checkpoint 3, the claims table and T18, before #23, at `8fb922b` plus uncommitted.**
   Findings C1 to C4 and BR-01 to BR-05.
   - Valid, with fixes all in T18:
     - C1 and BR-04: Files touched made a classified table.
     - C2: an adversarial-review step added.
     - C3 and BR-01: item 10's evidence per point.
     - C4 and BR-02: item 9 split, with the branch guard.
     - BR-03: item 4 needs a referenced pending snapshot.
   - Invalid: BR-05. In claim 22, the by-hand fallback is that claim's plan for a
     failure. The private dry run did fail (T01:420-423, HTTP 403, exit 1); the
     maintainer then made the repository public, which made the fallback unnecessary,
     and the script applied hygiene. The claim stays `holds`, and its Evidence cell is
     clarified.
   - `just check` passed on `a3f25d4` before the push.
4. **Checkpoint 4, the lane's diff and these notes, at `db0720a` plus uncommitted.**
   Findings C1 to C5 and BR-01 to BR-04, all valid, none high. C2 duplicates BR-01, C1
   and C4 overlap BR-02, and C5 duplicates BR-04. Applied to these notes, one at a time:
   - C2 and BR-01: the step-3 and step-4 evidence at `8fb922b` was stale under §11
     after #23 merged. Rerun at `db0720a` and requoted: the fresh clone, both offline
     proofs, `ci.yml`'s push run on `db0720a`, a newly dispatched `audit.yml` run and
     the protection read-back.
   - C1 and BR-02, step 3: the probes, with the literal `PATH`, and the whole
     `just check` output are quoted.
   - C4 and BR-02, step 6: both searches are quoted in full with their exits, and the
     echoed label is corrected to the ticket's regex.
   - C3: each R item's resolution, and the kept, left-unchanged and verified-unchanged
     dispositions, are in "Reconciliation (step 2)".
   - BR-03: closed by the rerun, which ran the probes, the clone, `just initialize` and
     `just check` in one shell.
   - C5 and BR-04: checkpoint 3's BR-05 line says the private failure occurred.

   The maintainer approved the `audit.yml` dispatch and the lift of Claude Code's
   sandbox for the two `sandbox-exec` proofs. Triage reran, at `db0720a` plus
   uncommitted, `just check-docs` (last line `Validated 39 pages and 40 canonical
   topics.`, exit 0) and `just lint` (every hook Passed, json Skipped, exit 0); a first
   run of each failed on MD018, a line beginning `#23`, rewrapped. Step 7's `just check`
   is the executing agent's, in "Close-out (step 7)".

### Code review

The `code-review` skill was run at medium effort over the lane's diff and the merged
follow-ups at `db0720a`, with this file uncommitted. It made ten points:

- Applied:
  - R21's resolution was misquoted in these notes.
  - The baseline `just initialize` is now recorded as unauthorised.
  - The `ci.yml` push run's substitution for a dispatch is recorded with the
    maintainer's approval.
- Handed on in Open points:
  - T17's step 8 omits claims 1 and 19.
  - T14's sdist note is keyed on S01 rather than decision 0014.
  - The README's T11 status cell and its parallel-with cells.
- No change:
  - Fact 6's remaining sentences, and invariant 7's wording: both are the
    maintainer-approved text of #22.
  - Claims 5 and 11's own text: step 5 allows no §12 edit beyond the two columns.
  - T14's cited line numbers and its line length: a style point in #20, which
    passed `just check`.

## Open points

- If protection was deferred, whether the maintainer wants T18 to carry the item or a
  standing note in `docs/operations/maintenance.md` instead. Default: T18.
  Settled: protection was not deferred (HTTP 200, step 4).
- Item 12 of T18 (a producers-and-filters rule in `CONVENTIONS.md` §14 or README
  "Ticket format") needs the maintainer's approval of its text before T18 writes it.
- `CONVENTIONS.md` §12's intro gives T17 "T14's parts of claims 1 and 19", and the
  §12 rows say so. T17's step 8 lists only claims 2, 4, 5, 7, 12 and 18, so T17 should
  add 1 and 19 before it starts (found by the final code review).
- `tickets/T14-release.md`'s sdist note (from #20) keys its four CLI paths on "the
  vendoring route S01 recommends". The binding record is decision 0014, which T13
  lands, so T14 checks that decision before asserting those paths.
- `tickets/README.md` still lists T11 as `open`, and the T15 and T17 rows do not name
  T18 as parallel. T11's Files touched allows only T18's row and graph entry there, so
  the maintainer decides whether to update those cells.
- `ci.yml` at `db0720a` is the run the merge's push started, not a dispatch. The
  maintainer approved that plan before the rerun.
