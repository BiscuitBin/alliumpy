---
title: "Decision 0018: A Nix flake owns the tools"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_nix_tool_owner"]
requires: []
---

# Decision 0018: A Nix flake owns the tools

## Context

The tools here had three owners. pixi owned Python and every tool binary conda-forge
carries ([decision 0006](0006-tool-manager.md)). rustup owned the compiler.
cargo-binstall filled the gaps from two pin lists. On top of those, prek fetched and
built its own hook tools, and the parity reference was a `cargo install` into a
directory kept off `PATH`.

Each owner had its own pin file, its own cache in CI and its own way to fail. A first
run needed rustup and pixi installed and in the right order on `PATH`, and the gate's
first check existed to catch the order being wrong. One tool ran under Rosetta because
its only macOS binary was x86-64. Each tool's version was pinned exactly and moved
alone, so the dependency dashboard carried a row per tool.

In November 2026 the maintainer chose to move to one owner.

## Decision

A project-local Nix flake owns every tool. `flake.nix` says what the dev shell holds
and `flake.lock` pins it.

**Flakes with direnv.** `nix develop` enters the shell everywhere. A checked-in
`.envrc` holding `use flake` enters it automatically for a contributor who uses direnv
and has allowed this directory; it does nothing until then.

**nixpkgs decides tool versions.** One nixpkgs revision in `flake.lock` sets the
version of every tool at once. Two things stay exact. The Rust version, with its
components, is read from `rust-toolchain.toml`, which remains its single owner. The
`allium-parser` pin stays exact under [decision 0011](0011-exact-pin-on-allium-parser.md).
`nextest-version` in the nextest configuration is a floor, not a pin, so it holds
under either provider.

**`just check` in the shell stays the gate.** The `Justfile` remains the only
interface to the checks. `nix build` and `nix flake check` are recipes beside the gate,
never the gate.

**Nix-built wheels are not release artefacts.** A wheel built by Nix links against
Nix's libraries and is not a portable PyPI wheel. `release-pypi.yml` keeps its own
build path and its own pins ([decision 0015](0015-release-process.md)).

**The project never manages the machine.** A contributor installs Nix once, with any
installer. The repository uses it only through this flake: no nix-darwin, no
home-manager, no global profile. The flake relies on no setting an installer happens to
enable. Where the experimental `nix-command` and `flakes` features are needed, the
caller names them: direnv's `use flake` does, and CI writes them into its Nix
configuration.

**Three systems.** Apple silicon macOS and x86-64 Linux are where contributors and CI
work, as before. arm64 Linux is added so the same shell runs natively in a Linux
container on an Apple silicon Mac.

**One seam says who provides the tools.** The dev shell sets `ALLIUMPY_TOOLS=nix`. The
`Justfile` reads it in one place: inside the shell it leaves `PATH` as the shell made
it and adds nothing from `.pixi` or `.tools`, even when both exist. A tool the shell does
not hold still falls through to the `PATH` the shell inherited, so the shell's contents
decide what is complete; the toolchain check requires cargo and rustc to come from the
Nix store there. Any other value is refused. Every recipe finds Python and each tool by
name either way. The proof that nothing outside the shell is needed is a run with
nothing else on `PATH`, which belongs to the cutover.

**The Nix files are code.** nixfmt formats them, statix lints them and deadnix finds
unused bindings, all three from the dev shell. `just nix-check` runs the three and
fails when Git lists no Nix file; `just format` and `just fix` format them first in the
shell, before any tool the shell may not yet hold; `nix fmt` works through the flake's `formatter` output. The recipe joins
`just check`'s list when the shell becomes the only provider, because pixi has no Nix
formatter. The hook gate, the flake checks and CI each gain it as they move to the
shell.

**A flake sees only what Git tracks.** In a Git repository Nix reads the tracked files
and nothing else. A new file that a build or the shell needs must be added to the index
first; `git add --intent-to-add` is enough.

### Flake inputs

Each input is a dependency under [decision 0004](0004-dependency-policy.md), and
`flake.lock` pins each to a commit and a content hash.

| Input | Why it is here | Alternatives considered | Gate impact | Licence |
| --- | --- | --- | --- | --- |
| `nixpkgs`, the `nixpkgs-unstable` branch | Every tool except the compiler. | A release branch, such as `nixos-26.05`, moves less but lags the cargo tools by months; unstable carried every tool the gates need, and is built for all three systems. | Every gate run in the shell. `flake.lock` is outside the lock check until the cutover. | MIT |
| `rust-overlay` (oxalica) | Builds the toolchain `rust-toolchain.toml` names, exact channel and components, from the official release binaries, each pinned by hash in the overlay's own manifests. It follows this flake's `nixpkgs`, so no second nixpkgs is fetched. | fenix also reads the toolchain file but tracks its own manifest snapshots; nixpkgs' own `rustc` is one version, not the pinned one, and has no `llvm-tools` component. | The toolchain check and every Rust gate in the shell. | MIT |
| `biscuit-games-tooling`, built in the flake from GitHub | The `bg-*` commands, `just check`'s runner among them ([decision 0002](0002-hook-runner-and-checkers.md)). Pinned to the commit the pixi manifest's `v0.3.0` tag resolves to, by content hash. Its build backend's upper bound is relaxed to nixpkgs' `uv_build`. | None: nixpkgs does not carry it, and it is this organisation's own. | `just check`, the docs and agents checks, the secret scan. | None declared at this revision: no licence file or field. It is the maintainer's own package and never ships. |
| rustqual 1.8.3, built in the flake from crates.io | The metrics gate ([decision 0007](0007-metrics-gate.md)); nixpkgs does not carry it. The same crate and version `tools-source.txt` pins, pinned here by source and vendor hashes. | A prebuilt binary does not exist for any version. | The metrics gate in the shell. | MIT |

## Consequences

The ones that hurt. Nix is a heavier prerequisite than pixi: on macOS it is a
machine-level install with its own volume and daemon. A first shell entry downloads
several gigabytes. Flakes are still labelled experimental by upstream Nix.

Tool versions move together. One tool cannot be bumped, or held back, without moving
nixpkgs or overriding that tool in the flake. The exact per-tool pins are gone, and a
tool's version is read from the shell or from nixpkgs at the locked revision, not from
a manifest line.

A file Git does not track is invisible to the flake, which surprises everyone once.

Until the cutover there are two providers, and every recipe has to work under both.
pixi stays the supported path and [decision 0006](0006-tool-manager.md) stands until
then.

When this was decided Nix was not installed on the maintainer's Mac. Linux evidence
comes from a Nix container and from CI, and macOS evidence from a CI job on an Apple
silicon runner; the commit messages cite each run.

## What would reopen this

The exact Rust toolchain becoming unobtainable through the overlay, which would move
the compiler to another overlay or back to rustup without moving the tools. nixpkgs
dropping or long lagging a tool the gate needs is not a reopening: that tool is
packaged in the flake. A pattern of such overrides would reopen the pin model. Flakes
being withdrawn or replaced upstream. A contributor platform Nix does not support.

## The conversion's record

Design choices that later steps of the conversion build on are recorded here as they
are made.

- **The tracer bullet.** The shell first held the toolchain, just, cargo-nextest,
  Python 3.14 for pyo3's build script, a C and C++ compiler from the standard
  environment, and the three Nix tools. The toolchain check, the format check, clippy,
  the tests and the docs build passed in it with nothing from the machine.
- **The Python gates.** One interpreter, Python 3.14 with pytest and mypy from its own
  package set, serves pyo3's build script, pytest, mypy and stubtest; maturin, uv and
  ruff come from nixpkgs beside it. The dev shell's Python environment is read-only, so
  the editable install goes into a virtual environment under `target/py-develop/`,
  built offline on the provider's interpreter with its packages visible. Both providers
  use it, so there is one mechanism. `PYO3_PYTHON` stays the provider's own interpreter,
  so the first `py-develop` does not move it.
- **A shell-built wheel on a Python from outside Nix.** On arm64 Linux maturin tagged
  the wheel `manylinux_2_34`. Its extension needs only libc and libgcc, and its run path
  names Nix store directories that do not exist elsewhere, so another system's loader
  falls back to its own libraries. Installed offline into a virtual environment on
  Debian's Python 3.13 (glibc 2.41), in a container with no `/nix`, it passed the smoke.
  Python 3.11 from outside Nix is CI's Python 3.11 smoke job to show.
- **The remaining Rust gates.** cargo-hack, cargo-llvm-cov, cargo-deny, cargo-shear,
  cargo-insta, cargo-fuzz, cargo-mutants and taplo come from nixpkgs. nixpkgs does not
  carry rustqual, so the flake builds it from the crate crates.io publishes, at the
  version `tools-source.txt` pins, with the crate's own lockfile, the pinned toolchain
  and two content hashes, and exports that version as `ALLIUMPY_RUSTQUAL_VERSION`. The
  metrics gate reads its expectation from there in the shell and from
  `tools-source.txt` under pixi, so each provider has one owner for it. No LLVM tool is
  on the shell's `PATH`; coverage can only use the ones in the pinned compiler's
  sysroot. cargo-fuzz is built for the host, so the Rosetta prerequisite does not apply
  in the shell. The lock check skips pixi's lock in the shell; covering `flake.lock`
  arrives with the cutover.
- **The hooks.** prek and the seven third-party checkers come from nixpkgs, and the
  `bg-*` commands from the tooling package the flake builds. While pixi remains, the
  two forms coexist as two configurations: `.pre-commit-config.yaml` and its fix
  counterpart stay the pixi form, in which prek fetches and builds each checker, and
  `.pre-commit-nix.yaml` and `.pre-commit-nix-fix.yaml` are the dev shell's form, with
  the same ids, the same local and builtin hooks and the checkers called by name, plus
  a hook for the Nix files. The Justfile picks one by provider. The cutover makes the
  dev shell's form the only one. Two places name the tooling's revision until then:
  the pixi manifest's tag, locked in `pixi.lock`, and the commit in `flake.nix`. Nothing
  checks that they agree; a bump moves both in one change, and the flake's comment says
  so. In the dev shell's form the checkers are newer than the pixi form's pins
  (editorconfig-checker 4.0.2, markdownlint-cli2 0.24.0, typos 1.52.0) and found
  nothing new.

## Related pages

- [Decision 0004: Dependency policy](0004-dependency-policy.md)
- [Decision 0006: Tool manager](0006-tool-manager.md)
- [Develop locally](../how-to/develop-locally.md)
- [Commands](../reference/commands.md)
