---
title: "Decision 0006: Tool manager"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_tool_manager"]
requires: []
---

# Decision 0006: Tool manager

Carried from pachinko's decision 0011 at `bf51e0d`, which carried libpawdoku's decision 0011 at `ccdd001`.

## Context

The carried hook-runner decision kept Python and named the installers of its day: uv for
the Python side, cargo-binstall for the cargo tools, each with its own lockfile or pin
list, beside rustup for the compiler. A fresh machine installed four tools before the
first-run script could start, and the tool pin list named versions rather than hashes,
trusting each tool's GitHub release naming.

The source project stopped on that trust. taplo 0.10.0 publishes no binstall metadata
and its release archives are in a shape binstall cannot unpack, so the pinned, current
version could not be installed without compiling it, which the install command refuses
by design. The other five tools installed only because binstall's default naming guess
matched their releases.

pixi resolves the same tools from conda-forge, where every one of them except cargo-hack
is packaged at the pinned version, and records the whole environment, Python and the
checkers included, in one hashed lockfile. conda-forge also packages Rust, but only
rustup's cargo proxy honours `rust-toolchain.toml` and its pinned components, including
llvm-tools for coverage. A second compiler owner would undermine that evidence.

## Decision

pixi owns the Python environment and the tool binaries available from conda-forge.
`pyproject.toml` is the manifest: its `[tool.pixi.*]` tables pin just, prek,
cargo-binstall, cargo-nextest, cargo-llvm-cov, cargo-deny, cargo-shear and taplo
exactly, constrain Python to its chosen patch series, and pin maturin, uv, pytest, ruff
and mypy exactly for the Python gates, plus `biscuit-games-tooling` as a PyPI git
dependency at a release tag. `pixi.lock` is the pin; `pixi install --locked` is the
first thing the first-run script does; `pixi lock --check` is the gate's lockfile check;
the environment lives in the gitignored `.pixi/`. The `Justfile` puts the environment's
`bin` first on every recipe's `PATH`, then `.tools/bin`, and calls every tool by name;
nothing runs through `pixi run` inside a recipe.

rustup keeps the compiler. `rust-toolchain.toml` remains the single owner of the Rust
version, its components and its targets; the pixi environment holds no `rust` package,
and `check-toolchain` keeps refusing any cargo that is not rustup's proxy.

`tools.txt` remains as the escape hatch for a tool conda-forge does not carry. It lists
`cargo-hack` alone; cargo-binstall, itself a pixi dependency, installs it into
`.tools/bin`. The hooks that prek pins (typos, lychee, shellcheck, actionlint,
markdownlint-cli2, editorconfig-checker, ripsecrets) keep their pins in the hook
configuration. `tools-source.txt` is the second escape hatch, added by [decision
0007](0007-metrics-gate.md), for a tool that also has no release binary: it lists
rustqual, which cargo-binstall builds from source.

## Consequences

This installation supersedes the older separate Python resolver and tool installers:
`uv.lock`, `.venv/` and `.python-version` are absent, no recipe starts with `uv run
--frozen`, and CI restores pixi's environment. uv is now a pinned binary used by
maturin, not the tooling environment's resolver. prek and the shared checkers remain.

Contributors need rustup, pixi and just (any just launches the recipes; the pinned one
in the environment runs every nested call and CI). CI installs pixi with one action,
restores the environment from a cache keyed on the lockfile's hash, and needs one more
cache only for what pixi cannot own. pixi-owned resolutions have hashes in `pixi.lock`;
moving one is a manifest edit, a lock update and a reviewed diff. The compiler and extra
lists retain their separate owners.

The cost is a package manager that Rust contributors do not usually carry, needed for
the gate and not for `cargo build`; one environment per worktree, not relocatable; a
version that conda-forge lags on occasionally; and cargo-hack still arriving by a second
mechanism until conda-forge packages it.

## What would reopen this

cargo-hack appearing on conda-forge, which empties `tools.txt`, and with rustqual there
too (decision 0007) removes cargo-binstall; that is a pin move, not a new decision. A
pixi Rust package that respects the toolchain pin and supplies all required components
would reopen compiler ownership. pixi's PyPI git resolution failing for the tooling
package, which would return the Python side to uv without moving the tools. A house-wide
move of every Biscuit Games repository to pixi, which would make the manifest shape a
template concern.

## Related pages

- [Decision 0002: Hook runner and checkers](0002-hook-runner-and-checkers.md)
- [Develop locally](../how-to/develop-locally.md)
- [Maintain dependencies](../how-to/maintain-dependencies.md)
