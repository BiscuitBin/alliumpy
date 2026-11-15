---
id: T19
title: "Nix owns the development environment: one flake for the toolchain, the tools and CI"
status: open
depends_on: [T17]
parallel_with: []
branch: claude/relaxed-dirac-mwwcf2
estimated_size: L
---

# T19: Nix owns the development environment: one flake for the toolchain, the tools and CI

## Context

Decision 0006 split the development environment between four owners: pixi installs
Python and the conda-forge tools from `pixi.lock`; rustup installs the compiler that
`rust-toolchain.toml` names, and `check-toolchain` refuses any other cargo;
cargo-binstall installs `tools.txt` and `tools-source.txt` into `.tools/bin`; and prek
clones seven hook repositories and downloads Go, Node and a rustup toolchain to build
them. CI repeats all four in `.github/actions/setup/action.yml`. A fresh machine needs
rustup, pixi and just before `just initialize` can start, and four lockfiles or pin
lists move independently.

The maintainer asked for one owner: a Nix flake, for local development on Linux x86_64
and macOS arm64, and for CI. The maintainer settled these points on 2026-11-14:

- No container image. None exists (`CONVENTIONS.md` §1 decision 5), and none is added.
  The digest-pinned smoke containers in `.github/workflows/release-pypi.yml` stay.
- One nixpkgs pin. `flake.lock` pins one nixpkgs revision, which fixes every tool
  version at once. The Rust toolchain is read from `rust-toolchain.toml`. A tool that
  nixpkgs lacks is packaged under `nix/` at an exact version. The pins that used to
  equal a local pin (uv and maturin in `release-pypi.yml`, `nextest-version` in
  `.config/nextest.toml`) become separately owned.
- The full ticket process, with decision 0018 superseding decision 0006.
- macOS is proved by a `macos-smoke` CI job on `macos-latest` (arm64), outside the
  required `check` aggregate.
- `CONVENTIONS.md` gets one amendment paragraph on this branch.
- A baseline attempt with the old toolchain, time-boxed.
- Pushing this branch is authorised once it is green locally, and so are follow-up
  fixes on it. A pull request, a tag or a settings change still needs asking.

## Goal

A clone with Nix and nothing else runs `nix develop`, then `just initialize`, then
`just check`. The run ends with `All checks passed and the worktree is unchanged.`, and
no tool resolves from outside the Nix store. CI runs the same gates in the same shell.
`macos-smoke` proves the shell builds, tests and smokes the wheel on Apple silicon.

## Non-goals

- A container image of any kind.
- Any change to the build, smoke or publish jobs of `release-pypi.yml`. One stale
  comment is the only edit there.
- An upstream bump, a version change or a new gate. The gate count stays 22.
- Repackaging the parity reference. `install-parity-reference` keeps its `cargo
  install` with the flake's cargo (open point 1).
- Making `macos-smoke` required.
- Platforms beyond `x86_64-linux` and `aarch64-darwin`.

## Files touched

| Path | Class | Content |
| --- | --- | --- |
| `flake.nix`, `flake.lock` | new | the inputs, the dev shell, `packages.dev-shell`, `checks`, `formatter` |
| `nix/dev-shell.nix`, `nix/rustqual.nix`, `nix/biscuit-games-tooling.nix` | new | the shell and the two packages nixpkgs lacks |
| `scripts/pre-commit-hook.sh` | new | the path-free hook shim `install-hooks` copies |
| `.envrc` | new | `use flake`, opt-in through direnv |
| `docs/decisions/0018-nix-dev-environment.md` | new | the decision |
| `tickets/T19-nix-dev-environment.md` | ticket | this file |
| `pixi.lock`, `tools.txt`, `tools-source.txt` | deleted | replaced by `flake.lock` and `nix/` |
| `Justfile` | shared, own lines | the header, gate 1, the lock recipes, `install-hooks`, the Python recipes, `metrics`, `fmt-check`, `format`; `install-toolchain` and `install-tools` removed |
| `pyproject.toml` | shared, own lines | the `[tool.pixi.*]` tables and `[project]` removed; `[tool.biscuit-games-tooling]` kept |
| `scripts/initialize.sh`, `scripts/version_check.py` | shared, own lines | rustup and pixi wording and steps |
| `.pre-commit-config.yaml`, `.pre-commit-fix.yaml` | shared, own lines | remote hooks as `language: system`, excludes |
| `.github/actions/setup/action.yml` | shared, own lines | Nix install, store cache, shell build, rust-cache, sync |
| `.github/workflows/ci.yml`, `audit.yml`, `fuzz.yml`, `mutants.yml`, `pages.yml` | shared, own lines | the job default shell; `macos-smoke`; timeouts |
| `.github/workflows/release-pypi.yml` | shared, own lines | one comment |
| `renovate.json` | shared, own lines | the pixi, tool-list and hook-revision machinery out; the `nix` manager in |
| `.config/nextest.toml`, `crates/alliumpy/pyproject.toml`, `mypy.ini` | shared, own lines | comments |
| `.gitignore`, `.gitattributes`, `lychee.toml`, `taplo.toml`, `_typos.toml`, `.markdownlint-cli2.jsonc` | shared, own lines | `.pixi` out; `.nix`, `.direnv`, `result` in |
| `docs/how-to/develop-locally.md` | shared, own lines | rewritten around the flake |
| `docs/tutorials/first-change.md`, `docs/reference/commands.md`, `docs/reference/configuration.md`, `docs/reference/quality-gates.md`, `docs/reference/testing.md` | shared, own lines | the recipes, files, variables and gate 1 that moved |
| `docs/how-to/maintain-dependencies.md`, `docs/how-to/test-and-debug.md`, `docs/how-to/bump-upstream.md` | shared, own lines | how the pins move; tool paths |
| `docs/operations/troubleshooting.md`, `docs/operations/maintenance.md` | shared, own lines | the new failure modes; the routine |
| `docs/project/repository-map.md`, `docs/explanation/packaging.md`, `docs/explanation/security-model.md` | shared, own lines | the tree, the manifests and the trust roots |
| `docs/decisions/0002`, `0005`, `0006`, `0007`, `0008`, `0012`, `0016`, `0017`, `docs/decisions/README.md`, `docs/manifest.yml` | shared, own lines | superseded and amended markers; the index row; the manifest entry |
| `AGENTS.md`, `.agents/skills/project-check/SKILL.md`, `.agents/skills/fix-quality/SKILL.md` | shared, own lines | the project map, the network recipes, the prerequisites; the frontmatter and bridges are unchanged |
| `README.md`, `SECURITY.md`, `CHANGELOG.md` | shared, own lines | Contribute, the tool wording, `[Unreleased]` |
| `tickets/README.md`, `tickets/CONVENTIONS.md` | shared, own lines | the index row and the pixi sentence; one amendment paragraph |

## Steps

1. Baseline. Run the old `just initialize` and `just check` on the untouched worktree
   at `545e7f2`, with the pinned pixi under `ai_tmp/`. Record the last line and every
   tool version, then remove `.pixi/` and `.tools/`.
2. This ticket and the `CONVENTIONS.md` amendment.
3. `flake.nix` and `nix/dev-shell.nix` with the nixpkgs tools, then `nix flake lock` and
   `nix develop --command true`. Record each tool version for decision 0018's table.
4. `nix/biscuit-games-tooling.nix`, `nix/rustqual.nix` and the Python environment.
5. The `Justfile` header and `check-toolchain` with its four negative controls. Then
   the lock recipes, `scripts/initialize.sh`, `pyproject.toml`, the deletions, ignores
   and excludes. Run the gates in order through `deps-unused`.

   **Adversarial review** (`CONVENTIONS.md` §14), the first checkpoint, over the flake,
   the `Justfile` header and gate 1. Every later step builds on this design.

6. The Python recipes, from `py-lint` to `version-check`.
7. The hook configurations and the shim. Run `just lint`, run `just fix` on a scratch
   copy, and make a real commit from a bare shell in a scratch clone, once accepted and
   once blocked.
8. Fallout from moved tool versions. Fix each finding at its root and record it for
   decision 0018.
9. The CI files and `renovate.json`.

   **Adversarial review** (`CONVENTIONS.md` §14), the second checkpoint, over the
   workflows, the composite action and `renovate.json`, before the push.

10. Documents, decision 0018, `AGENTS.md` and the two skills: `just check-docs` and
    `just check-agents`.
11. The proofs under Verification.

    **Adversarial review** (`CONVENTIONS.md` §14), the third checkpoint, over the
    lane's whole diff, before the final commit.

12. Push the branch. Collect the CI and `macos-smoke` evidence, and fix forward on this
    branch.

## Acceptance criteria

1. `nix develop --command just check` ends with
   `All checks passed and the worktree is unchanged.`, and `git status --short` prints
   nothing, in a shell whose `PATH` holds nothing from `$HOME`.
2. `just check-toolchain` exits 2 and names the cause in each of four cases: a rustup
   proxy first on `PATH`, a uv from `~/.local/bin` first on `PATH`, a stale shell, and
   a run outside the shell.
3. `just lock-check` fails on a `flake.nix` that disagrees with `flake.lock`, and
   rewrites nothing.
4. `just check` passes under `unshare -rn`, with both negative-control requests
   failing (`CONVENTIONS.md` §11).
5. A fresh clone passes `just initialize` and `just check`.
6. `nix flake check` passes, and the `aarch64-darwin` shell evaluates.
7. CI is green on the pushed branch, including `wheel-smoke-py311` on the wheel the Nix
   shell built and `macos-smoke`.
8. Every handbook page, decision, skill and `AGENTS.md` line that named the old
   mechanism names the new one. `just check-docs` and `just check-agents` pass.

## Verification

```console
nix flake check --no-update-lock-file
nix eval --raw .#devShells.aarch64-darwin.default.drvPath
env -i HOME="$HOME" TERM=dumb PATH=/nix/var/nix/profiles/default/bin nix develop --no-update-lock-file --command just check
git status --short
nix develop --command unshare -rn sh -c 'curl -fsS --max-time 10 https://static.rust-lang.org; curl --noproxy "*" -fsS --max-time 10 https://1.1.1.1; just check'
```

## Hand-back notes

Written at the end of the ticket. Each quoted output is headed by the commit it ran at.

## Open points

1. Packaging the parity reference in the flake, so that CI substitutes it rather than
   building it.
