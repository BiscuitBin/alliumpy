---
title: "Maintenance"
kind: "operations"
audience: ["maintainer", "operator", "agent"]
canonical_for: ["maintenance_routine"]
requires: []
---

# Maintenance

There is no service to operate. The parser runs inside whoever calls it, nothing
accumulates between releases, and there is no on-call. The API reference can be deployed when the repository visibility permits it; see
[Deploy to GitHub Pages](../how-to/deploy-to-github-pages.md). What follows is upkeep of
the pins that build and check it.

## Routine

**Weekly.** Read the week's run of the `audit` workflow. It runs `just audit` against the
RustSec advisory database every Monday, as well as on every pull request, and it is never
a required check, so a failure there blocks nothing and is easy to miss. An advisory
against a crate in `Cargo.lock` is fixed by moving that crate, not by ignoring it.

In the same weekly pass, read the `mutants` and `fuzz` runs, which also run every
Monday and are never required. A red `mutants` run names a surviving mutant in its
`mutants` artefact; answer it with a test in the core, or exclude a truly equivalent
mutant in `.cargo/mutants.toml` with a comment. A red `fuzz` run uploads the crashing
input. A crash in this repository's conversion is fixed here with a regression test; a
crash inside upstream's parser is reported upstream and waits for an upstream release,
because upstream decides behaviour ([decision 0016](../decisions/0016-mutation-bench-and-fuzz.md)).

**Monthly.** Read Renovate's dependency dashboard and approve what is due, one kind at a
time, then read each pull request it opens and merge it yourself;
[Maintain dependencies](../how-to/maintain-dependencies.md) lists what it proposes and what
each kind needs. The `crates` and `github actions` groups open weekly without that click,
and a vulnerability-fix pull request can open unasked; read and merge those too. Approve a
`tools-source.txt` line one release at a time, because
rustqual is a gate. What Renovate does not read moves by hand, as that page lists; to move
a lockfile without waiting for it, `just lock-upgrade` moves all three within the
manifests' constraints, and `just check` and a commit follow.

**Monthly.** Run `just check-links-online`. It is not part of the gate because it needs
the network, so external links rot silently until someone looks.

**Per toolchain release.** Approve Renovate's `rust toolchain` update, which moves
`rust-toolchain.toml` and `rust-version` in both manifests together, then run `just clippy`
on its branch before anything else: clippy's lint set moves with the release, and a lint
that is new under `-D warnings` fails the gate with no change to the code. `just check`
follows.

## Cut a release

A release is a version tag on a `main` commit, a rehearsed workflow run and a deployment
approval that publishes to PyPI; [Cut a release](../how-to/release.md) is the procedure,
with every step that leaves the worktree marked as separately authorised.

## When upstream releases

An upstream bump is a release, not an ordinary dependency update, so Renovate leaves it
alone and the dashboard never lists it as an update. Check for a new upstream release
yourself, then follow [Bump upstream](../how-to/bump-upstream.md), which ends in
[Cut a release](../how-to/release.md). Signatures have grown between upstream releases; a
bare pin bump fails version-check.

The first dashboard after upstream's next release is also a check on the exclusion:
`allium-parser` has had no newer version to refuse since it landed, so read that it opens
no update and no branch.

Nothing here merges on its own. Renovate proposes moves to the other pins: the `crates` and
`github actions` groups open weekly, the rest wait for a dashboard click, and a
vulnerability-fix pull request can open unasked. Each waits for a person to merge it.

## Secrets

None are stored, and there is nothing to rotate. Continuous integration uses the token
GitHub mints for each run and discards with it. Publishing to PyPI uses trusted
publishing from `release-pypi.yml` and the `release` environment, never a stored token
([decision 0015](../decisions/0015-release-process.md)).

## Related pages

- [Maintain dependencies](../how-to/maintain-dependencies.md)
- [Bump upstream](../how-to/bump-upstream.md)
- [Cut a release](../how-to/release.md)
- [Troubleshooting](troubleshooting.md)
- [Security model](../explanation/security-model.md)
