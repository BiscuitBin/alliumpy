---
title: "Cut a release"
kind: "how-to"
audience: ["maintainer", "agent"]
canonical_for: ["release_procedure"]
requires: []
---

# Cut a release

A release publishes one version of the `alliumpy` wheel and its sdist to PyPI from an
annotated tag on `main`, through `.github/workflows/release-pypi.yml` and PyPI's trusted
publisher. No PyPI token is stored anywhere. A PyPI version can never be uploaded twice,
so every step that leaves the worktree is authorised on its own, and the publish is a
deployment approval separate from the tag push.
[Decision 0015](../decisions/0015-release-process.md) records why the process has this
shape; [decision 0010](../decisions/0010-version-tracks-upstream.md) owns the version
policy.

Each step below is marked **local** (the worktree only, no network), **read-only
network** (reads a remote and changes nothing there; run it only where the task
authorises network access), **CI** (a workflow does it) or **authorised** (changes
something outside the worktree, or creates a tag; ask first, and approval for one step
is not approval for the next).

## When the version moves

A packaging-only fix of a release `X.Y.Z` is `X.Y.Z.postN`: only `[project] version` in
`crates/alliumpy/pyproject.toml` moves. A new upstream release moves `[project]
version`, both crates' `version` and the exact `allium-parser` pin together; that bump
belongs to T17's upstream-bump runbook, `docs/how-to/bump-upstream.md`, with this page
as its last part. T17 has not written that runbook yet, so an upstream bump is not
available until it exists. `just version-check` fails a bare pin bump by design.

## Pre-flight

**read-only network**. Set `version` to the version being released, then read the plan,
the visibility and the `release` environment:

```sh
gh api orgs/BiscuitBin --jq .plan.name
gh api repos/BiscuitBin/alliumpy --jq '{visibility, permissions}'
gh api repos/BiscuitBin/alliumpy/environments/release \
  --jq '{protection_rules, deployment_branch_policy}'
```

A 404 or any other error stops the release; GitHub also answers 404 to a token that may
not read the resource. A plan name of `null` means the token cannot read the plan: stop
and ask an organisation owner rather than infer it. The environment must show a `required_reviewers` rule: on GitHub
Free, Pro or Team, required reviewers exist for public repositories only.

Then read PyPI with a status check that fails closed. Do not use `curl -f`, because a
404 is an expected answer here. Set `project_code` to `404` for the first publication
and to `200` for every later release; the snippet refuses to run without it:

```sh
check() {
  url=$1 expected=$2
  code=$(curl -sS -o /dev/null -w '%{http_code}' "$url") || return 1
  echo "$url $code"
  test "$code" = "$expected"
}
check https://pypi.org/pypi/alliumpy/json "${project_code:?404 or 200}" &&
  check "https://pypi.org/pypi/alliumpy/${version:?}/json" 404 &&
  echo "pre-flight passed"
```

The last line must print `pre-flight passed`; the variable is `code` rather than
`status`, which zsh reserves.

For the first publication the project endpoint must answer 404: a 200 means the name is
taken, and the release stops for the maintainer. For every later release it must answer
200, the existing project. The version endpoint must answer 404 in both cases: a 200
means that version is already published, and the release stops. A transport failure or
any other status stops the step.

## The release branch

1. **read-only network** `git switch main && git pull --ff-only`, then **local**
   `git switch -c release/v<version>`.
2. **local** Edit `[project] version`, and for an upstream bump the crates and the pin
   as T17's runbook will say once it exists.
3. **local** In `CHANGELOG.md`, rename `## [Unreleased]` to
   `## [<version>] - <UTC date>` and add a new empty `## [Unreleased]` above it. At the
   foot, the links become
   `[Unreleased]: https://github.com/BiscuitBin/alliumpy/compare/v<version>...HEAD` and
   `[<version>]: https://github.com/BiscuitBin/alliumpy/releases/tag/v<version>`. The
   workflow's release notes are the lines under the `## [<version>] -` heading up to the
   next heading or the link lines, so the heading's prefix must be exact.
4. **local** `just version-check`, then `just check`, which must end with
   `All checks passed and the worktree is unchanged.`
5. **authorised** Push the branch and open a pull request. **CI** runs `check`.
6. **authorised** Merge once `check` is green. If the merge lands on a later UTC day than
   the heading, a one-line pull request re-dates it before the tag.

## The rehearsal

**authorised**, whenever the matrix or `release-pypi.yml` changed since the last green
run, and before the first release. It costs Actions minutes on macOS and Windows
runners.

```sh
gh workflow run release-pypi.yml --ref main -f publish=false
gh run list --workflow release-pypi.yml --event workflow_dispatch --limit 1 \
  --json databaseId,url,createdAt,headSha
gh run watch <id>
```

The run is created a moment after the dispatch returns, so confirm that `createdAt` is
after the dispatch and `headSha` is `main`'s head before watching or approving it.

**CI** builds every wheel and the sdist, smokes each wheel its runner or a pinned
container can import, and runs `twine check`. The `release` job then waits at the
`release` environment; approving it publishes no distribution to PyPI and creates no
GitHub Release, because those steps' `if` is false on a dispatch without `publish`. The
attestation still runs: it signs through Sigstore and records the attestation on GitHub.
Read the `release` job's steps:

```sh
gh api repos/BiscuitBin/alliumpy/actions/jobs/<release-job-id> \
  --jq '.steps[] | {name, conclusion}'
```

The download, the three guards and the attestation show `success`; `Publish to PyPI`
and `Create the GitHub Release` show `skipped`. Download the artefacts with
`gh run download <id> -D ai_tmp/release/rehearsal` and list them: 7 `cp311-abi3`
wheels, 7 `cp314t` wheels and one sdist.

## The tag and the publish

1. **read-only network** `git switch main && git pull --ff-only`; **local** confirm
   `HEAD` is the release merge commit.
2. **authorised** `git tag -a v<version> -m 'alliumpy <version>'`; `git cat-file -t
   v<version>` prints `tag` and `git rev-parse v<version>^{commit} HEAD` prints one
   commit twice.
3. **authorised** `git push origin v<version>`. **CI** builds and smokes the matrix
   again from the tag's commit and waits at the `release` environment. Its guards
   refuse a commit not on `main`, a tag that disagrees with `[project] version`, and a
   `dist/` that does not hold exactly the expected files, each carrying the version.
4. **authorised** Approve the `release` deployment, in the GitHub UI or through
   `gh api`. This approval is the publish: **CI** runs `uv publish --trusted-publishing
   always` and creates the GitHub Release from the CHANGELOG section.

If a job is red before the approval, nothing has reached PyPI. Fix the workflow through
a pull request, then, separately authorised, delete the tag locally and on the remote
and tag the new merge commit.

## The proof

**read-only network**, on a machine with `uv`, from a directory holding this
repository's `tests/fixtures/smoke/` and nothing built:

```sh
export UV_CACHE_DIR="$(mktemp -d)"
uvx -v --from "alliumpy==$version" allium --version 2> uvx.log; echo "exit $?"
grep -n pypi.org uvx.log
uvx --from "alliumpy==$version" allium check tests/fixtures/smoke/ok.allium; echo "exit $?"
uvx --from "alliumpy==$version" allium check tests/fixtures/smoke/broken.allium; echo "exit $?"
```

The first prints the version line and `exit 0`, and `uvx.log` names `pypi.org`; the
checks print `exit 0` and `exit 1`. Then list the published files, with the download
checked before the filter reads it:

```sh
curl -fsS -o release.json "https://pypi.org/pypi/alliumpy/$version/json" &&
  jq -r '.urls[].filename' release.json > release.files &&
  test -s release.files && sort release.files
```

It lists the rehearsal's file set: 7 `cp311-abi3` wheels, 7 `cp314t` wheels and one
sdist.

## Related pages

- [Decision 0015: The release process](../decisions/0015-release-process.md)
- [Python packaging](../explanation/packaging.md)
- [Maintenance](../operations/maintenance.md)
- [Install and run](install-and-run.md)
