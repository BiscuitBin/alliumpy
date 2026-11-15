---
title: "Configuration"
kind: "reference"
audience: ["contributor", "maintainer", "operator", "agent"]
canonical_for: ["configuration_reference"]
requires: []
---

# Configuration

The parser API has no local runtime settings. This page describes the files that build,
package and check it. The [packaging explanation](../explanation/packaging.md) owns the
reason for two Python manifests and a static wheel version.

## Environment

| Variable | Read by and effect |
| --- | --- |
| `ALLIUMPY_DEV_SHELL` | Exported by the dev shell. Every recipe refuses to run when it is unset, and the hook shim runs prek directly when it is set. |
| `ALLIUMPY_RUST_TOOLCHAIN` | Exported by the dev shell: the flake's toolchain, under which check-toolchain requires cargo, rustc, rustfmt and clippy. |
| `ALLIUMPY_ENV_FILES`, `ALLIUMPY_ENV_FINGERPRINT` | Exported by the dev shell: the files it is built from and their digest, which check-toolchain recomputes to refuse a stale shell. |
| `ALLIUMPY_FLAKE_INPUTS` | Exported by the dev shell only so that its GC root keeps the flake inputs' sources. |
| `PYO3_PYTHON` | Exported by the dev shell: the absolute path of its Python, for every Cargo invocation and every venv a recipe makes. |
| `UV_PYTHON_DOWNLOADS`, `UV_PYTHON_PREFERENCE` | Exported by the dev shell as `never` and `only-system`, so uv uses the shell's interpreter and downloads none. |
| `VIRTUAL_ENV`, `UV_OFFLINE` | Set on py-develop's maturin line, so maturin installs into `target/py-env` through uv, offline. |
| `CC`, `SOURCE_DATE_EPOCH`, `NIX_HARDENING_ENABLE` | Set by `nix develop` from stdenv: the C and C++ compiler libfuzzer-sys's build script uses, a fixed build timestamp, and that compiler's hardening flags. |
| `SSL_CERT_FILE`, `NIX_SSL_CERT_FILE` | Kept from the caller by `nix develop`; Nix reads the second to trust a TLS-intercepting proxy. |
| `RUSTDOCFLAGS` | Set on doc to `-D warnings --cfg docsrs`. |
| `INSTA_UPDATE` | no during checks; new during snapshot acceptance. |
| `CARGO_NET_OFFLINE` | true after lock validation in the snapshot recipes, `fuzz` and `fuzz-build`. |
| `CARGO_TERM_COLOR`, `CARGO_INCREMENTAL`, `CARGO_NET_RETRY`, `RUST_BACKTRACE` | CI log colour, incremental policy, fetch retries and panic traces. |

There is no `.cargo/config.toml`. A global RUSTFLAGS there would change fingerprints
and make rust-analyzer and recipes rebuild against each other. Recipe-specific flags
stay on the recipe.

## Configuration files

| File | Owns |
| --- | --- |
| `rust-toolchain.toml` | Exact compiler, minimal profile, rustfmt, clippy and llvm-tools-preview components. |
| `Cargo.toml` | Workspace members, the excluded `fuzz/` crate, inherited package fields and version, shared dependencies, workspace lints, release/test profiles. |
| `Cargo.lock` | Committed Cargo resolution. |
| `crates/alliumpy-core/Cargo.toml` | rlib, upstream dependency, inherited workspace lint table, and the divan dev-dependency with the `parse` bench. |
| `fuzz/Cargo.toml`, `fuzz/Cargo.lock` | The fuzz crate outside the workspace: its libfuzzer-sys range, the path dependency on the core, the repeated `forbid` and Clippy tables, and its own committed resolution. |
| `crates/alliumpy/Cargo.toml` | cdylib, path dependency on core, pyo3 and the bindings crate's own lint table. |
| `flake.nix` | The flake's inputs (nixpkgs from its unstable channel, rust-overlay, and the shared checkers at a release tag), the two supported systems, the dev shell, `packages.dev-shell`, `checks` and the formatter ([decision 0018](../decisions/0018-nix-dev-environment.md)). |
| `flake.lock` | Generated pin of every flake input, and through nixpkgs of every tool version; never hand-edited. |
| `nix/dev-shell.nix` | The dev shell: the toolchain read from `rust-toolchain.toml`, Python with pytest, mypy and the checkers, every tool a recipe or hook calls, and the variables above. |
| `nix/rustqual.nix` | rustqual, which nixpkgs lacks, built from crates.io at an exact version against two pinned hashes. |
| `nix/biscuit-games-tooling.nix` | The shared checkers, built from the flake input at the version its own manifest names. |
| `.envrc` | Opt-in direnv entry to the dev shell. |
| `pyproject.toml` | The ordered gate recipes the shared checkers read, and nothing else. |
| `crates/alliumpy/pyproject.toml` | maturin build backend, static distribution metadata, entry point, module layout, locked builds and trusted-publishing settings. |
| `rustfmt.toml` | Stable Rust formatting settings and style edition. |
| `clippy.toml` | Complexity thresholds, test relaxations and deterministic collection guidance. |
| `rustqual.toml` | Complexity, cohesion, coupling and IOSP thresholds; module rules wait for modules. |
| `taplo.toml` | TOML formatting/lint, dependency sorting and generated/fixture exclusions. |
| `deny.toml` | Shipping graph targets, licence allowlist, bans, sources and advisory policy. |
| `.config/nextest.toml` | Test-runner version floor, default fail-fast and CI reporting profiles. |
| `ruff.toml` | Python target floor, lint/format rules, exclusions and documented per-file exceptions. |
| `mypy.ini` | Python type-checking inputs, strictness, exclusions and native module handling. |
| `Justfile` | Recipes, the refusal outside the dev shell, the gate tool list check-toolchain reads, and the core line-coverage floor. |
| `scripts/initialize.sh` | Bootstrap order and primary-checkout-only hook installation. |
| `scripts/pre-commit-hook.sh` | The hook shim install-hooks copies: prek in the dev shell, entered when the commit comes from outside it. |
| `scripts/version_check.py` | Version-copy assertions and the installed wheel-smoke version check. |
| `.pre-commit-config.yaml` | Installed read-only hooks, every one a system hook on a dev-shell binary. |
| `.pre-commit-fix.yaml` | Mutating hooks invoked by fix; excludes deliberately invalid Python controls. |
| `.editorconfig` | Whitespace, newlines and indentation, including four-space Python. |
| `.gitattributes` | Text normalization and generated file classification. |
| `.gitignore` | Build products, environments, local state, snapshots' pending files and scratch exclusions. |
| `.markdownlint-cli2.jsonc` | Markdown rules, permitted instruction elements and ignored generated paths. |
| `lychee.toml` | Offline link settings and excluded paths. |
| `_typos.toml` | Spelling exclusions and vocabulary exceptions. |
| `docs/manifest.yml` | Strict JSON page registration and canonical topic ownership. |
| `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` | Canonical agent instructions and fixed adapters. |
| `.agents/skills/`, `.claude/skills/`, `.codex/skills/` | Seven canonical procedures and fourteen fixed bridges. |
| `.github/actions/setup/action.yml` | Shared setup: Nix, the store cache, the dev shell, the cargo cache and sync. |
| `.github/workflows/ci.yml` | CI gate layout: seven gate jobs, the required `check` aggregate, and `macos-smoke` outside it. |
| `.github/workflows/audit.yml`, `.github/workflows/pages.yml` | T01's scheduled advisory checks and conditional API deployment. |
| `.github/workflows/release-pypi.yml` | Release builds and publication ([decision 0015](../decisions/0015-release-process.md)). |
| `renovate.json` | Dependency-update automation over every pin except `allium-parser` ([decision 0017](../decisions/0017-renovate.md)). |
| `.github/workflows/mutants.yml`, `.github/workflows/fuzz.yml` | Weekly and manual mutation and fuzzing reports outside the aggregate gate; never in `check`'s `needs`. |
| `.cargo/mutants.toml` | cargo-mutants' exclusion file, as `exclude_re` with a comment for an equivalent mutant. Absent until one needs it. |

### The lint tables

The core opts into `[workspace.lints]`. The binding keeps an equal copy under its own
`[lints]` tables, because Cargo cannot combine workspace lint inheritance with member
overrides. Both keep `unsafe_code = "forbid"` and `missing_docs = "warn"`. No pyo3 macro
exception is needed on Rust 1.99.1 and pyo3 0.30.1; a future exception needs a `warn`
probe naming the pyo3 macro that emits it, and must not hide a diagnostic on a
hand-written line. Pedantic and cargo groups warn; clippy turns warnings into
errors. Missing public documentation, exhaustive public types, panic-prone production
calls and undocumented suppression are checked. At call sites use
`#[expect(lint, reason = "...")]`, so an obsolete suppression warns itself.

### Dependency and version policy

Cargo manifests use full caret ranges except the exact upstream parser pin; the
lockfile records the actual resolution. The bindings' path dependency version follows
the workspace version. The wheel's static version permits `.postN` while Cargo keeps
the base upstream version. Version-check reads manifests and the core literal and
runs the installed command from wheel-smoke; it fails if that environment is missing.

deny's graph includes the five wheel platforms and both Linux libc variants, excluding
development dependencies. It permits named Apache-compatible licences, rejects unknown
git/registry sources and wildcard versions, warns on duplicate versions and bans
`openssl-sys`. Advisory fetching is audit's separate network operation.

## Related pages

- [Maintain dependencies](../how-to/maintain-dependencies.md)
- [Decision 0005](../decisions/0005-rust-quality-gate.md)
