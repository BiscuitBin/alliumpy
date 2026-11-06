---
title: "Decision 0017: Dependency updates through Renovate, except the upstream pin"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_dependency_updates"]
requires: []
---

# Decision 0017: Dependency updates through Renovate, except the upstream pin

## Context

Every pin here moved by hand. Libpawdoku's S01 spike compared Dependabot, Renovate and no
updater against the same kinds of pins, and found Dependabot stronger than expected: it
has `rust-toolchain` and `pre-commit` ecosystems. What Renovate alone reaches is the
one-line pins outside any ecosystem: the lines of `tools.txt` and `tools-source.txt`,
`rust-version` grouped with the toolchain, the tooling package's tag, the workflow inputs
and the markdownlint rev repeated in `.pre-commit-fix.yaml`. Dependabot cannot read a pixi
manifest at all. Pachinko adopted Renovate on the same hosted app in the same
organisation, and its first dashboard listed every regex manager.

This repository has pins pachinko does not: the Python tools in the pixi manifest, the
maturin range in `crates/alliumpy/pyproject.toml`, the pyo3 crate, and the release
workflow's `maturin-version`, `setup-uv` `version` and `twine` pins. It also has one pin
that must not move as a dependency: `allium-parser`.

## Decision

Renovate, through the Mend-hosted app, configured by `renovate.json` at the repository
root. The app was already installed for every repository in the `BiscuitBin` organisation
when this was decided, on 2026-10-24 for pachinko, and the maintainer chose to keep that
rather than narrow it to this repository. Native managers read the crates (both cargo
roots), the actions, the pixi pins, the toolchain channel and the `build-system` range.
Regex managers read `rust-version`, `tools.txt` and `tools-source.txt`, `nextest-version`,
`maturin-version`, the `setup-uv` version, `twine`, the tooling tag, the pixi bootstrap
pair and the hook revs.

**The exclusion.** A rule disables `allium-parser` under the cargo manager, in both cargo
roots. An upstream bump moves the wheel version, the version constants, the vendored code
and the parity reference together, and `just version-check` fails a bare one by design; it
is a release through [Bump upstream](../how-to/bump-upstream.md). Lock-file maintenance
cannot move it either, because cargo holds an `=` requirement. The parity reference has no
pin of its own, so nothing else can carry a different upstream version. No rule names
`allium-cli`, because [decision 0014](0014-cli-strategy.md) chose route (a); route (c)
would have to add it.

**What flows and what is held.** The configuration landed with
`:dependencyDashboardApproval` in `extends`, so that nothing opened before the proofs were
read, and that line was then removed. The `crates` and `github actions` groups now open
weekly; every other rule carries its own approval and waits for a click on the dependency
dashboard. There is one exception: Renovate's `vulnerabilityAlerts` settings skip dashboard
approval by default, and vulnerability alerts are enabled here, so a vulnerability-fix pull
request can open unasked. It still never merges itself, and the exclusion holds against it:
a dependency a package rule disabled stays disabled under an alert. `automerge` is `false`.

**Pairs read from one source.** `uv`, `maturin` and `cargo-nextest` each have a pin in the
pixi manifest and a copy elsewhere that must equal it. The copies are read from conda-forge
through regex managers, under the pixi pin's depName, and grouped with it. Grouping
Renovate's native readings would not do: those read GitHub releases and PyPI, which can run
ahead of what conda-forge carries and split the pair. The maturin range is a separate
group, because it is a range the sdist's builder honours and not a copy of a pin.

**The toolchain.** The native `rust-toolchain` manager reads `channel` and a regex manager
reads `rust-version` in both manifests, under one depName and the `rust-version`
datasource. `rust-release-channel` versioning keeps the precision of the value it
replaces, so `rust-version` stays `major.minor` and moves only on a minor release.

## Consequences

The installation holds read access to administration, members, metadata, packages and
vulnerability alerts, and write access to checks, contents, issues, pull requests,
statuses and workflows, which the [security model](../explanation/security-model.md)
records. It reaches every repository in the organisation. No review is required on
`main`, so "a person merges" rests on `automerge` staying off.

Some pins stay manual, and [Maintain dependencies](../how-to/maintain-dependencies.md) says
why for each: the three image digests in `release-pypi.yml`, the two `requires-python`
floors, the `python-version` inputs, the tooling interpreter, the release matrix's runner
labels, lychee and its `LYCHEE_VERSION`, and the literal `15` in the release job's guard.

`release-pypi.yml` does not run on pull requests, so an update to its actions or inputs is
first exercised by the release rehearsal, not by the branch that moved it.

Each regex manager is proved only by Renovate itself, from its dashboard or a real pull
request; the first dashboard, on 2026-11-05, listed every one (ticket T17's hand-back
notes). There is no local validator: `tickets/CONVENTIONS.md` section 4 gives this decision
no recipe, and a pinned one would need node through a pixi pin.

The hosted app relocks `pixi.lock`, but `requires-pixi` is only a floor, so it can relock
with a newer pixi than CI pins. On 2026-11-05 that turned every relocking branch red until
the `pixi bootstrap` group moved CI to 0.84.1. It can recur;
[Maintain dependencies](../how-to/maintain-dependencies.md) says what to do.

## What would reopen this

The app's permissions changing, or Mend's hosted service ending. The hosted app ceasing to
relock `pixi.lock`, which would put that relock on the manual list. The relock breaking CI
repeatedly, which would argue for pinning the pixi it uses with `constraints`. A Renovate manager
for crates.io binaries, which would replace the regex over `tools.txt`. Dependabot gaining
the one-line pins above, or a way to read a pixi manifest. Decision 0014 moving to route
(c), which would extend the exclusion to `allium-cli`.

## Related pages

- [Maintain dependencies](../how-to/maintain-dependencies.md)
- [Bump upstream](../how-to/bump-upstream.md)
- [Maintenance](../operations/maintenance.md)
- [Security model](../explanation/security-model.md)
- [Decision 0004: Dependency policy](0004-dependency-policy.md)
- [Decision 0011: An exact pin on `allium-parser`](0011-exact-pin-on-allium-parser.md)
