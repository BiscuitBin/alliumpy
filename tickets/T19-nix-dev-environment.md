---
id: T19
title: "Nix owns the development environment: one flake for the toolchain, the tools and CI"
status: done
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
| `Justfile` | shared, own lines | the header, gate 1, `sync` and the lock recipes, `install-hooks`, the Python recipes and `wheel`, `parity`'s interpreter and dependency on `py-develop`, `metrics`, `fmt-check`, `format`, and the comments of `fuzz`, `mutants` and `snapshots-check` that named the old tools; `install-toolchain` and `install-tools` removed |
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
| `docs/how-to/maintain-dependencies.md`, `docs/how-to/test-and-debug.md`, `docs/how-to/bump-upstream.md`, `docs/how-to/install-and-run.md` | shared, own lines | how the pins move; tool paths and the interpreter |
| `docs/operations/troubleshooting.md`, `docs/operations/maintenance.md` | shared, own lines | the new failure modes; the routine |
| `docs/project/repository-map.md`, `docs/explanation/packaging.md`, `docs/explanation/security-model.md` | shared, own lines | the tree, the manifests and the trust roots |
| `docs/decisions/0002`, `0005`, `0006`, `0007`, `0008`, `0012`, `0016`, `0017`, `docs/decisions/README.md`, `docs/manifest.yml`, `docs/README.md` | shared, own lines | superseded and amended markers; the index row; the manifest entry; the map's link |
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
2. `just check-toolchain` exits 2 and names the cause when a rustup proxy, a uv from
   `~/.local/bin` or a tool from another store path is first on `PATH`, when the shell is
   stale, and when `ALLIUMPY_DEV_SHELL` is set outside the shell. Outside the shell every
   recipe refuses before it runs, with just's own exit status 1 and the message naming
   `nix develop`.
3. `just lock-check` fails on a `flake.nix` that disagrees with `flake.lock`, and
   rewrites nothing.
4. `just check` passes with the network denied at the OS level, with both
   negative-control requests failing (`CONVENTIONS.md` §11). On a single-user Nix store,
   as in T19's container, the denial is `unshare -n` run as root: `unshare -rn` maps root
   to an unprivileged user, and Nix then cannot write the store it copies the flake into,
   which fails `lock-check` for a reason that is not the network.
5. A fresh clone passes `just initialize` and `just check`.
6. `nix flake check` passes, and the `aarch64-darwin` shell evaluates.
7. CI is green on the pushed branch, including `wheel-smoke-py311` on the wheel the Nix
   shell built and `macos-smoke`.
8. Every handbook page, decision, skill and `AGENTS.md` line that named the old
   mechanism names the new one. `just check-docs` and `just check-agents` pass.

## Verification

```console
nix flake check --no-update-lock-file
nix flake check --no-update-lock-file --all-systems --no-build
nix eval --raw .#devShells.aarch64-darwin.default.drvPath
env -i HOME="$HOME" TERM=dumb PATH=/nix/var/nix/profiles/default/bin nix develop --no-update-lock-file --command just check
git status --short
```

The offline run checks each control's exit status, so a missing `curl` cannot pass for a
refused request (`curl` is the host's, not the shell's):

```sh
nix develop --no-update-lock-file --command unshare -n sh -c '
  command -v curl >/dev/null || { echo "no curl: the controls cannot run"; exit 3; }
  if curl -fsS --max-time 10 https://static.rust-lang.org >/dev/null; then echo "control 1 reached the network"; exit 3; fi
  if curl --noproxy "*" -fsS --max-time 10 https://1.1.1.1 >/dev/null; then echo "control 2 reached the network"; exit 3; fi
  just check'
```

## Hand-back notes

Written at the end of the ticket. Each quoted output is headed by the commit it ran at.

### Departures

- The branch is `claude/relaxed-dirac-mwwcf2`, which the session's harness required,
  not `ticket/t19-nix-dev-environment` (`CONVENTIONS.md` §11).
- `tickets/CONVENTIONS.md` gained one amendment paragraph on this lane branch, which the
  maintainer approved on 2026-11-14 (its authority paragraph routes changes through
  `main`).
- The offline proof uses `unshare -n` as root, not `unshare -rn` (acceptance criterion 4).
- Checkpoints 1 and 2 ran as one round, over the flake, the `Justfile`, the hooks, CI and
  Renovate together, after step 9 rather than at step 5, because all of that design was
  in place by then.
- Triage (§14 phase 2) was done by the executing agent, which checked each finding by
  command or by reading the pinned source, not by separate subagents. The verdicts are in
  `ai_tmp/review/T19-1/verdicts.md` and `ai_tmp/review/T19-2/verdicts.md`.

### Baseline, at `545e7f2` (the untouched worktree)

The old toolchain could not reach a green `just check` in this container. pixi v0.84.1
(release archive, SHA-256 `c81a1659…454a`, matching its published checksum) installed
the environment, and `just initialize` then stopped at `install-tools`:

```text
cargo-binstall:  WARN resolve: Error while checking fetcher QuickInstall: Failed to render template: Context: 'GraphQL API', err: 'Remote Error: could not POST https://api.github.com/graphql: HTTP status client error (403 Forbidden) for url (https://api.github.com/graphql)'
  × For crate cargo-fuzz: Fallback to cargo-install is disabled
error: recipe `install-tools` failed on line 58 with exit code 94
```

With the remaining first-run steps run by hand (`just sync`, `just install-hooks`),
`just check` stopped at gate 3 for the same reason, in the lychee hook's own
cargo-binstall download:

```text
==> just lint
lychee...................................................................Failed
error: recipe `check` failed on line 406 with exit code 1
```

Each other gate, run alone on the old toolchain: `fmt-check`, `toml-check`, `clippy`,
`test-doc`, `coverage` (lines 92.14%), `doc`, `deny`, `deps-unused`, `py-lint`,
`py-typecheck`, `py-test` (19 passed, 51 skipped), `py-stubtest`, `wheel-smoke`,
`version-check`, `check-agents` and `snapshots-check` exited 0; `check-docs` failed on
the lychee hook as above; `metrics` and `features` could not run, because rustqual and
cargo-hack could not be installed. The tool versions are decision 0018's "Under 0006"
column, read from the pixi environment's binaries.

### Final evidence, at `110807a`

A fresh clone (`git clone --no-hardlinks`), an empty `CARGO_HOME`, and nothing from
`$HOME` on `PATH`
(`env -i HOME=… TERM=dumb CARGO_HOME=<empty> PATH=/nix/var/nix/profiles/default/bin`):

```text
=== 1. fresh clone, empty CARGO_HOME: just initialize
initialize rc=0
Ready. Next: just check.
Nothing has been formatted, staged, committed, tagged, or pushed.
=== 2. just check, nothing from HOME on PATH
check rc=0
All checks passed and the worktree is unchanged.
--- git status --short:
--- (end status)
```

Core line coverage in that run: `92.14%`, as at the baseline.

Offline (acceptance criterion 4), the same clone, with the ticket's script under
`unshare -n`:

```text
curl: (6) Could not resolve host: static.rust-lang.org
control 1 refused
curl: (7) Failed to connect to 1.1.1.1 port 443 after 0 ms: Couldn't connect to server
control 2 refused
All checks passed and the worktree is unchanged.
--- git status --short:
--- (end status)
```

The wheel that run built (`alliumpy-3.6.1-cp311-abi3-manylinux_2_34_x86_64.whl`): no
RUNPATH or RPATH in the extension, and it installs and runs in `/usr/bin/python3.11`,
Ubuntu's own interpreter outside Nix (`smoke.py`, `allium --version` printing
`allium 3.6.1 (language versions: 1, 2, 3)`, and `allium check` on the clean fixture,
exit 0).

Parity, outside `just check`, in the same clone: `just install-parity-reference` (network,
crates.io) built `allium-cli` 3.6.1 with the flake's cargo, then `just parity` reported
202 `same` cases, the positive control and both negative controls fired, and
`test_cli.py` gave `51 passed`; `just version-check` then printed
`version-check: the reference prints the same: allium 3.6.1 (language versions: 1, 2, 3)`.

Gate 1's controls (acceptance criterion 2), each `exit 2` with its cause:

```text
check-toolchain: cargo resolves to /root/.cargo/bin/cargo, not the flake's toolchain
check-toolchain: uv resolves to /root/.local/bin/uv, not the dev shell
check-toolchain: git resolves to /nix/store/raag8qjvm4gxm451hfm7qb6xjas4yig7-git-minimal-2.56.0/bin/git, not the dev shell
check-toolchain: the dev shell is stale: flake.nix, flake.lock, nix/ or rust-toolchain.toml changed since it was entered; leave it and run nix develop again
check-toolchain: ./rust-toolchain.toml is missing; the dev shell was built from it
check-toolchain: not in the dev shell: ALLIUMPY_DEV_SHELL is set, but the variables the shell exports are not; run nix develop
```

Outside the shell, just itself refuses with exit 1:

```text
error: not in the dev shell: run `nix develop`, or `nix develop --command just <recipe>` (docs/how-to/develop-locally.md)
```

The first two cases and the stale case were run before the first review, the others after
it; the gate script they exercise last changed in `4e4c14b`, and the full `just check`
above runs it through `bg-project-check`.

`lock-check` (acceptance criterion 3): with an extra input added to `flake.nix`,
`nix flake metadata --no-update-lock-file --offline .` exited 1 with
`… while updating the lock file of flake 'git+file:///home/user/alliumpy'`, and
`flake.lock` was byte-identical afterwards (`cmp`).

The hook (step 7): installed by `just install-hooks` in a scratch clone, a commit from
`env -i HOME=… PATH=/usr/bin:/bin` was accepted, with only the staged file checked; one
staging a private-key line was blocked by `detect private key` and `ripsecrets`, with an
unstaged typo left alone; and on a branch at `545e7f2`, from both a bare shell and a dev
shell, the commit was blocked with
`pre-commit: <checkout> has no flake.nix, so it predates the dev shell,`. `just fix` on a
clean clone changed nothing.

`nix flake check --no-update-lock-file` and `--all-systems --no-build` passed, and
`nix eval --raw .#devShells.aarch64-darwin.default.drvPath` printed a derivation. That is
evaluation only: nothing was built for macOS here. `renovate-config-validator --strict`
(Renovate 44.216.0, from the pinned nixpkgs) validated `renovate.json`; its six regex
managers each matched their files in a local test.

### Adversarial reviews

Each checkpoint used two fresh-context subagents on Claude Code with
`claude-opus-5-5`, one per lens. Raw findings are under `ai_tmp/review/` and are not
committed.

- **Checkpoint 1** (`545e7f2..a4427d1`). Conformance: C1 to C10, none high. Breakage: B1
  to B11, none high. Every finding was valid, B5 in part. All were applied in `1602720`,
  except C10, which was the documentation step itself. Notable fixes:
  - B1: the hook on pre-flake branches.
  - B3: gate 1 now checks the shell's own packages.
  - B4: the offline proof uses `unshare -n`.
  - B6: RUNPATH. Investigating B6 showed that the baseline's release artefacts had been
    reused, so the final evidence comes from a fresh clone.
- **Checkpoint 3** (`545e7f2..1602720`). Conformance: F-C1 to F-C12. Breakage: F-B1 to
  F-B8, with one high finding, F-B1.
  - F-B1 was a regression from B3's fix. The checkers' wrapped scripts put two more store
    directories first on `PATH`. The fresh-clone proof found it first, and `fad0934` and
    `e78a472` fixed it.
  - F-C10 was invalid. Renovate's nix extractor matches the `channels.nixos.org` input
    explicitly.
  - The rest were valid and applied in `4e4c14b` and `110807a`.
  - The final evidence above re-runs everything after the high fix. No third round ran
    (§14, two at most).

### What only CI can show, not yet run

`ci.yml` runs on pull requests, pushes to `main` and a manual dispatch, so pushing this
branch started no run. The cold-store run, the store cache hit on a second run, rust-cache
finding the flake's rustc, `wheel-smoke-py311` on the CI-built wheel, and `macos-smoke`
all wait for a dispatch or a pull request, which need the maintainer's authorisation.

## Open points

1. Packaging the parity reference in the flake, so that CI substitutes it rather than
   building it.
2. The CI evidence above: a `ci.yml` dispatch on this branch, or a pull request, then the
   run URLs and commits recorded here.
3. macOS: `macos-smoke` is the first build of the aarch64-darwin shell anywhere. rustqual
   and the checkers are built there from source. If the job is green, decision 0016's
   Rosetta prerequisite can be retired with evidence.
4. Renovate's dependency dashboard after merge, to confirm that the `nix` manager lists
   nixpkgs and rust-overlay, and that the regex managers list rustqual, the checkers' tag
   and the release pins.
5. actionlint does not shellcheck `run:` blocks under the dev-shell default shell
   (decision 0018). A wrapper that actionlint recognises would restore that check.
