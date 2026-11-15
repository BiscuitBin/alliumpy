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
dependency cannot be built together. The tools are the other way round: one nixpkgs
revision in `flake.lock` fixes every tool's exact version at once
([decision 0018](../decisions/0018-nix-dev-environment.md)), and `nix/` packages at exact
versions the two nixpkgs lacks.
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
request runs the same jobs as any branch; read its diff as you would anyone's. After
editing `renovate.json`, validate it against the pinned nixpkgs' Renovate, a download on
first use:

```console
nix shell --inputs-from . nixpkgs#renovate --command renovate-config-validator --strict --no-global renovate.json
```

The hosted app's own check is that no `Action Required: Fix Renovate Configuration` issue
appears and the dashboard shows no configuration error. The dashboard's
detected-dependencies list leaves out anything a rule disables, so `allium-parser` and the
`python-version`, setup-uv and `maturin-version` inputs under `github-actions` never appear
there. That absence is the rule
working, not a failed read.

| Group | What moves |
| --- | --- |
| `crates` | `Cargo.lock` and `fuzz/Cargo.lock` within the caret ranges, or a range itself when a release falls outside it, which is the diff to read |
| `github actions` | each remote action's SHA with its version comment, in the workflows and the `setup` action |
| `rust toolchain` | `channel` in `rust-toolchain.toml` and `rust-version` in the root and fuzz manifests |
| `nix` | `flake.lock`'s inputs: nixpkgs, and with it every tool in the dev shell, and rust-overlay. The checkers' input is left to its tag's own rule |
| `uv` | the release job's `setup-uv` `version`, read from PyPI |
| `maturin` | every `maturin-version` in `release-pypi.yml`, read from PyPI |
| `python build backend` | the `maturin` range in `crates/alliumpy/pyproject.toml` |
| one per pin | `rustqual` in `nix/rustqual.nix`, the `biscuit-games-tooling` tag in `flake.nix`, and `twine` in `release-pypi.yml` |
| lock-file maintenance | the transitive closure of the lockfiles: `Cargo.lock` and `fuzz/Cargo.lock` together, and `flake.lock`. Each waits for a click, the first despite its branch's `crates` name |

Major updates open in a pull request of their own beside their group's, because
Renovate's `separateMajorMinor` takes precedence over a group. That is the major number
alone: a breaking 0.x release, such as `pyo3` 0.31, counts as minor and lands in the
`crates` group, moving the range in `Cargo.toml`. If it turns the group red, it holds up the
other crates until it is fixed, so read which crate failed.

Some of these need more than the branch shows:

- **A nixpkgs move.** The `nix` group and `flake.lock`'s maintenance move every tool in
  the dev shell at once, so one pull request can bring a new ruff, typos or markdownlint
  rule set together. Check the branch out, enter the shell, and run `just check`; fix each
  new finding at its root, and record any version that changes what a gate reports, as
  decision 0018 records the first set.
- **The checkers' tag.** Its pull request edits the ref in `flake.nix` alone, so
  `lock-check` fails it until `flake.lock` follows: run `just lock` on its branch, read the
  diff, and commit it. The rest is [Moving the tooling package](#moving-the-tooling-package).
- **rustqual.** Its pull request moves the version in `nix/rustqual.nix` and leaves the two
  hashes stale, so the dev shell fails to build until both are fixed by hand, as
  [The tools in the dev shell](#the-tools-in-the-dev-shell) describes.
- **Several relocks at once.** After merging one, rebase the next from its dashboard box
  and read its checks before merging it, so CI reads the combined lockfiles.
- **The `maturin` range.** `requires = ["maturin>=1.15,<2.0"]` is kept rather than pinned.
  The dev shell's maturin is what builds locally and in `just check`, and the release
  workflow sets `maturin-version`, so neither reads the range. It is what a user's installer
  honours when it builds the sdist; PyPI itself builds nothing. `just wheel-smoke` never
  reads it, so its colour proves nothing about a range update. Build as an installer would,
  from the branch, inside the dev shell, whose cargo is the pinned toolchain the unpacked
  sdist cannot name (network). Name the wheel's directory, because the root
  `pyproject.toml` is not a project: `uv build crates/alliumpy -o ai_tmp/sdist`.
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
  precision of the value it replaces. Prose naming the toolchain moves by hand. A new
  channel also needs a rust-overlay revision that knows it, or the dev shell fails to
  build: [The toolchain](#the-toolchain).

These stay with you:

| Pin | Why it is manual |
| --- | --- |
| `allium-parser` | Excluded. A bump is a release: [Bump upstream](bump-upstream.md) |
| the parity reference | It has no pin of its own; it moves with `allium-parser`, by the runbook |
| `python314` in `nix/dev-shell.nix` | The tooling interpreter's minor release; nixpkgs moves its patch release |
| `nextest-version` in `.config/nextest.toml` | A floor under the dev shell's cargo-nextest, raised by hand when a profile needs a newer feature and never above what `flake.lock` provides |
| `requires-python` in `crates/alliumpy/pyproject.toml`; `python_version` in `mypy.ini`; `target-version` in `ruff.toml` | `>=3.11` is the abi3 floor of [decision 0012](../decisions/0012-abi3-wheels-and-platforms.md), and the other two move with that floor |
| `python-version` inputs | `3.11` is that same floor; `3.14t` is the free-threaded build the release matrix smokes |
| the three image digests in `release-pypi.yml` | Smoke-only, never in the wheel. Bare digests suit a regex poorly, and the `python` images' tags would need a digest-only rule |
| runner labels in the release matrix | `ubuntu-22.04` and `macos-15-intel` sit under `matrix.platform.runner`, which the manager does not reach; they decide which wheels build (decision 0012) |
| the literal `15` in the `release` job | The expected file count; it moves with the matrix, not with any release |

## Check that the lockfiles still match

```console
just lock-check
```

This runs `cargo update --workspace --locked --offline`, the same line over
`fuzz/Cargo.toml`, and `nix flake metadata --no-update-lock-file --offline .`, which fails
when `flake.lock` disagrees with `flake.nix`. None of them writes. An input pointed at a
new git URL makes git try that URL before the failure. It is gate 2 of
`just check`, so a manifest edited without relocking fails the gate rather than
drifting.

## Update deliberately

```console
just lock            # relock after a manifest edit
just lock-upgrade    # move every crate to the newest version its range admits, and every flake input
```

`just lock` relocks the workspace against what the manifests state, then runs
`nix flake lock`, which locks an input `flake.nix` newly names or whose URL changed and
moves no other. It relocks `fuzz/Cargo.lock` too: the fuzz crate sits outside the
workspace (decision 0016), so its lockfile is a third pin that moves with the others,
and its path dependency on the core names no version, so a workspace version bump
leaves it stale until `just lock` runs. It is not a no-op: a dependency whose range was edited, or that is new,
resolves to the newest version its range admits, not to the version the range names.
`just lock-upgrade` moves every crate, transitive ones included, to the newest version
its range admits, in both Cargo lockfiles, which under caret ranges changes plenty, and
runs `nix flake update`, which moves nixpkgs, and with it every tool, and rust-overlay to
the head of their refs; the checkers stay on their tag. Read every lockfile diff before
accepting it. After either recipe leave the dev shell and enter it again:
`check-toolchain` refuses the stale one.

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

## The tools in the dev shell

`nix/dev-shell.nix` names every tool a recipe or hook calls, and the nixpkgs revision in
`flake.lock` decides each one's version, so the tools move together, never one at a time
([decision 0018](../decisions/0018-nix-dev-environment.md)). The narrow move is that one
input, then the whole gate on the result:

```console
nix flake update nixpkgs
```

A tool held at a version nixpkgs does not carry is packaged under `nix/` instead, as
rustqual is, on a decision record that says why. cargo-fuzz moves with nixpkgs, built
natively for each system; after a move run `just fuzz-build`, which `macos-smoke` also
runs on Apple silicon.

`nix/rustqual.nix` pins rustqual's version and two hashes: the crates.io source and the
vendored dependencies. To move it, edit `version`, set `hash` and `cargoHash` to `""`,
and build the shell; each failing build prints the right value after `got:`. Move it one
release at a time and run `just check` on each, because the tool is a gate: record any
bump that needs a suppression or threshold change, as
[decision 0007](../decisions/0007-metrics-gate.md) requires.

The bootstrap is Nix itself. Locally any Nix with flakes enabled enters the shell; in CI
the installer action's SHA in `.github/actions/setup/action.yml` moves in the
`github actions` group like every other action.

## The toolchain

`channel` in `rust-toolchain.toml` and `rust-version` in the root and fuzz manifests move
together, in Renovate's `rust toolchain` group. The dev shell reads the channel through
rust-overlay, whose locked revision must already know the release, so after a bump run
`nix flake update rust-overlay` if the shell fails to build, read the `flake.lock` diff,
enter the shell again, then run `just clippy`, because the lint set moves with the release
and `-D warnings` turns every new lint into a failure.

## Hook pins

Every hook in `.pre-commit-config.yaml` and `.pre-commit-fix.yaml` runs a binary the dev
shell provides, so the hooks carry no pin of their own: `flake.lock` pins each checker,
and they move with nixpkgs. The `builtin` hygiene hooks are part of prek.

## Moving the tooling package

The documentation and agent gates and the runner behind `just check` are console scripts
of `biscuit-games-tooling`. The `biscuit-games-tooling` input in `flake.nix` names a
release tag of `steven-cutting/biscuit_games_tooling`, and `nix/biscuit-games-tooling.nix`
builds it. `flake.lock` records the commit behind the tag and its content hash, and
`just lock-check` fails when the input's URL and the lockfile disagree. A remote tag moved
to a different commit does not change what is locked.

1. Read the package's `CHANGELOG.md` in that repository for the release you are taking, and
   the level its README gives the change. A Major release can fail a tree that passed.
2. Edit the tag in the input's `ref=refs/tags/` URL in `flake.nix`, then relock and read
   the `flake.lock` diff before committing it:

   ```console
   just lock
   ```

3. Enter the shell again, which builds the new package. `nix/biscuit-games-tooling.nix`
   relaxes the package's `uv_build` requirement by exact text, so a release that changes
   that requirement fails the build until the patch follows it.
4. Run `just check` before committing, whatever the release level. The package supplies
   the gate runner and the validators, and the hooks that read `pyproject.toml`, which re-run the contracts but not `lock-check` or the whole gate.

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
moves with the commit that calls it. To move a pin by hand, resolve the release's commit
and replace both the SHA and the comment. Tags are often annotated, so ask for the
commit: the SHA a tag reference answers with names the tag object, which a `uses:` line
does not accept.

```console
gh api repos/<owner>/<repo>/commits/<tag> --jq .sha
```

The toolchain and tools the jobs use are not pinned here: the setup action builds the dev
shell from `flake.lock`, so CI reads the same pins as everyone else.

`actionlint` runs inside `just lint`, so a malformed workflow fails locally.

## Related pages

- [Configuration](../reference/configuration.md)
- [Quality gates](../reference/quality-gates.md)
- [Maintenance](../operations/maintenance.md)
- [Decision 0004: dependency policy](../decisions/0004-dependency-policy.md)
- [Decision 0017: Renovate](../decisions/0017-renovate.md)
- [Bump upstream](bump-upstream.md)
