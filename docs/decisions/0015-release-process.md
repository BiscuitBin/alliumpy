---
title: "Decision 0015: The release process"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_release_process"]
requires: []
---

# Decision 0015: The release process

## Context

This repository publishes one Python distribution, `alliumpy`, to PyPI and nothing to
crates.io: both crates keep `publish = false`. Its version is one hand-edited line,
`[project] version` in `crates/alliumpy/pyproject.toml`, held equal to the crates and the
`allium-parser` pin by `just version-check` ([decision
0010](0010-version-tracks-upstream.md)). A PyPI version can never be uploaded again, and
`just check` builds for the developer's platform alone, so the five-target matrix of
[decision 0012](0012-abi3-wheels-and-platforms.md) first runs in the release workflow.
pachinko's release used cargo-release, per-crate tags and a GitHub Release; only its
shape carries here: a release branch, a pull request that requires `check`, an annotated
tag on the merge commit, a workflow the tag starts, and a `release` environment with a
required reviewer.

## Decision

The bump is a hand edit checked by a gate, not cargo-release. There is one line to
move, no crate to publish, and a packaging fix's `.postN` cannot be expressed in Cargo's
version, so a release tool would add a dependency to automate what `version-check`
already proves.

`release-pypi.yml` is `maturin generate-ci github` output from maturin 1.15.0, edited by
hand and never regenerated in place. It runs on a tag `vX.Y.Z` or `vX.Y.Z.postN` and on
`workflow_dispatch` with a `publish` boolean that defaults to false. Every job but
`release` has a read-only token and no OIDC token. Each build job builds the `cp311-abi3`
wheel and the free-threaded `cp314t` wheel with `--locked`, installs each wheel it
built into a fresh venv (Python 3.11 for abi3, 3.14t for `cp314t`), smokes it, compares `allium --version` byte for
byte with `ALLIUM_VERSION_STRING`, asserts the exit codes of `allium check`, checks both
licence entries in the wheel and runs `twine check`. Wheels the runner cannot import are
smoked in digest-pinned containers, aarch64 under QEMU; wheels no container covers are
built and never imported, as the workflow states. The `sdist` job asserts `Cargo.lock`,
both licence texts and the vendored CLI sources as whole archive entries.

The `release` job has no job-level condition, so a rehearsal dispatch runs everything
but the publish: it waits at the `release` environment, downloads every artefact into
`dist/`, refuses a commit not on `main`, a tag that disagrees with `[project] version`
and a `dist/` that does not hold exactly the expected files, and attests the files. Only
`uv publish --trusted-publishing always` (on a tag push or a dispatch with `publish`
true) and `gh release create` (on a tag push) are conditional. Trusted publishing is the
only PyPI credential, and no PyPI token is stored: a pending publisher on PyPI names this
repository, the workflow file and the `release` environment. The environment's required
reviewer is the publish gate, so approving the deployment is the publish, a decision
separate from pushing the tag.

The pre-flight of 2026-11-04 settled two availability questions. The repository is
public and the organisation's plan is `enterprise`; GitHub's documentation says
required reviewers on Free, Pro or Team plans are available to public repositories only,
and that artifact attestations on those plans are only available for public
repositories, so both apply here and `actions/attest` runs in the `release` job.

## Consequences

Each release costs a matrix run of macOS and Windows runners, twice when a rehearsal
precedes it. The workflow is a hand-edited copy, so a maturin upgrade means generating
into `ai_tmp/`, diffing and porting the changes by hand. The expected file count is a
literal in the `release` job and moves with any change to the matrix. Three wheels, the
aarch64 and musllinux `cp314t` ones, are built and never imported. The GitHub Release
takes `contents: write` in the `release` job for notes PyPI does not need. Nothing
prevents a second tag on an unreleased commit of `main`: the reviewer is the only stop.
If the repository became private on a non-Enterprise plan, the required reviewer and
attestation would both stop working, and the fallback is a dispatch-only publish
recorded as a change to this decision.

## What would reopen this

A second distribution from this repository. A conda-forge recipe, which would add a
second release target. A crates.io publish of either crate, which would make
cargo-release or release-plz worth its dependency. A change of plan or visibility that
removes the required reviewer or attestation. maturin's generator changing shape enough
that hand-porting a regeneration costs more than rewriting the workflow.

## Related pages

- [Cut a release](../how-to/release.md)
- [Python packaging](../explanation/packaging.md)
- [Decision 0010: The wheel version tracks upstream](0010-version-tracks-upstream.md)
- [Decision 0012: `abi3-py311` wheels and the five platforms](0012-abi3-wheels-and-platforms.md)
- [Decision 0014: How the `allium` command gets into the wheel](0014-cli-strategy.md)
