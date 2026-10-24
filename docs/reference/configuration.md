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
| `PYO3_PYTHON` | Set by the Justfile to the absolute pixi interpreter path for every Cargo invocation. |
| `CONDA_PREFIX` | Set on py-develop so maturin finds the pixi environment. |
| `RUSTDOCFLAGS` | Set on doc to `-D warnings --cfg docsrs`. |
| `CARGO_HOME` | check-toolchain expects the rustup proxy here, defaulting to the user's cargo directory. |
| `PREK_HOME` | Hook cache; CI places it outside the workspace. |
| `GITHUB_TOKEN`, `GH_TOKEN` | Release lookup credentials; unset for install-tools' source-build pass, with token discovery disabled. |
| `INSTA_UPDATE` | no during checks; new during snapshot acceptance. |
| `CARGO_NET_OFFLINE` | true after lock validation in the snapshot recipes. |
| `CARGO_TERM_COLOR`, `CARGO_INCREMENTAL`, `CARGO_NET_RETRY`, `RUST_BACKTRACE` | CI log colour, incremental policy, fetch retries and panic traces. |

There is no `.cargo/config.toml`. A global RUSTFLAGS there would change fingerprints
and make rust-analyzer and recipes rebuild against each other. Recipe-specific flags
stay on the recipe.

## Configuration files

| File | Owns |
| --- | --- |
| `rust-toolchain.toml` | Exact compiler, minimal profile, rustfmt, clippy and llvm-tools-preview components. |
| `Cargo.toml` | Workspace members, inherited package fields and version, shared dependencies, workspace lints, release/test profiles. |
| `Cargo.lock` | Committed Cargo resolution. |
| `crates/alliumpy-core/Cargo.toml` | rlib, upstream dependency and inherited workspace lint table. |
| `crates/alliumpy/Cargo.toml` | cdylib, path dependency on core, pyo3 and the bindings crate's own lint table. |
| `pyproject.toml` | pixi tooling environment, exact tool pins, supported tooling platforms and ordered gate recipes. No Rust compiler package. |
| `pixi.lock` | Generated tooling resolution; never hand-edited. |
| `crates/alliumpy/pyproject.toml` | maturin build backend, static distribution metadata, entry point, module layout, locked builds and trusted-publishing settings; no pixi table. |
| `tools.txt` | Binary-only extra tools, currently cargo-hack. |
| `tools-source.txt` | Extras whose source build is accepted, currently rustqual. |
| `rustfmt.toml` | Stable Rust formatting settings and style edition. |
| `clippy.toml` | Complexity thresholds, test relaxations and deterministic collection guidance. |
| `rustqual.toml` | Complexity, cohesion, coupling and IOSP thresholds; module rules wait for modules. |
| `taplo.toml` | TOML formatting/lint, dependency sorting and generated/fixture exclusions. |
| `deny.toml` | Shipping graph targets, licence allowlist, bans, sources and advisory policy. |
| `.config/nextest.toml` | Test-runner version floor, default fail-fast and CI reporting profiles. |
| `ruff.toml` | Python target floor, lint/format rules, exclusions and documented per-file exceptions. |
| `mypy.ini` | Python type-checking inputs, strictness, exclusions and native module handling. |
| `Justfile` | Recipes, tool PATH, PYO3_PYTHON and the core line-coverage floor. |
| `scripts/initialize.sh` | Bootstrap order and primary-checkout-only hook installation. |
| `scripts/version_check.py` | Version-copy assertions and the installed wheel-smoke version check. |
| `.pre-commit-config.yaml` | Installed read-only hooks. |
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
| `.github/actions/setup/action.yml` | T01's shared pinned setup and cache preparation. |
| `.github/workflows/ci.yml` | CI gate layout; T01 replaces the foundation stub. |
| `.github/workflows/audit.yml`, `.github/workflows/pages.yml` | T01's scheduled advisory checks and conditional API deployment. |

### Planned configuration

These files are assigned by the repository plan and do not exist yet:

| File | Future owner and purpose |
| --- | --- |
| `.github/workflows/release-pypi.yml` | T14: release builds and publication. |
| `.github/workflows/mutants.yml`, `.github/workflows/fuzz.yml` | T15: mutation and fuzzing runs outside the aggregate gate. |
| `.cargo/mutants.toml` | T15: created only if an equivalent mutant needs configuration. |
| `renovate.json` | T17: dependency-update automation. |

### The lint tables

The core opts into `[workspace.lints]`. The binding owns a copy under its own `[lints]`
tables because a member cannot lower a workspace forbid for macro output. Both keep
`unsafe_code = "forbid"`. T02 settles any documented pyo3 macro exceptions there,
without weakening the core. Pedantic and cargo groups warn; clippy turns warnings into
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
