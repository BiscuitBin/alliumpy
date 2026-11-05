---
title: "Maintain dependencies"
kind: "how-to"
audience: ["maintainer", "agent"]
canonical_for: ["dependency_maintenance"]
requires: []
---

# Maintain dependencies

The manifests write full `x.y.z` caret ranges, and `Cargo.lock` is the pin: committed,
marked `linguist-generated`, and passed `--locked` by every cargo gate that builds or
resolves dependencies (invariant 7 names the two exceptions, `deps-unused` and
`snapshots-check`), so no recipe that checks can rewrite it. This is
[decision 0004](../decisions/0004-dependency-policy.md), a stated
deviation from the games' exact-pin rule, because a library that writes `=1.2.3` poisons
every downstream resolution: two crates pinning different patch releases of one
dependency cannot be built together. The tools are the other way round: `pyproject.toml`
pins each one exactly, and `pixi.lock`, committed beside it, records the resolution.
Renovate proposes moves to most of these pins, and the upstream parser is excluded;
nothing merges itself.

## What the updater proposes

`renovate.json` at the repository root names every pin Renovate reads
([decision 0017](../decisions/0017-renovate.md)). Each update waits for a click on the
dependency dashboard while `:dependencyDashboardApproval` is in `extends`, with one
exception: a vulnerability-fix pull request skips that approval and can open unasked,
because vulnerability alerts are enabled on this repository. It still never merges itself.
An approved pull request runs the same jobs as any branch; read its diff as you would
anyone's. There is no local validator: after editing `renovate.json`, the check is that no
`Action Required: Fix Renovate Configuration` issue appears and the dashboard shows no
configuration error.

| Group | What moves |
| --- | --- |
| `crates` | `Cargo.lock` and `fuzz/Cargo.lock` within the caret ranges, or a range itself when a release falls outside it, which is the diff to read |
| `github actions` | each remote action's SHA with its version comment, in the workflows and the `setup` action |
| `rust toolchain` | `channel` in `rust-toolchain.toml` and `rust-version` in the root and fuzz manifests |
| `pixi bootstrap` | `requires-pixi` in `pyproject.toml` and `pixi-version` in the `setup` action |
| `uv` | the pin in `pyproject.toml` and the release job's `setup-uv` `version` |
| `maturin` | the pin in `pyproject.toml` and every `maturin-version` in `release-pypi.yml` |
| `cargo-nextest` | the pin in `pyproject.toml` and `nextest-version` in `.config/nextest.toml` |
| `python build backend` | the `maturin` range in `crates/alliumpy/pyproject.toml` |
| `hook revs` | every hook SHA and comment in both prek configurations, except lychee's |
| one per pin | the other tool pins in `pyproject.toml`, each line of `tools.txt` and `tools-source.txt`, `twine` in `release-pypi.yml`, and the `biscuit-games-tooling` tag |
| lock-file maintenance | the transitive closure of the three lockfiles |

Major updates open in a pull request of their own beside their group's, because
Renovate's `separateMajorMinor` takes precedence over a group.

Some of these need more than the branch shows:

- **`pixi.lock`.** Renovate's `pixi` manager relocks only where the app allows `pixi` in
  `allowedUnsafeExecutions`, which the hosted app does not document. Pachinko's branches
  on the same app carried their relock; this repository's first approved branch is what
  proves it here. If a branch arrives without one, `just lock-check` fails on it; check the
  branch out and run `pixi update <name>`.
- **The `maturin` range.** `requires = ["maturin>=1.15,<2.0"]` is kept rather than pinned.
  The pixi pin is what builds locally and in `just check`, and the release workflow sets
  `maturin-version`, so neither reads the range. It is what a user's installer honours when
  it builds the sdist; PyPI itself builds nothing. `just wheel-smoke` never reads it, so its
  colour proves nothing about a range update; try `uv build --sdist` from the branch.
- **`serde` and `serde_json`.** The vendored command depends on both, so an update can
  change the `allium` command's output while upstream's reference keeps its own. Read the
  `parity` job on that branch; CI runs it on every pull request.
- **`release-pypi.yml`.** It does not run on pull requests, so an update to its actions,
  inputs or `twine` passes CI without running. The
  [release rehearsal](release.md#the-rehearsal) is what first exercises it.
- **A toolchain update.** clippy's lint set moves with the release, so a red `rust` job is
  often new lints; check the branch out, run `just clippy` and fix what it finds.
  `rust-version` moves only on a minor release. Prose naming the toolchain moves by hand.
- **`tools.txt`.** Its versions are read from crates.io, but its pass installs only a
  release binary. Before approving, check that the release has an archive for each
  platform.

These stay with you:

| Pin | Why it is manual |
| --- | --- |
| `allium-parser` | Excluded. A bump is a release: [Bump upstream](bump-upstream.md) |
| the parity reference | It has no pin of its own; it moves with `allium-parser`, by the runbook |
| `python = "3.14.*"` | The tooling interpreter, not a pin to bump; the rule disables it |
| `requires-python`, both; `python_version` in `mypy.ini`; `target-version` in `ruff.toml` | `>=3.14` follows the tooling interpreter; `>=3.11` is the abi3 floor of [decision 0012](../decisions/0012-abi3-wheels-and-platforms.md), and the other two move with that floor |
| `python-version` inputs | `3.11` is that same floor; `3.14t` is the free-threaded build the release matrix smokes |
| the three image digests in `release-pypi.yml` | Smoke-only, never in the wheel. Bare digests suit a regex poorly, and the `python` images' tags would need a digest-only rule |
| runner labels in the release matrix | `ubuntu-22.04` and `macos-15-intel` sit under `matrix.platform.runner`, which the manager does not reach; they decide which wheels build (decision 0012) |
| lychee | `LYCHEE_VERSION` in both argument lists must match its rev comment, and its tags are prefixed `lychee-v` |
| the literal `15` in the `release` job | The expected file count; it moves with the matrix, not with any release |

## Check that the lockfiles still match

```console
just lock-check
```

This runs `cargo update --workspace --locked --offline`, the same line over
`fuzz/Cargo.toml`, and `pixi lock --check --offline --dry-run`, none of which writes. It is gate 2 of
`just check`, so a manifest edited without relocking fails the gate rather than
drifting.

## Update deliberately

```console
just lock            # relock after a manifest edit
just lock-upgrade    # move every crate to the newest version its range admits
```

`just lock` relocks the workspace against what the manifests state, then runs
`pixi lock`. It relocks `fuzz/Cargo.lock` too: the fuzz crate sits outside the
workspace (decision 0016), so its lockfile is a third pin that moves with the others,
and its path dependency on the core names no version, so a workspace version bump
leaves it stale until `just lock` runs. It is not a no-op: a dependency whose range was edited, or that is new,
resolves to the newest version its range admits, not to the version the range names.
`just lock-upgrade` moves every crate, transitive ones included, to the newest version
its range admits, in both Cargo lockfiles, which under caret ranges changes plenty, and
runs `pixi update`. Every
tool pin is exact, so that moves transitive packages and one direct one: Python, pinned
`3.14.*`, whose patch release can move. Read both lockfile diffs before accepting them.

## Upgrading a crate

1. The version lives in `[workspace.dependencies]` in the root `Cargo.toml` and nowhere
   else; a member crate names the dependency with `workspace = true`. Edit the range there.
2. Run `just lock`, then read the `Cargo.lock` diff before accepting it.
3. Run `just sync`, so the new sources are fetched while the network is there.
4. Run `just deny`: licences, bans and sources, answered offline.
5. Run `just check`. A clippy or rustdoc upgrade usually surfaces new findings; fix them
   rather than pinning back, unless the finding is wrong for this project.
6. Run `just audit` for security advisories. It needs the RustSec database over the
   network, which is why it sits outside `just check`; the scheduled `audit.yml` workflow
   runs it too.

A new crate, rather than a new version of one, is a decision-0004 note in the pull
request: what it is for, why it is needed, alternatives considered, and licence and gate impact.

## The tools in `pyproject.toml`

The `[tool.pixi.dependencies]` table pins tools, including prek, exactly; Python uses
the `3.14.*` patch range. `pixi.lock` records the exact resolution for each platform
(decision 0006). To move an exact pin or change Python's range, edit its line, relock
that one package, read the lockfile diff, and commit `pixi.lock` with the manifest:

```console
pixi update <name>
```

Two lists hold what conda-forge lacks, one `name@version` per line, and
`just install-tools` reads both. It skips a version already installed.

- `tools.txt` (cargo-hack and cargo-fuzz today) is binary-only: its pass never compiles
  (`--disable-strategies compile`), so a tool with no prebuilt binary fails loudly
  rather than building at bootstrap.
- `tools-source.txt` (rustqual today) is for a tool with no prebuilt binary at all. Its
  pass may compile, from crates.io source with `--locked`, or take a signed
  cargo-quickinstall build, but never an unsigned upstream release asset
  (`--disable-strategies crate-meta-data`). A line goes here only on a
  decision record that accepts the source build, as
  [decision 0007](../decisions/0007-metrics-gate.md) does for rustqual.

Renovate proposes a bump to either, held for approval. By hand, edit the line and run
`just install-tools`. cargo-fuzz's line moves
with `libfuzzer-sys` in `fuzz/Cargo.toml`; after either, run `just fuzz-build`, and on a
macOS bump check whether the release now ships an arm64 binary, which would retire the
Rosetta prerequisite. Move a
`tools-source.txt` pin one release at a time and run `just check` on each, because the
tool is a gate: record any bump that needs a suppression or threshold change, as
decision 0007 requires.

Outside both files sit the bootstrap pins: pixi's own version, a floor in `requires-pixi`
in `pyproject.toml` and an exact `pixi-version` on the `setup-pixi` step in
`.github/actions/setup/action.yml`. They move together, in Renovate's `pixi bootstrap`
group.

## The toolchain

`channel` in `rust-toolchain.toml` and `rust-version` in the root and fuzz manifests move
together, in Renovate's `rust toolchain` group. After a bump run `just install-toolchain`, then `just clippy`, because the lint
set moves with the release and `-D warnings` turns every new lint into a failure.

## Hook pins

Every remote hook in `.pre-commit-config.yaml` and `.pre-commit-fix.yaml` is pinned to a
full commit SHA, with the release tag as a comment. lychee also carries `LYCHEE_VERSION`
at the head of both its argument lists, which must match the comment; the comment beside
the hook says why. The `builtin` hygiene hooks carry no pin.

To move a pin, resolve the release's commit and replace both the SHA and the comment,
in every file that names the hook. Tags are often annotated, so ask for the commit: the
SHA a tag reference answers with names the tag object, which neither a `rev:` nor a
`uses:` line accepts. For typos, the worked example:

```console
gh api repos/crate-ci/typos/commits/<tag> --jq .sha
```

The same line, as `gh api repos/<owner>/<repo>/commits/<tag> --jq .sha`, resolves any hook
or action.

## Moving the tooling package

The documentation and agent gates and the runner
behind `just check` are console scripts of `biscuit-games-tooling`, which
`[tool.pixi.pypi-dependencies]` in `pyproject.toml` pins to a release tag of
`steven-cutting/biscuit_games_tooling`. `pixi.lock` records the commit behind the tag, and
`just lock-check` checks that the manifest's declared tag matches the lockfile. This
offline check cannot detect a remote tag being moved to a different commit.

1. Read the package's `CHANGELOG.md` in that repository for the release you are taking, and
   the level its README gives the change. A Major release can fail a tree that passed.
2. Edit the `tag` in the `biscuit-games-tooling` line of `pyproject.toml`, then relock that
   one package and read the lockfile diff before committing `pixi.lock`:

   ```console
   pixi update biscuit-games-tooling
   ```

3. Run `just sync`, because the lock installs nothing.
4. Run `just check` before committing, whatever the release level. The package supplies
   the gate runner and the validators, and the hooks that read `pyproject.toml`, which re-run the contracts but not `lock-check` or the whole gate.

A tag the package has released is never moved, so relocking without editing the tag
changes nothing.

## Moving the upstream parser

`allium-parser = "=3.6.1"` is the one exception to caret ranges
([decision 0011](../decisions/0011-exact-pin-on-allium-parser.md)). An upstream bump
is a release, not an ordinary dependency update, so Renovate leaves it alone:
[Bump upstream](bump-upstream.md) is the procedure. A bare pin bump fails `version-check`
by design.

## Actions in the workflows

`ci.yml`, `audit.yml`, `pages.yml`, `mutants.yml`, `fuzz.yml`, `release-pypi.yml` and the composite `setup` action pin every remote action in a
`uses:` line to a full commit SHA with its version comment, never to a tag. The one
exception is the local `uses: ./.github/actions/setup`, a path in this repository that
moves with the commit that calls it. The same `gh api` line resolves a tag to
the commit to paste. The toolchain the jobs build with is not pinned here: the setup
action runs `just install-toolchain`, so CI reads `rust-toolchain.toml` like everyone else.

`actionlint` runs inside `just lint`, so a malformed workflow fails locally.

## Related pages

- [Configuration](../reference/configuration.md)
- [Quality gates](../reference/quality-gates.md)
- [Maintenance](../operations/maintenance.md)
- [Decision 0004: dependency policy](../decisions/0004-dependency-policy.md)
- [Decision 0017: Renovate](../decisions/0017-renovate.md)
- [Bump upstream](bump-upstream.md)
