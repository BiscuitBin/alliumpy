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
dependency cannot be built together. The tools are the other way round: `flake.nix`
names them and `flake.lock`, committed beside it, pins one nixpkgs revision that decides
every tool's version at once ([decision 0018](../decisions/0018-nix-owns-the-tools.md)).
Renovate proposes moves to most of these pins, and the upstream parser is excluded;
nothing merges itself.

## What the updater proposes

`renovate.json` at the repository root names every pin Renovate reads
([decision 0017](../decisions/0017-renovate.md)). The `crates` and `github actions` groups
open a pull request weekly on their own, once a release is seven days old. Every other
update waits for a click on the dependency dashboard, including anything a future file or
manager brings in, because held is the default. There is one exception: a vulnerability-fix
pull request skips that approval and the seven days, and can open unasked, because
vulnerability alerts are enabled on this repository. Nothing merges itself. A Renovate pull
request runs the same jobs as any branch; read its diff as you would anyone's. There is no
local validator: after editing `renovate.json`, the check is that no `Action Required: Fix
Renovate Configuration` issue appears and the dashboard shows no configuration error. The
dashboard's detected-dependencies list leaves out anything a rule disables, so
`allium-parser` and the `python-version`, setup-uv and `maturin-version` inputs under
`github-actions` never appear there; setup-uv's and maturin's appear under the regex
managers instead. That absence is the rule working, not a failed read.

| Group | What moves |
| --- | --- |
| `crates` | `Cargo.lock` and `fuzz/Cargo.lock` within the caret ranges, or a range itself when a release falls outside it, which is the diff to read |
| `github actions` | each remote action's SHA with its version comment, in the workflows and the `setup` action |
| `rust toolchain` | `channel` in `rust-toolchain.toml` and `rust-version` in the root and fuzz manifests |
| `nix flake` | the flake's inputs in `flake.lock` (`nixpkgs`, `rust-overlay`, `crane`), and with them every tool the dev shell holds, through the `nix` manager, which Renovate calls beta and which is enabled explicitly |
| `release uv` | the release job's `setup-uv` `version`, from uv's GitHub releases |
| `release maturin` | every `maturin-version` in `release-pypi.yml`, from PyPI |
| `python build backend` | the `maturin` range in `crates/alliumpy/pyproject.toml` |
| one per pin | `twine` in `release-pypi.yml` |
| lock-file maintenance | the transitive closure of the lockfiles: `Cargo.lock` and `fuzz/Cargo.lock` together, and `flake.lock`. Each waits for a click, the first despite its branch's `crates` name |

Major updates open in a pull request of their own beside their group's, because
Renovate's `separateMajorMinor` takes precedence over a group. That is the major number
alone: a breaking 0.x release, such as `pyo3` 0.31, counts as minor and lands in the
`crates` group, moving the range in `Cargo.toml`. If it turns the group red, it holds up the
other crates until it is fixed, so read which crate failed.

Some of these need more than the branch shows:

- **`flake.lock`.** One update moves every tool at once: the cargo tools, Python and its
  packages, prek and the checkers, maturin and uv. Read it as a tool upgrade (see
  [A flake update](#a-flake-update) below). Whether the hosted app can relock a flake
  itself was not proven when this was written: the `nix` manager is beta, and Renovate's
  documentation does not say the hosted app has Nix. If its branch fails `lock-check`, or
  no `nix flake` entry appears on the dashboard, run the update by hand instead.
- **The `maturin` range.** `requires = ["maturin>=1.15,<2.0"]` is kept rather than pinned.
  The dev shell's maturin is what builds locally and in `just check`, and the release workflow sets
  `maturin-version`, so neither reads the range. It is what a user's installer honours when
  it builds the sdist; PyPI itself builds nothing. `just wheel-smoke` never reads it, so its
  colour proves nothing about a range update. Build as an installer would, from the branch
  (network). Name the wheel's project, because the root `pyproject.toml` is
  `alliumpy-tooling`. Inside the dev shell the pinned compiler is already first on
  `PATH`, so the unpacked sdist, which has no `rust-toolchain.toml`, builds with it:
  `uv build crates/alliumpy -o ai_tmp/sdist`.
  It must exit 0, ending with `Successfully built` lines for the `.tar.gz` and the `.whl`.
- **`serde` and `serde_json`.** The vendored command depends on both, so an update can
  change the `allium` command's output while upstream's reference keeps its own. Read the
  `parity` job on that branch; CI runs it on every pull request.
- **`release-pypi.yml`.** It does not run on pull requests, so an update to its actions,
  inputs or `twine` passes CI without running. The
  [release rehearsal](release.md#the-rehearsal) is what first exercises it.
- **A toolchain update.** clippy's lint set moves with the release, so a red `rust` job is
  often new lints; check the branch out, run `just clippy` and fix what it finds.
  `rust-version` moves only on a minor release, because its versioning keeps the
  precision of the value it replaces. Prose naming the toolchain moves by hand. The dev
  shell reads the channel from the file, so the branch's CI already runs the new
  compiler.

These stay with you:

| Pin | Why it is manual |
| --- | --- |
| `allium-parser` | Excluded. A bump is a release: [Bump upstream](bump-upstream.md) |
| the parity reference | `alliumCliVersion` and its two hashes in `flake.nix` move with `allium-parser`, by the runbook; no manager reads them |
| rustqual | `rustqualVersion` and its two hashes in `flake.nix`: a gate tool built from source, moved one release at a time as [decision 0007](../decisions/0007-metrics-gate.md) requires; no manager reads them |
| the tooling package | `rev` and `hash` of `biscuit-games-tooling` in `flake.nix`; see [Moving the tooling package](#moving-the-tooling-package) |
| `nextest-version` | A floor in `.config/nextest.toml`, never above the nextest `flake.lock` provides; moved by hand when a newer feature is needed |
| `requires-python`, both; `python_version` in `mypy.ini`; `target-version` in `ruff.toml` | `>=3.14` follows the tooling interpreter; `>=3.11` is the abi3 floor of [decision 0012](../decisions/0012-abi3-wheels-and-platforms.md), and the other two move with that floor |
| `python-version` inputs | `3.11` is that same floor; `3.14t` is the free-threaded build the release matrix smokes |
| the three image digests in `release-pypi.yml` | Smoke-only, never in the wheel. Bare digests suit a regex poorly, and the `python` images' tags would need a digest-only rule |
| runner labels in the release matrix | `ubuntu-22.04` and `macos-15-intel` sit under `matrix.platform.runner`, which the manager does not reach; they decide which wheels build (decision 0012) |
| the literal `15` in the `release` job | The expected file count; it moves with the matrix, not with any release |

## Check that the lockfiles still match

```console
just lock-check
```

This runs `cargo update --workspace --locked --offline`, the same line over
`fuzz/Cargo.toml`, and `nix flake metadata --offline --no-update-lock-file`, none of
which writes. It is gate 2 of
`just check`, so a manifest edited without relocking fails the gate rather than
drifting.

## Update deliberately

```console
just lock            # relock after a manifest edit
just lock-upgrade    # move every crate, and every flake input, to the newest allowed
```

`just lock` relocks the workspace against what the manifests state, then runs
`nix flake lock`, which adds an input `flake.nix` names and `flake.lock` lacks and moves
nothing else. It relocks `fuzz/Cargo.lock` too: the fuzz crate sits outside the
workspace (decision 0016), so its lockfile is a third pin that moves with the others,
and its path dependency on the core names no version, so a workspace version bump
leaves it stale until `just lock` runs. It is not a no-op: a dependency whose range was edited, or that is new,
resolves to the newest version its range admits, not to the version the range names.
`just lock-upgrade` moves every crate, transitive ones included, to the newest version
its range admits, in both Cargo lockfiles, which under caret ranges changes plenty, and
runs `nix flake update`, which moves every input to its branch's head and so every tool.
Read both diffs before accepting them; the flake's is [a flake update](#a-flake-update).

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

## A flake update

`flake.lock` pins `nixpkgs`, `rust-overlay` and `crane` each to a commit and a content
hash. Every tool's version follows from the `nixpkgs` revision, so there is no line per
tool to edit. To move them, run, inside the dev shell (network):

```console
just lock-upgrade
```

or `nix flake update nixpkgs` for that one input. Then leave the shell and enter it again,
so the new tools are the ones on `PATH`, and check:

1. Which tools moved: `nix store diff-closures` between the old and the new shell, or
   each tool's `--version`. A new ruff, typos, markdownlint or cargo tool often finds
   something new.
2. `just check`. Fix what the new versions find, as for any upgrade.
3. Python: the dev shell's interpreter is the newest `python314` patch release nixpkgs
   carries. A move to 3.15 is a decision, not an update: it changes `python314` in
   `flake.nix`.
4. nextest: the shell's must stay at or above `nextest-version` in
   `.config/nextest.toml`.
5. `just nix-flake-check` and `just nix-wheel`, because the flake's own builds move too.

**Holding one tool back.** When nixpkgs moves a tool somewhere unwanted, keep the rest
and override that one in `flake.nix`: build it at the version wanted, as the flake already
does for rustqual, with its source and vendor hashes, and say why in a comment beside it.
A second, older nixpkgs input for one tool also works, at the cost of a second nixpkgs in
the lock. Either is a decision-0004 note. Remove the override when nixpkgs catches up.

The compiler is not in nixpkgs: `rust-overlay` builds the exact channel
`rust-toolchain.toml` names, so a flake update moves the overlay's manifests, never the
compiler.

## The toolchain

`channel` in `rust-toolchain.toml` and `rust-version` in the root and fuzz manifests move
together, in Renovate's `rust toolchain` group. After a bump leave the dev shell and enter
it again, which fetches the new compiler, then run `just clippy`, because the lint set
moves with the release and `-D warnings` turns every new lint into a failure. If the new
channel is newer than the locked `rust-overlay` knows, run `nix flake update rust-overlay`
first.

## Hook pins

There are none. Every hook in `.pre-commit-config.yaml` and `.pre-commit-fix.yaml` is a
local or builtin hook that runs a tool the dev shell holds, so a hook's version is that
tool's, and moves with `flake.lock`. Actions and other repositories' commits still
resolve with `gh api repos/<owner>/<repo>/commits/<tag> --jq .sha`, which asks for the
commit rather than an annotated tag's object.

## Moving the tooling package

The documentation and agent gates and the runner behind `just check` are console scripts
of `biscuit-games-tooling`, which `flake.nix` builds from
`steven-cutting/biscuit_games_tooling` at a commit (`rev`) with a content hash (`hash`).
No Renovate manager reads them: the hash cannot be computed without Nix, so a bump is by
hand.

1. Read the package's `CHANGELOG.md` in that repository for the release you are taking, and
   the level its README gives the change. A Major release can fail a tree that passed.
2. Resolve the release tag's commit with
   `gh api repos/steven-cutting/biscuit_games_tooling/commits/<tag> --jq .sha`, put it in
   `rev`, and set `hash` to an empty string. Entering the shell then fails and prints the
   hash it got; put that in `hash`. Update the comment naming the tag.
3. Leave the shell and enter it again.
4. Run `just check` before committing, whatever the release level. The package supplies
   the gate runner and the validators.

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
the commit to paste. The toolchain the jobs build with is not pinned here: every job runs
in the dev shell, so CI reads `rust-toolchain.toml` and `flake.lock` like everyone else.

`actionlint` runs inside `just lint`, so a malformed workflow fails locally.

## Related pages

- [Configuration](../reference/configuration.md)
- [Quality gates](../reference/quality-gates.md)
- [Maintenance](../operations/maintenance.md)
- [Decision 0004: dependency policy](../decisions/0004-dependency-policy.md)
- [Decision 0017: Renovate](../decisions/0017-renovate.md)
- [Bump upstream](bump-upstream.md)
