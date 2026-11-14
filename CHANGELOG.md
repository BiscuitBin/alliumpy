# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
A version `X.Y.Z` means the wheel wraps allium-tools `X.Y.Z`; `X.Y.Z.postN` is the
Nth packaging-only fix of that wheel (decision 0010). Only this repository's changes
are listed here; upstream's own changes belong to upstream's release notes.

## [Unreleased]

### Added

- Renovate over every pin except `allium-parser` (`renovate.json`, decision 0017), and
  the upstream-bump runbook,
  `docs/how-to/bump-upstream.md`, with `scripts/vendor_cli.py`, which generates the
  vendored command.
- A project-local Nix flake (`flake.nix`, `flake.lock`, `.envrc`; decision 0018) that
  provides every tool, the pinned compiler and Python; `just nix-check` (gate 23),
  `just nix-wheel` and `just nix-flake-check`. CI runs every gate job in its dev shell.

### Removed

- pixi (`pixi.lock` and the root `pyproject.toml`'s pixi tables), `tools.txt`,
  `tools-source.txt` and the `install-toolchain`, `install-tools` and
  `install-parity-reference` recipes: run every recipe inside the dev shell. A hook shim
  installed before this names pixi's prek; run `just install-hooks` once from the
  primary checkout, inside the shell, to replace it. `.pixi/` and `.tools/` are no
  longer used and can be deleted.

## [3.6.1] - 2026-11-05

### Added

- The two-crate foundation: interpreter-independent `alliumpy-core` over an exact
  `allium-parser` pin, and thin pyo3 bindings packaged as one `alliumpy` wheel.
- The Python API: `parse`, immutable `Diagnostic`, `AlliumError` and `ALLIUM_VERSION`.
- The `allium` command through vendored upstream CLI modules in the core
  (decision 0014).
- The read-only `just check` gate, pinned tools and hooks, the handbook and decision
  records, and the agent contract with its skills and bridges.

- Mutation testing (`just mutants`, weekly `mutants.yml`), a divan benchmark (`just bench`)
  and a stable fuzz target over `alliumpy_core::parse` (`just fuzz`, weekly `fuzz.yml`),
  all reports outside the gate (decision 0016).
- The `allium` command is upstream's `allium-cli` 3.6.1, vendored, with stdout and exit-code parity proved by `just parity` (decision 0014).

[Unreleased]: https://github.com/BiscuitBin/alliumpy/compare/v3.6.1...HEAD
[3.6.1]: https://github.com/BiscuitBin/alliumpy/releases/tag/v3.6.1
