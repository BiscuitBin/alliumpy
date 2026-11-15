---
title: "Commands"
kind: "reference"
audience: ["contributor", "maintainer", "operator", "agent"]
canonical_for: ["command_reference"]
requires: []
---

# Commands

`just --list` prints the live set. This page says what each recipe is for. The `Justfile`
is the supported interface: if something is worth running twice, it belongs there
rather than in a shell history.

Every recipe runs inside the dev shell `flake.nix` defines and refuses to run outside it
([Develop locally](../how-to/develop-locally.md)). Entering that shell for the first time,
or after `flake.lock` moves, downloads it. `initialize`, `sync`, `lock`, `lock-upgrade`,
`audit`, `check-links-online` and `install-parity-reference` reach the network.
Initialization prepares the caches; later `check` runs need no network. A cold cache fails instead of
fetching. Setup recipes and mutating recipes sit outside `check`. `fuzz` and `fuzz-build`
are not network recipes: their lock guard is offline and cargo-fuzz runs with
`CARGO_NET_OFFLINE`, so after `just sync` they need no network. `mutants`, `bench`, `fuzz`
and `fuzz-build` are reports or proofs a person runs, never part of `check`.

## Setup

| Recipe | Purpose |
| --- | --- |
| `default` | Print the recipe list when just has no arguments. |
| `initialize` | Refuse outside the dev shell, run check-toolchain, sync, and install the hook only in the primary checkout. Never formats, stages, commits, tags or pushes. |
| `check-toolchain` | Refuse a stale dev shell, a cargo, rustc, rustfmt or clippy outside the flake's toolchain, any other gate tool outside the shell's own packages, or a toolchain other than the pinned channel; then print the toolchain and host. |
| `sync` | Fetch the workspace's and the fuzz crate's Cargo dependencies and record the dev shell as a GC root at `.nix/dev-shell`, without rewriting any of the three locks. |
| `lock` | Relock `Cargo.lock` and `fuzz/Cargo.lock` after a manifest edit, and lock any input `flake.nix` newly names. Read every diff. |
| `lock-upgrade` | Move both Cargo resolutions within manifest constraints and every flake input to the head of its ref. |
| `lock-check` | Compare `Cargo.lock`, `fuzz/Cargo.lock` and `flake.lock` with their manifests offline without writing. |
| `install-hooks` | Copy the path-free hook shim `scripts/pre-commit-hook.sh` into the hooks directory; offline. |

## Develop

| Recipe | Purpose |
| --- | --- |
| `bench` | Run the core's divan benchmarks by hand; never in CI or the gate. |
| `fuzz` | Refuse a stale `fuzz/Cargo.lock` offline, then fuzz one target on the pinned stable with `--sanitizer none` for a bounded time (300 seconds by default). Outside check. |
| `fuzz-build` | The same lock guard, then compile the fuzz targets without running them; the `rust` CI job runs it. Outside check. |
| `build` | Build the workspace with every feature and the lockfile. |
| `test` | Run core unit and integration tests through nextest, then doctests. Exclude the cdylib, whose tests are Python's. |
| `test-doc` | Run core doctests alone. |
| `snapshots-check` | Validate locks, run all core tests offline through cargo-insta and nextest, reject mismatches and unreferenced files without writing pending snapshots. |
| `snapshots-review` | Interactive review of pending snapshots for a person at a terminal. |
| `snapshots-accept` | Validate locks, rerun all core tests offline, accept intended snapshots without a terminal and delete unreferenced snapshots. Read the diff. |

## Format and check

| Recipe | Purpose |
| --- | --- |
| `format` | Write rustfmt formatting over the workspace and the fuzz crate, taplo's, and nixfmt's over the flake's Nix files. |
| `fix` | Run the mutating hook configuration twice, format the fuzz crate, then clippy's repairs over the workspace and the fuzz crate, then lint. |
| `lint` | Run the complete read-only hook gate over all files. |
| `fmt-check` | Check Rust formatting in the workspace and the fuzz crate, and nixfmt formatting of `flake.nix` and `nix/`. |
| `toml-check` | Check TOML formatting and lint. |
| `clippy` | Lint all targets and features, and the fuzz crate's targets, with warnings as errors. |
| `metrics` | Complexity, cohesion and coupling once per crate, through the rustqual `nix/rustqual.nix` pins. Module rules wait for modules. |
| `features` | Check every feature combination using cargo-hack. |
| `coverage` | Run core nextest tests instrumented, enforce the line floor, and write ignored lcov output. |
| `doc` | Build both crates' rustdoc with warnings as errors and `--cfg docsrs`. |
| `site` | Empty `target/doc`, run doc, then write a root index linking both crates. Outside check. |
| `deny` | Offline licence, ban and source checks. |
| `audit` | Advisory check requiring the RustSec database; outside check. |
| `mutants` | Check the locks offline, require a non-empty mutant list for the selection, then run cargo-mutants over the core on a copy of the tree; a report outside check. |
| `deps-unused` | Report declared dependencies no crate uses. |

## Documents

| Recipe | Purpose |
| --- | --- |
| `check-docs` | markdownlint, typos and offline links, then the documentation contract. |
| `check-agents` | Validate the agent inventory, adapters, skills and bridges. |
| `check-links-online` | Resolve external links manually; network failures keep it outside check. |

## Python

| Recipe | Purpose |
| --- | --- |
| `py-develop` | Recreate the venv `target/py-env` offline on the shell's interpreter, with its site packages visible, and install the extension editable into it via maturin and uv. |
| `py-lint` | Ruff lint and format; require the package in its input and the positive fixture's F401 and E501 failures. |
| `py-typecheck` | mypy over package, stub, tests and scripts; require the deliberate type-error fixture to fail with status 1. |
| `py-test` | Rebuild with py-develop, then run pytest on the binding from `target/py-env`. |
| `py-stubtest` | Rebuild, then compare the imported native module with its canonical stub and reviewed allowlist. |
| `wheel` | Empty dist and build a locked release wheel for this platform. |
| `wheel-smoke` | Build the wheel, require exactly one, install offline into a fresh venv, run isolated Python smoke, the console version and `allium check` on the clean fixture. |
| `version-check` | Compare version copies, each member crate's version included, with the installed wheel-smoke command, and its whole `--version` output with `ALLIUM_VERSION_STRING` and, when built at the pin, the parity reference's; a missing smoke venv fails. |

## Parity

| Recipe | Purpose |
| --- | --- |
| `install-parity-reference` | Build upstream's `allium-cli` at the pin from crates.io, locked, into `.tools/parity/`, off `PATH`. Network; outside check. |
| `parity` | Run wheel-smoke and py-develop, then compare the wheel's `allium` with the reference byte for byte on stdout and exactly on exit status over the parity corpus, with its controls, then run `test_cli.py`. POSIX; outside check. |

## Aggregate

| Recipe | Purpose |
| --- | --- |
| `check` | Run the twenty-two configured gates in order with worktree snapshots, then check-clean. |
| `check-clean` | Require a clean worktree, or equality with a supplied baseline. |

## Related pages

- [Quality gates](quality-gates.md)
- [Develop locally](../how-to/develop-locally.md)
- [Configuration](configuration.md)
