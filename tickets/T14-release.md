---
id: T14
title: "Release: the rehearsed matrix, `release-pypi.yml` by trusted publishing, `alliumpy 3.6.1` on PyPI"
status: open
depends_on: [T12]
parallel_with: [T15]
branch: ticket/t14-release
estimated_size: L
---

# T14: Release: the rehearsed matrix, `release-pypi.yml` by trusted publishing, `alliumpy 3.6.1` on PyPI

## Context

This repository publishes one wheel to PyPI and nothing to crates.io (`CONVENTIONS.md`
§0, §1 decision 2). Its release is therefore not P's: P's T14 (P `tickets/T14-release.md`)
is built on cargo-release, per-crate tags and a GitHub Release, and only its shape
carries: a release branch, a pull request that requires `check`, an annotated tag on the
merge commit, a workflow the tag starts, a `release` environment with a required
reviewer, and each step separately authorised. L's two spikes hold the rest. L
`tickets/S02-release-and-publishing.md` lines 648-866 is the branch, pull request and tag
flow and the two guards, and the `verify`-then-publish split is P `tickets/T14-release.md`
step 5; L `tickets/S04-bindings-and-cli.md` lines 299-440 (question (a); its
`generate-ci` bullet is lines 370-395) is what `maturin generate-ci github` emits (the
`linux`, `musllinux`, `windows`, `macos`, `sdist` and `release` jobs, the abi3 `cp314t`
step, `actions/attest`, `uv publish --trusted-publishing always` under
`[tool.maturin.generate-ci.github]`, and PyPI pending publishers), and lines 1563-1680 is
the drafted edit of that output into a house workflow. Read all three ranges first, then
`CONVENTIONS.md` §9 ("The two manifests", "The sdist", "The release matrix versus the
gate", "Licences"), §10, §11 and §12 claims 1, 2, 4, 5, 7, 18 and 19. L verified the
generator on maturin 1.15.0, which is still the pin (`CONVENTIONS.md` §2); a flag or
runner label this ticket needs that L did not verify is a check in Steps, never an
assumption.

The version policy is decision 4 (`CONVENTIONS.md` §1): the wheel is `3.6.1` while it
wraps allium-tools 3.6.1, `3.6.1.postN` for packaging fixes, the `[project] version` in
`crates/alliumpy/pyproject.toml` is static, and `just version-check` holds every copy
equal. There is no cargo-release: the bump is a hand edit of one line, checked by a gate.

Two things make the release irreversible and are why this ticket rehearses before it
tags: a PyPI version can never be re-uploaded, and the five-target matrix, and with it
Windows, macOS x86_64, musllinux and `cp314t`, has never run before this ticket, because
`just check` builds for the developer's platform alone (`CONVENTIONS.md` §9). The
repository is private: macOS and Windows runners consume metered Actions minutes at a
higher rate, so the rehearsal has a cost the maintainer authorises (`CONVENTIONS.md` §1
fact 6, §13).

T12 has merged, so `README.md`, `CHANGELOG.md`, `SECURITY.md` and
`crates/alliumpy/README.md` (the PyPI long description) hold their final text, and T13 has
merged under it, so the command the description describes is the one the wheel ships.
Wave-2 rules apply (`CONVENTIONS.md` §11).

## Goal

`alliumpy 3.6.1` on PyPI, published by `release-pypi.yml` from the annotated tag `v3.6.1`
on a `main` commit through a pending trusted publisher and the `release` environment, with
no token anywhere; the same workflow rehearsed first by a non-publishing
`workflow_dispatch` run over the whole matrix, whose artefacts were reviewed and smoked on
every operating system before the tag; and the end proof: on a machine with the network,
`UV_CACHE_DIR` on an empty directory, `uvx --from alliumpy==3.6.1 allium --version`
prints `allium 3.6.1 (language versions: 1, 2, 3)` with exit 0 and `uvx --from
alliumpy==3.6.1 allium check tests/fixtures/smoke/ok.allium` exits 0. Decision 0015 and
`docs/how-to/release.md` say how a release is cut.

## Non-goals

- No crates.io publish and no lifting of `publish = false`.
- No cargo-release, release-plz or git-cliff: the bump is one line and `version-check`.
- No change to the CLI, the API or the version string (T13); no sdist ruling (S01 made
  it; this ticket applies it).
- No extra platform beyond decision 6's five targets, and no `cp314t` wheel beyond what
  the generator emits and `CONVENTIONS.md` §12 claim 4 confirms.
- No PEP 541 claim on `allium`.
- No change to `check`'s `needs`: `release-pypi.yml` is never a required check
  (`CONVENTIONS.md` §10).
- No edit to the `Justfile`: the release needs no recipe `version-check`, `wheel` and
  `wheel-smoke` do not already provide.

## Files touched

| Path | Class | Content |
| --- | --- | --- |
| `.github/workflows/release-pypi.yml` | new | the generator's output, pinned, narrowed, with the smoke, `twine check`, the sdist assertion and the guarded `release` job |
| `crates/alliumpy/pyproject.toml` | shared, own lines | no edit for `3.6.1` (T00 wrote `version = "3.6.1"`; step 8 confirms it); a later `.postN` or upstream bump edits `version` on its release branch; the `[tool.maturin.generate-ci.github]` table is T00's |
| `CHANGELOG.md` | shared, own lines | the `[3.6.1] - YYYY-MM-DD` heading and its links, in the release branch |
| `docs/decisions/0015-release-process.md` | new | `CONVENTIONS.md` §8 |
| `docs/how-to/release.md` | new | "Cut a release"; slug `release_procedure` |
| `docs/manifest.yml` | shared, own lines | two entries |
| `docs/README.md` | shared, own lines | one link under "How to" |
| `docs/decisions/README.md` | shared, own lines | one row |
| `docs/operations/maintenance.md` | shared, own lines | "Cut a release", pointing at the how-to |
| `docs/explanation/packaging.md` | shared, own lines | the matrix as built, the sdist as ruled, attestation as settled |
| `docs/explanation/architecture.md` | shared, own lines | the release sentence (T07 step 7) made present tense, citing decision 0015 |
| `docs/how-to/install-and-run.md` | shared, own lines | the `uvx --from alliumpy` and `uv tool install` lines made present tense once 3.6.1 exists |
| `README.md` | shared, own lines | the install and platform sentences made present tense once 3.6.1 exists |
| `SECURITY.md` | shared, own lines | "Supported versions", once a version exists |
| `tickets/T14-release.md` | ticket | `status:` and hand-back notes |

## Steps

1. Create the worktree after T12 has merged; rebase on any wave-2 ticket merged since.
   Quote the baseline `just check`. Read S01's sdist ruling and T13's `ALLIUM_VERSION_STRING`
   outcome from their hand-back notes; both shape step 3.

2. **Pre-flight, read-only.** `gh api orgs/BiscuitBin --jq .plan.name` and
   `gh api repos/BiscuitBin/alliumpy --jq '{visibility, permissions}'`; `gh api
   repos/BiscuitBin/alliumpy/environments --jq '{total_count, names:
   [.environments[].name]}'`: none exists when a 200 response carries `total_count` 0; a
   404, which GitHub also answers to a token that may not read the resource, or any other
   error stops the step (`CONVENTIONS.md` §11). **Settle the gate from these two
   readings** (`CONVENTIONS.md` §13): GitHub's documentation for deployment environments
   says an environment on a private repository needs GitHub Pro, Team or Enterprise, and
   that on Free, Pro or Team a required reviewer is available to public repositories
   only. So if `visibility` is `private` and `.plan.name` is not an Enterprise plan, the
   `release` environment cannot carry a required reviewer: stop before step 3 and hand
   the maintainer the choice T01 had (`CONVENTIONS.md` §10): make the repository public,
   move to a plan that allows it, or the dispatch-only fallback in step 6, recorded as a
   deviation. Quote the documentation page read on the day. Read GitHub's
   artifact-attestations availability page the same way: if it says attestations on a
   private repository need GitHub Enterprise and the repository is private on a
   non-Enterprise plan, `CONVENTIONS.md` §12 claim 5 is settled as failing from that
   reading, dated and quoted, and step 3 omits the `actions/attest` step with a comment
   saying why; the rehearsal then confirms nothing else needed it. For this first
   publication, require HTTP 404 from `https://pypi.org/pypi/alliumpy/json`
   (`CONVENTIONS.md` §12 claim 7); HTTP 200 means the name is already taken and stops
   this ticket for the maintainer. The reusable release procedure in step 4 instead
   expects HTTP 200 for the existing project after the first publication. For every
   release, also require HTTP 404 from
   `https://pypi.org/pypi/alliumpy/<version>/json`: HTTP 200 means that version is
   already published and stops the release. For each URL use
   `status=$(curl -sS -o /dev/null -w '%{http_code}' "$url") || exit 1`, print the
   status, then `test "$status" = "$expected" || exit 1`, with `url` and `expected`
   set as above. Do not use `-f`, because 404 is expected; a transport failure or any
   unexpected HTTP status stops the step. Read the Actions billing state with `gh api
   orgs/BiscuitBin/settings/billing/actions` (`BiscuitBin` is an organisation,
   `CONVENTIONS.md` §13; if the REST reference on the day has replaced it with a usage
   endpoint, such as `gh api /organizations/BiscuitBin/settings/billing/usage`, use that);
   if it is unreadable, say so and ask the maintainer for the minutes left before step 7.

3. **Generate, then edit, `release-pypi.yml`.** Run `mkdir -p ai_tmp/release` (a fresh
   worktree has no such directory), then `.pixi/envs/default/bin/maturin generate-ci
   github -m crates/alliumpy/Cargo.toml -o ai_tmp/release/generated.yml` (pixi's
   binaries are on `PATH` only inside recipes), and keep that file unedited for the whole
   ticket: the hand-back notes' diff and step 10's pattern check read it. Then, for the
   positive control of step 10 and Verification, run the generator a second time with
   the `[tool.maturin.generate-ci.github]` table temporarily deleted from
   `crates/alliumpy/pyproject.toml`, `-o ai_tmp/release/generated-token.yml`: that output
   carries `UV_PUBLISH_TOKEN`, which the real output cannot, because T00's table makes
   the generator emit `uv publish --trusted-publishing always` with no token (L
   `tickets/S04-bindings-and-cli.md`). Restore the manifest with `git checkout --
   crates/alliumpy/pyproject.toml` and confirm `git status --short` prints nothing. Copy
   the first output to `.github/workflows/release-pypi.yml` and edit:
   - `name: Release to PyPI`. Triggers: `push: tags: ['v[0-9]+.[0-9]+.[0-9]+',
     'v[0-9]+.[0-9]+.[0-9]+.post[0-9]+']` and `workflow_dispatch` with one boolean input,
     `publish`, default `false`, described as "publish to PyPI (a tag push always
     publishes; a dispatch publishes only when true)". Not the generator's push to
     `main` and every tag.
   - Top level `permissions: contents: read`; a concurrency group on `github.ref` with
     `cancel-in-progress: false`; `persist-credentials: false` on every checkout.
   - Every `uses:` pinned to a 40-character SHA with a version comment, read on the day
     with `gh api repos/<owner>/<repo>/git/ref/tags/<tag>` and annotated tags
     dereferenced (`CONVENTIONS.md` §10). `PyO3/maturin-action`, `actions/checkout`,
     `actions/setup-python`, `actions/upload-artifact`, `actions/download-artifact`,
     `astral-sh/setup-uv` or whatever the generator names.
   - The matrix narrowed to decision 6: `linux` keeps `x86_64` and `aarch64` and drops
     `x86`, `armv7`, `s390x` and `ppc64le`; `musllinux` keeps `x86_64` and `aarch64`;
     `windows` keeps `x64` and drops `x86` and the ARM runner; `macos` keeps both of the
     generator's runners. T01's CI wheel is tagged `manylinux_2_34`, the glibc of the
     runner that built it; the manylinux target chosen here decides the published floor
     (`tickets/T01-github-and-ci.md:690-691`). Record the exact runner labels the generator emitted; whether
     each exists for this repository is `CONVENTIONS.md` §12 claim 4, settled by step 7.
     Keep `args: --release --out dist` with `--locked` appended if the generator did not
     (L `tickets/S04-bindings-and-cli.md`: `locked = true` already makes maturin honour
     `Cargo.lock`; confirm with the generated args and say which). Keep the abi3
     feature's consequence: no
     `--find-interpreter`, and the "Build free-threaded wheels" `cp314t` step, kept
     unless claim 4 fails on it in step 7, in which case it is removed with a comment.
   - The `sdist` job: kept or deleted as S01 ruled (`CONVENTIONS.md` §9, "The sdist"). If
     kept, a step after the build runs `tar tzf dist/*.tar.gz` and fails unless it lists
     `Cargo.lock`, both `LICENSE` and `LICENSE-allium-tools`, and, under the vendoring route
     S01 recommends, `crates/alliumpy-core/src/cli.rs`, `crates/alliumpy-core/src/cli/main.rs`,
     `crates/alliumpy-core/src/cli/test_plan.rs` and
     `crates/alliumpy-core/src/cli/domain_model.rs` (S01's seven paths,
     `tickets/S01-cli-strategy-spike.md:1048-1053`), each name matched as a whole archive entry
     (`grep -x` or `-F` with the full path and `$`), never as a prefix that
     `LICENSE-allium-tools` alone would satisfy; the list is quoted. It also fails on any
     `_bin/` entry. `tests/fixtures/parity/` is absent from the sdist by design, so
     `cargo test` from it is not expected to pass (S01:2568-2570). The `sdist` job runs
     this assertion and the `twine check` step below and nothing else: it builds no wheel
     to smoke.
   - **The bundled binary, under S01's route (b) only** (decision 0014; nothing is added
     under routes (a) and (c)): each wheel-building job gains, before its build step, the
     step S01's hand-back notes record (S01 step 5): `cargo install allium-cli@<pin>
     --locked --root <scratch>` for the job's own target, `<pin>` read with
     `scripts/version_check.py --print-pin` and never written as a literal
     (`CONVENTIONS.md` §9, "The parity reference"), then the binary copied to the
     package-data path T13 fixed, so that `maturin build` packs the target's own binary.
     On Linux the step runs inside maturin-action's container (confirm the action's
     pre-build hook input against its README on the day; L did not verify it), on macOS
     and Windows on the host. T13's open point hands this ticket where the Windows binary
     comes from; the smoke's `allium --version` is the proof that each wheel carries its
     target's binary. If S01's notes or T13's layout do not settle the aarch64,
     musllinux or Windows case, stop and hand back. The hand-back notes say where the
     version lives, which T17's runbook reads.
   - **The smoke, in each of the four wheel-building jobs (`linux`, `musllinux`,
     `windows`, `macos`), in plain shell** (`shell: bash` on every runner, Windows
     included; no `just`, no pixi, because the runner has neither; the venv's programs
     are called by path, `venv/bin/` on Linux and macOS and `venv/Scripts/` on Windows,
     never through activation): `actions/setup-python` with `python-version: '3.11'` for
     the abi3 wheel's floor; then `python -m venv venv`; the venv's `pip install
     --no-index --no-deps` of the one `cp311-abi3` wheel the job built (the exact
     filename read from `dist/`, never a glob that could match two); `python -I
     tests/fixtures/smoke/smoke.py`; `allium --version`, its output compared byte for
     byte with what the venv's `python -c 'from alliumpy._alliumpy import
     ALLIUM_VERSION_STRING as s; print(s)'` prints (`CONVENTIONS.md` §9: `_alliumpy`
     exposes it, literal or derived as T13 settled it, so the workflow needs no
     per-release edit), and whose second word must equal `[project] version` with any
     `.postN` stripped; `allium check tests/fixtures/smoke/ok.allium` must exit 0 and
     `allium check tests/fixtures/smoke/broken.allium` must exit 1, each exit code read
     explicitly and asserted: for each command, `status=0`, then
     `<venv-allium> check <fixture> || status=$?`, `echo "exit $status"`, and
     `test "$status" -eq <expected>` (0 for `ok.allium`, 1 for `broken.allium`). Use
     the venv's platform-specific command path above. The `||` captures the expected
     failure under Actions' `bash -e -o pipefail`; unexpected statuses fail the test.
     This on Windows is
     `CONVENTIONS.md` §12 claim 18, together with a byte check of the redirected stdout:
     `allium check tests/fixtures/smoke/ok.allium > out.json`, then `python -c "import
     sys; sys.exit(1 if b'\r' in open('out.json', 'rb').read() else 0)"` (bash redirects
     bytes unchanged; pwsh would re-encode them, which is why it is not used); then
     `python -m zipfile -l <wheel>` must list
     `alliumpy-<version>.dist-info/licenses/LICENSE` and
     `.../licenses/LICENSE-allium-tools` (claim 19), each as a whole-entry match as for
     the sdist. The `cp314t` wheel, where built, is smoked the same way under
     `python-version: '3.14t'` if `actions/setup-python` offers it on the day; if it does
     not, the step is dropped and the hand-back notes say the free-threaded wheel is
     built and never imported. In the `linux` x86_64 job the smoke runs on the host,
     outside the manylinux container. The two `musllinux` wheels and both aarch64 wheels
     cannot be installed on the x86_64 glibc host (pip's platform tags are the
     interpreter's libc and architecture): smoke the musllinux x86_64 wheel in a
     `python:3.11-alpine` container step, the image pinned by digest (`docker run --rm
     -v "$PWD:/w" -w /w`, the venv and the commands above inside it), and the two
     aarch64 wheels the same way under a SHA-pinned `docker/setup-qemu-action` with
     `--platform linux/arm64`, if that works on the day; a wheel no container smoke
     covers is built and never imported, stated in a workflow comment and in the
     hand-back notes.
   - A `twine check dist/*` step in each build job (`pip install twine` in the venv),
     so that the long description from `crates/alliumpy/README.md` renders.
   - The `release` job: `needs` every build job; no job-level `if`, so that it runs on
     the rehearsal too (it waits at the `release` environment on every event, step 7);
     `environment: release`; `permissions: id-token: write, contents: write,
     attestations: write` (`contents: write` for the GitHub Release below,
     `attestations: write` for `actions/attest` below and only where step 2 allows it,
     and nothing else; no job but this one has more than `contents: read`);
     `actions/checkout` with `fetch-depth: 0` and
     `persist-credentials: false`, which the generator's `release` job lacks and the
     guards below need (the default `fetch-depth: 1` leaves `merge-base` nothing to walk
     once `main` has moved past the release merge); `actions/download-artifact` with
     `pattern: wheels-*`, `path: dist` and `merge-multiple: true`, because the generator's
     bare `actions/download-artifact` puts each artefact in its own `wheels-<platform>/`
     directory and leaves no `dist/`; three guards before anything publishes, run on every
     event and each failing with `::error::`: `git merge-base --is-ancestor
     "$GITHUB_SHA" origin/main` succeeds on every event (L
     `tickets/S02-release-and-publishing.md`'s guard, unconditional there as here, without
     its `git fetch`: with `persist-credentials: false` a fetch from this private
     repository has no credential, and `fetch-depth: 0` has already brought
     `origin/main`; it is what refuses a dispatch with `publish` true from a ref not on
     `main`, since the publish step's `if` and, under step 6's fallback, nothing else
     looks at the ref; `main`'s own head and the tag's merge commit both pass it), and on
     a tag push (`github.event_name == 'push'`) `HEAD` is the tag's commit; `[project]
     version` read from `crates/alliumpy/pyproject.toml` with `python -c 'import tomllib
     ...'` equals the tag's version (`${GITHUB_REF_NAME#v}`) on a tag push, and on a
     dispatch, where there is no tag, is only read, printed and handed to the filename
     check that follows, never failing on the version alone; and `ls dist/` lists exactly
     the expected number of files (the matrix's wheel count plus the sdist if kept, a
     number written into the workflow, so an empty `dist/` fails rather than passing a
     loop over a glob that matched nothing) and every filename carries that version.
     Then, only where step 2's reading allows it, `actions/attest` over `dist/*`, run on
     every event so that the rehearsal executes it (`CONVENTIONS.md` §12 claim 5,
     confirmed by the rehearsal); where step 2 ruled it out, a comment in its place says
     why and `attestations: write` is not granted. Then the generator's `Install uv`
     (`astral-sh/setup-uv`) step with its `if:` removed, so that `uv` exists on every
     event; then `uv publish --trusted-publishing always dist/*`, the one step carrying
     `if: github.event_name == 'push' || inputs.publish == true` (the exact expression
     confirmed with actionlint), with no `UV_PUBLISH_TOKEN` and no `with: password`
     anywhere in the file (step 10's grep and the Verification block check this).
     Then `gh release create "$GITHUB_REF_NAME" --verify-tag --notes-file <the CHANGELOG
     section extracted by a small shell step>` with the run's `github.token`, under `if:
     github.event_name == 'push'`. The job-level `if` is not used: a skipped job executes
     nothing, and the download, the guards, and attest must have run once before the tag.
   - A comment at the top naming the generator command, the maturin version and the
     date, so that the next regeneration is a readable diff.

   `just lint` (actionlint runs over it).

4. **The release documents.** `docs/how-to/release.md`: the sequence of steps 2 and 7 to
   11 below as a procedure (pre-flight; `release/v<version>` branch; edit `[project]
   version` and, when the upstream version moves, both crates' `version` and the
   `allium-parser` pin, which T17's runbook owns; `CHANGELOG.md`'s `[Unreleased]` split
   into `[<version>] - <UTC date>` with the comparison links; `just version-check`;
   `just check`; pull request; merge; `git switch main && git pull --ff-only`; the
   rehearsal dispatch when the matrix or the workflow changed; `git tag -a v<version>
   -m 'alliumpy <version>'` on the merge commit; the tag push; the deployment approval,
   which is the publish; the proof), marking which steps are local, which CI does, and
   which are separately authorised. Distinguish first publication's project-level 404
   from later releases' project-level 200, and require the target version's endpoint
   to return 404 in both cases, using step 2's fail-closed status checks.
   `docs/operations/maintenance.md` gains "Cut a
   release", three lines pointing at the how-to. `docs/explanation/packaging.md` gains
   the matrix as built, the sdist as ruled and attestation as settled. `SECURITY.md`'s
   "Supported versions": the newest release on PyPI, tracking upstream, no backports.
   Decision 0015: a hand bump checked by a gate instead of cargo-release (one line, no
   crates.io, `.postN` inexpressible to Cargo), tag-triggered trusted publishing with a
   rehearsal dispatch, the `release` environment as the publish gate, what would reopen
   it (a second package, a conda-forge recipe, a crates.io publish). Register the page
   and the record (`CONVENTIONS.md` §11). `just check-docs`.

   **Adversarial review** (`CONVENTIONS.md` §14): the workflow and the documents, before
   step 5 pushes them. Ask: whether any job but `release` can see a write token or an OIDC
   token; whether a dispatch with `publish` false can reach the `uv publish` step or the
   `gh release create` step, whether a dispatch with `publish` true from a commit not on
   `main` can reach `uv publish`, and whether any step but those two sends anything
   outside the run; whether a tag on a commit not on `main`, or whose version disagrees
   with the manifest or the wheel filenames, is refused; whether the smoke could pass on
   a wheel other than the one the job built, or without checking an exit code; whether the
   `release` job's guards and `uv publish` would run over an empty `dist/`, or over
   `wheels-*/` directories the download left in place; whether a `tar tzf` or `zipfile -l`
   filter would print a pass when the archive is missing; whether every `uses:` is a SHA;
   what the how-to says that the first tag makes false.

5. **Authorisation required: push and open a pull request** for the workflow and the
   documents. Stop and ask. On approval, push and open it; `check` must be green. The
   `release` job never runs on a pull request, so the matrix is still unproved here.

6. **Authorisation required: the `release` environment and the pending publisher.** Stop
   and ask, naming both. On approval: `gh api users/<login> --jq .id` for the
   maintainer's numeric id; `gh api -X PUT repos/BiscuitBin/alliumpy/environments/release
   --input -` with a JSON body holding `reviewers: [{"type": "User", "id": <that id>}]`
   and `deployment_branch_policy: {"protected_branches": false, "custom_branch_policies":
   true}` (the PUT takes no login and no pattern); then `gh api -X POST
   repos/BiscuitBin/alliumpy/environments/release/deployment-branch-policies` twice, with
   `{"name": "main", "type": "branch"}` and `{"name": "v*", "type": "tag"}` (an
   environment with custom policies and no pattern refuses every deployment, the
   rehearsal's included). Confirm each shape against the REST reference on the day; read
   back and quote `protection_rules` and `deployment_branch_policy` from the environment
   and both patterns from `.../deployment-branch-policies`. The environment
   must exist before the workflow merges, or the first run creates it unprotected (P
   `tickets/T14-release.md` step 5). If the read-back shows no `required_reviewers` entry
   under `protection_rules`, or the PUT is refused, the environment is not a gate and the
   pending publisher is **not** registered yet: go back to the maintainer with step 2's
   choice. Under the dispatch-only fallback, the `release` job still has no job-level `if`
   (step 3: its download, guards and attest run on every event) and only the `uv publish`
   step's `if` becomes `github.event_name == 'workflow_dispatch' && inputs.publish ==
   true`, so the tag push builds and never publishes, step 10's authorisation is the
   maintainer's own `gh workflow run release-pypi.yml --ref v3.6.1 -f publish=true` after
   the tag, and the
   `environment:` key and the publisher's environment field are kept only where the plan
   lets the environment exist; the deviation and its reason are recorded in the hand-back
   notes and in decision 0015. Then, on PyPI, as the maintainer (a browser step the
   agent cannot perform; the ticket states the fields and the maintainer confirms): a
   pending publisher for project `alliumpy`, owner `BiscuitBin`, repository `alliumpy`,
   workflow `release-pypi.yml`, environment `release`. Record the date. Then the pull
   request merges (the maintainer's action).

7. **Authorisation required: the rehearsal.** Stop and ask, stating the matrix (the job
   count, the macOS and Windows jobs, and the minutes step 2 found). On approval, `gh
   workflow run release-pypi.yml --ref main -f publish=false`, then find the run with `gh
   run list --workflow release-pypi.yml --limit 1 --json databaseId,url` and wait with
   `gh run watch <id>`. The run stops at the `release` environment; the maintainer
   approves the deployment (an approval that publishes nothing, since the publish step's
   `if` is false; it rehearses step 10's gate and is dated in the hand-back notes). Read
   the result: every build job green, the `release` job green with its `uv publish` and
   `gh release create` steps skipped, quoting the step list from `gh run view <id> -v` (or
   `gh api repos/BiscuitBin/alliumpy/actions/jobs/<release-job-id> --jq '.steps[] |
   {name, conclusion}'`), which must show `skipped` for the publish and release steps and
   `success` for the download, the three guards and `actions/attest`; a skipped step
   writes no log lines, so `--log` cannot show it. Download the
   artefacts into `ai_tmp/release/rehearsal/` with `gh run download` and list them:
   filename, platform tag, size; expect the abi3 wheels for the five targets plus
   musllinux, the `cp314t` wheels where built, and the sdist if kept. Read each job's
   smoke step log and quote the `allium --version` line, the two exit codes and the two
   `licenses/` lines per platform. Settle `CONVENTIONS.md` §12 claims 1, 4, 5, 18 and 19
   from this run and record each: claim 1 is every wheel filename carrying `3.6.1` from
   the static `[project] version` with both crates at `3.6.1` (its `.post1` half is T00's
   scratch check, cited from T00's hand-back notes); claim 5 is the attest step's outcome
   in the `release` job's log, quoted, or step 2's documentation reading when the step
   was omitted. If a runner label does not exist or a job is red, fix the workflow,
   push through a second pull request (authorised), and run the rehearsal again; the
   review below is over the last green run.

   **Adversarial review** (`CONVENTIONS.md` §14): the rehearsal's artefacts and logs,
   before step 8 tags. Ask: which wheel of decision 6 is missing or carries an
   unexpected tag; whether every smoke step read a real exit code and the Windows one
   proves claim 18; whether any wheel was built from a `Cargo.lock` other than `main`'s
   (the `--locked` evidence in the build log); whether `twine check` passed on every
   artefact; whether the long description names a command the wheel does not have;
   whether the `uv publish` step was skipped by its `if` and never reached, and whether
   the `release` job's download, guards and attest steps ran rather than being skipped.

8. **The release branch.** On `release/v3.6.1` from `main`: confirm `[project] version`
   in `crates/alliumpy/pyproject.toml` is `3.6.1` (it is since T00; a packaging fix after
   this release edits it to `3.6.1.post1`); edit `CHANGELOG.md`, `[Unreleased]` becoming
   `[3.6.1] - <UTC date>` with a new empty `[Unreleased]` above it, and the link lines at
   the foot becoming
   `[Unreleased]: https://github.com/BiscuitBin/alliumpy/compare/v3.6.1...HEAD` and
   `[3.6.1]: https://github.com/BiscuitBin/alliumpy/releases/tag/v3.6.1` (the form of L
   `tickets/S02-release-and-publishing.md` lines 700-704, adapted to this repository and
   tag; P's stub carries only the `commits/main/` line T12 kept; step 3's `gh release
   create` extraction keys on the `## [3.6.1] -` heading prefix); `just version-check`;
   `just check`.

   **Adversarial review** (`CONVENTIONS.md` §14): the release branch, before this step's
   push. Ask: whether `[project] version` is `3.6.1` and `just version-check` agrees;
   whether the `[3.6.1]` section holds every `[Unreleased]` entry and nothing else, with
   both links naming `v3.6.1`; whether the date is today's UTC day; whether the shell
   step of step 3 would extract exactly that section for `gh release create`.

   **Authorisation required: push and open the pull request.** Merge once `check` is
   green (the maintainer's action). If the merge lands on a later UTC day than the
   heading, a one-line pull request re-dates it before the tag (P
   `tickets/T14-release.md` step 4).

9. **Authorisation required: the tag.** `git switch main && git pull --ff-only`, confirm
   `HEAD` is the release merge commit, `git tag -a v3.6.1 -m 'alliumpy 3.6.1'`, quote
   `git cat-file -t v3.6.1` (`tag`) and `git rev-parse v3.6.1^{commit} HEAD` (equal).
   Stop and ask. On approval, `git push origin v3.6.1`. The workflow runs and builds;
   under the required-reviewer gate it waits at the `release` environment, and under the
   dispatch-only gate it ends without publishing. If any job is red before the approval,
   nothing has reached PyPI: the run used the workflow at the tag's commit, so the fix is
   a pull request (authorised), then, authorised separately, `git tag -d v3.6.1 && git
   push origin :refs/tags/v3.6.1`, and this step again on the new merge commit.

10. **Authorisation required: the publish.** Approving the `release` deployment is the
    publish, a decision separate from the tag push (L
    `tickets/S02-release-and-publishing.md`, "Authorisation");
    the maintainer approves it in the GitHub UI or with `gh api`. Under step 6's
    dispatch-only fallback the publish is instead the maintainer's dispatch with
    `publish=true`, equally separate from the tag push. Watch the run: `uv
    publish` succeeds, the GitHub Release exists (`gh release view v3.6.1`), and
    `curl -fsS https://pypi.org/pypi/alliumpy/3.6.1/json | jq '.urls[].filename'` lists
    the same wheel set the rehearsal built (claim 7's second half). `gh run view <id>
    --log > ai_tmp/release/publish.log; echo "exit $?"` must print `exit 0`, `grep -c 'uv
    publish' ai_tmp/release/publish.log` must print at least 1 (the log was fetched and
    holds the publish step), and then `grep -i -E 'UV_PUBLISH_TOKEN|PYPI_API|password'
    ai_tmp/release/publish.log` must print nothing (positive control: the same grep over
    `ai_tmp/release/generated-token.yml`, which step 3 generated without T00's
    trusted-publishing table, matches `UV_PUBLISH_TOKEN`).

11. **The proof**, on a machine with the network and `uv` installed, from a directory
    holding this repository's `tests/fixtures/smoke/` and nothing built:

    ```sh
    export UV_CACHE_DIR="$(mktemp -d)"
    uvx -v --from alliumpy==3.6.1 allium --version 2> uvx.log; echo "exit $?"
    grep -n pypi.org uvx.log
    uvx --from alliumpy==3.6.1 allium check tests/fixtures/smoke/ok.allium; echo "exit $?"
    uvx --from alliumpy==3.6.1 allium check tests/fixtures/smoke/broken.allium; echo "exit $?"
    uv tool install alliumpy==3.6.1 && "$(uv tool dir --bin)/allium" --version; echo "exit $?"
    command -v allium; uv tool uninstall alliumpy
    uvx --python 3.11 pip download alliumpy==3.6.1 --no-deps -d "$(mktemp -d)"
    ```

    The first prints the version string and `exit 0`, and `uvx.log`, its `-v` stderr,
    names `pypi.org` (quoted in the hand-back notes); the first `check` prints `exit 0`;
    the second `exit 1`; the `uv tool install` line prints the version string and `exit
    0` from the shim `uv tool dir --bin` names, with the `command -v allium` output
    quoted beside it; the `pip download` names a `cp311-abi3` wheel for the machine. Only
    `uv` is assumed on the proof machine. This is `CONVENTIONS.md` §12 claim 2. Then the
    documents that spoke in the future tense are made present
    (`docs/how-to/install-and-run.md`, `README.md`, `SECURITY.md`, and the release
    sentence in `docs/explanation/architecture.md`, citing decision 0015), through a last
    pull request (authorised), with `just check`.

    **Adversarial review** (`CONVENTIONS.md` §14): the proof run and the published
    state, before the ticket closes. Ask: whether the proof could pass on a warm cache
    (`UV_CACHE_DIR` shown fresh) or on a locally built wheel (`uv` shown resolving from
    `pypi.org` in `-v` output); whether any secret was used anywhere in the run;
    whether the published wheel set equals the rehearsal's; whether the PyPI project page
    renders the long description and the two licence files; whether anything in the
    handbook or `README.md` still says no release exists.

## Acceptance criteria

- The rehearsal run is green on every job, `release` included, with its `uv publish`
  and `gh release create` steps skipped by their `if`, and its artefact listing shows an
  abi3 wheel for each of decision 6's five targets plus the two musllinux wheels, the
  `cp314t` wheels or a stated reason, and the sdist or S01's ruling.
- The reusable release procedure distinguishes first-publication name availability
  from an existing project and refuses an already published target version; transport
  failures and unexpected HTTP responses stop its pre-flight.
- The smoke log of every job whose wheel its runner can install (`linux` x86_64, both
  `macos`, `windows`) shows the version line, exit 0 for `ok.allium`, exit 1 for
  `broken.allium`, and both `licenses/` entries; the workflow explicitly asserts both
  statuses and captures expected failures without terminating the shell early.
  Each musllinux and aarch64 wheel shows
  the same from its container smoke or is listed as built and never imported, with the
  reason.
- `release-pypi.yml` passes actionlint; only the `release` job has `id-token: write`,
  `contents: write` and `attestations: write` (the last absent if claim 5 failed);
  `rg -n -i 'UV_PUBLISH_TOKEN|UV_PUBLISH_PASSWORD|TWINE_PASSWORD|MATURIN_PYPI_TOKEN|PYPI_API|--token|password' .github/workflows/release-pypi.yml`
  prints nothing (case-insensitive, so every spelling of a publish credential, including
  `password:`, is caught), and the same over `ai_tmp/release/generated-token.yml`
  matches.
- The `release` environment was read back with its required reviewer before the workflow
  merged, or the hand-back notes record the plan reading that made that impossible and
  the maintainer's chosen fallback; the pending publisher was registered before the tag;
  each authorisation is dated in the hand-back notes.
- `v3.6.1` is an annotated tag on the release merge commit, and
  `https://pypi.org/pypi/alliumpy/3.6.1/json` lists the rehearsal's wheel set.
- The proof block of step 11 ran as written with the quoted exit codes, and the run's log
  grep for a token printed nothing with its positive control matching.
- `CONVENTIONS.md` §12 claims 1, 2, 4, 5, 7, 18 and 19 each have a recorded outcome.
- `just check` is green.
- The adversarial reviews in Steps ran (`CONVENTIONS.md` §14), and every valid finding is
  fixed or handed back.

## Verification

```sh
just lint
rg -n 'permissions|environment|tags:|workflow_dispatch|trusted-publishing|attest' .github/workflows/release-pypi.yml
rg -n -i 'UV_PUBLISH_TOKEN|UV_PUBLISH_PASSWORD|TWINE_PASSWORD|MATURIN_PYPI_TOKEN|PYPI_API|--token|password' .github/workflows/release-pypi.yml; echo "exit $?"   # must be 1
rg -n -i 'UV_PUBLISH_TOKEN|UV_PUBLISH_PASSWORD|TWINE_PASSWORD|MATURIN_PYPI_TOKEN|PYPI_API|--token|password' ai_tmp/release/generated-token.yml; echo "exit $?"   # must be 0
rg -c 'uses: ' .github/workflows/release-pypi.yml; echo "exit $?"   # a count above zero and exit 0: the positive control
rg -v 'uses: \./' .github/workflows/release-pypi.yml | rg 'uses: ' | rg -v '@[0-9a-f]{40} # v[0-9]+\.[0-9]+\.[0-9]+$'; echo "exit $?"   # must print nothing, exit 1
gh api repos/BiscuitBin/alliumpy/environments/release --jq '{protection_rules, deployment_branch_policy}'
gh api repos/BiscuitBin/alliumpy/environments/release/deployment-branch-policies --jq '.branch_policies[] | {name, type}'
gh run list --repo BiscuitBin/alliumpy --workflow release-pypi.yml --limit 3
ls -l ai_tmp/release/rehearsal/*/
git cat-file -t v3.6.1; git rev-parse v3.6.1^{commit}   # tag; the merge commit step 9 quoted
git fetch origin && git merge-base --is-ancestor v3.6.1^{commit} origin/main; echo "exit $?"   # must be 0
curl -fsS https://pypi.org/pypi/alliumpy/3.6.1/json | jq -r '.urls[].filename'
gh release view v3.6.1 --repo BiscuitBin/alliumpy
just version-check
just check
```

## Hand-back notes

To be written by the executing agent: the pre-flight readings (plan, visibility,
minutes, the PyPI 404) and the gate they settled; the generator's output against the
edited workflow, as a summarised diff; every runner label and action SHA used, with the
day; the rehearsal's
run URL, artefact table and per-platform smoke quotes; the outcome of `CONVENTIONS.md`
§12 claims 1, 2, 4, 5, 7, 18 and 19, one row each; each authorisation with its timestamp
and what ran; the tag and publish run URLs; the proof block's output; the review record
for each of the four checkpoints (`CONVENTIONS.md` §14); where this ticket departed from
L's drafts; what T17 inherits (the pins the workflow adds, the runbook's release steps).

## Open points

- Whether the macOS x86_64 runner the generator names is still offered to a private
  repository on the free plan on the day; if not, the target is dropped from decision 6
  through a `main` edit of `CONVENTIONS.md`, stated here, rather than built on a paid
  runner without asking.
- Whether to publish `3.6.1` or wait for upstream's next release: this ticket publishes
  `3.6.1` (Goal, `CONVENTIONS.md` §1 decision 4). An upstream bump is T17's runbook,
  which depends on this ticket, so waiting means pausing T14 before step 8, not bumping
  here; the procedure is not the same. The maintainer confirms at step 5.
- Whether a tag ruleset restricting `v*` tag creation to the maintainer is wanted as L's
  draft had it. Rulesets on a private repository may be a paid-plan feature
  (`CONVENTIONS.md` §1 fact 6); the environment's required reviewer holds only where the
  plan and visibility allow it (step 2 settles this, `CONVENTIONS.md` §13).
- Whether the GitHub Release object is worth `contents: write` at all, since PyPI is the
  artefact store; L's draft dropped it, P's kept it. Kept here so that the CHANGELOG
  section is readable on GitHub; the maintainer may strike it.
