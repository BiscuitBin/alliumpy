---
title: "Decision 0018: Nix owns the development environment"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_dev_environment"]
requires: []
---

# Decision 0018: Nix owns the development environment

## Context

[Decision 0006](0006-tool-manager.md) gave the environment four owners:

- pixi installed Python and the conda-forge tools from `pixi.lock`.
- rustup installed the compiler `rust-toolchain.toml` names, and gate 1 refused any other
  cargo.
- cargo-binstall installed `tools.txt` and `tools-source.txt` into `.tools/bin`.
- prek cloned seven hook repositories and downloaded Go, Node and a rustup toolchain to
  build them.

A fresh machine needed rustup, pixi and just before `just initialize` could start. CI
repeated all four steps in its setup action, and four pin lists moved independently.

Two of the four owners fetched release assets through GitHub's API: cargo-binstall for
`tools.txt`, and the lychee hook for its binary. Where that API is refused, as it was
behind T19's proxy, `just initialize` stopped at `install-tools` and gate 3 failed on the
lychee hook. The old gate was therefore not reproducible in a network that could reach
every package registry. cargo-fuzz also shipped no arm64 macOS binary, so the
maintainer's platform needed Rosetta 2 for two recipes.

The maintainer asked for one owner, for local development on Linux x86_64 and macOS
arm64 and for CI.

## Decision

**A Nix flake owns the whole environment.** `flake.nix` defines one dev shell, and
`nix/dev-shell.nix` lists what goes in it. `flake.lock` is its only pin. The shell holds
the compiler, Python, the shared checkers, every tool a recipe or hook calls, and the C++
compiler libFuzzer needs.

- **nixpkgs is one pin.** One revision of `nixpkgs-unstable`, fetched from
  `channels.nixos.org`, fixes every tool's version at once. Those builds are already on
  `cache.nixos.org` for both platforms. The stable channel was too old: its uv and mypy
  are several releases behind the pins 0006 had.
- **`rust-toolchain.toml` stays the toolchain's owner.** rust-overlay reads it, channel
  and components alike, so the channel is still written once.
- **Two tools are packaged here, at exact versions.** nixpkgs lacks rustqual and the
  shared checkers. `nix/rustqual.nix` builds rustqual 1.8.3 from crates.io against two
  pinned hashes. `nix/biscuit-games-tooling.nix` builds the checkers from the flake
  input at their release tag.
- **Systems** are `x86_64-linux` and `aarch64-darwin`, the two with evidence.

**The recipes require the shell rather than construct it.** The `Justfile` puts nothing
on `PATH`. Outside the shell, every recipe refuses before it runs. Agents and scripts
spell a run `nix develop --command just <recipe>`. Gate 1, `check-toolchain`, proves
three things:

- The shell is the one the committed files produce. It compares a digest of
  `flake.nix`, `flake.lock`, `rust-toolchain.toml` and `nix/`.
- cargo, rustc, rustfmt and clippy resolve inside the flake's toolchain, and every
  other tool a gate calls resolves inside the Nix store.
- rustc and cargo report the pinned channel.

A rustup proxy, a Homebrew cargo or a uv in `~/.local/bin` is refused by path,
wherever it sits on `PATH`.

**The lockfile recipes and the gate follow the flake:**

- Gate 2 checks `flake.lock` against `flake.nix` offline, without writing.
- `just lock` and `just lock-upgrade` run `nix flake lock` and `nix flake update`.
- `just sync` records the shell as a garbage-collector root under `.nix/`.
- `install-toolchain` and `install-tools` are gone.

**Hooks and CI use the shell's binaries:**

- The hooks run those binaries as system hooks, with each upstream hook's id, file
  selection and arguments. Nothing is cloned, and `install-hooks` is offline.
- The hook itself is a committed shim, `scripts/pre-commit-hook.sh`, which names no
  store path.
- CI installs Nix, caches the store and runs every gate step inside the shell.
- `macos-smoke` builds, tests, fuzz-builds and smokes the wheel on Apple silicon. It
  sits outside the required check.

**Pins that used to equal a local pin are now owned apart:**

- `nextest-version` in `.config/nextest.toml` is a floor, raised by hand.
- The release workflow's uv and maturin are their own pins, which Renovate reads from
  PyPI.
- The release builds and their smoke containers are unchanged.

**No container image.** None existed (`tickets/CONVENTIONS.md` §1 decision 5), and this
decision adds none.

## Consequences

The ones that hurt come first.

- **Every tool moves at once.** A nixpkgs bump moves every tool together. Renovate holds
  that bump as one pull request, which needs `just check` run on it before it merges.
  Tools no longer move one version at a time.
- **The shell starts with different tool versions.** Each move below is a change to
  the gate this record owns. At T19, every gate that ran under 0006's tools passed
  identically under these: no new finding and no changed figure, and core line
  coverage was 92.14% under both.

  | Tool | Under 0006 | Under 0018 |
  | --- | --- | --- |
  | Python | 3.14.10 | 3.14.10 |
  | just | 1.58.0 | 1.59.0 |
  | prek | 0.5.3 | 0.5.10 |
  | cargo-nextest | 0.9.146 | 0.9.149 |
  | cargo-insta | 1.48.0 | 1.49.0 |
  | cargo-shear | 1.13.4 | 1.14.0 |
  | cargo-hack | 0.6.45 | 0.6.46 |
  | maturin | 1.16.0 | 1.15.0 |
  | ruff | 0.17.2 | 0.17.4 |
  | mypy | 2.4.0 | 2.3.1 |
  | typos | 1.50.2 | 1.52.0 |
  | markdownlint-cli2 | 0.23.2 | 0.24.0 |
  | editorconfig-checker | 3.11.1 | 4.0.2 |

  cargo-llvm-cov, cargo-deny, cargo-mutants, cargo-fuzz, taplo, uv, pytest, rustqual,
  lychee, shellcheck, actionlint, ripsecrets and the toolchain are at the same version
  under both. Two tools went down: maturin 1.15.0 still meets the wheel's
  `maturin>=1.15` floor, and mypy 2.3.1 reports nothing 2.4.0 did not. If a gate needs
  a version nixpkgs lacks, `nix/` overrides that package at an exact version.
- **Some updates need work by hand.** A new toolchain channel needs a rust-overlay
  revision that knows it. A rustqual bump needs both of its hashes fixed by hand. A
  new tag for the checkers needs `just lock` on its pull request's branch.
- **The trust roots change.** They are now:
  - `cache.nixos.org`'s signing key, for every substituted store path.
  - rust-overlay's manifests, whose hashes come from `static.rust-lang.org`.
  - The fixed-output hashes in `nix/rustqual.nix`.
  - The git revisions and content hashes in `flake.lock`.

  [Security model](../explanation/security-model.md) has the detail.
- **Commits and first runs cost time.** A commit made outside the shell pays a few
  seconds to enter it. A first `nix develop` fills about 2.5 GiB of store on Linux.
- **A store garbage collection can break built files.** It can remove what `target/`
  build scripts and the parity reference link against. `just sync`'s root keeps the
  shell itself.
- **Flakes read only files git knows.** A new file under `nix/` must be added to the
  index before the shell sees it.

The ones that help:

- One prerequisite replaces three.
- A clone needs no GitHub API access to reach a green gate.
- cargo-fuzz runs natively on Apple silicon, so Rosetta 2 is no longer a prerequisite
  once `macos-smoke` has shown it.
- Every recipe, hook and CI step runs the same binaries.

## What would reopen this

A gate that needs a tool version nixpkgs cannot provide and an override in `nix/` cannot
build. A contributor platform the dev shell cannot support. A house-wide move of every
Biscuit Games repository to another environment manager. Nix's flake interface changing
incompatibly before it is stabilised.

## Related pages

- [Develop locally](../how-to/develop-locally.md)
- [Maintain dependencies](../how-to/maintain-dependencies.md)
- [Quality gates](../reference/quality-gates.md)
- [Decision 0006: Tool manager](0006-tool-manager.md)
- [Decision 0017: Dependency updates through Renovate, except the upstream pin](0017-renovate.md)
