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
| `ALLIUMPY_TOOLS` | Set to `nix` by the flake's dev shell and by nothing else. The Justfile reads it in one place: `nix` leaves `PATH` as the shell made it, unset selects pixi, and any other value is refused. |
| `ALLIUMPY_PARITY_REFERENCE` | Set by the dev shell to the `allium` the flake builds as the parity reference, which is never on `PATH`. parity and version-check use it in place of `.tools/parity/bin/allium`; a named reference that is missing fails version-check. |
| `ALLIUMPY_RUSTQUAL_VERSION` | Set by the dev shell to the rustqual version the flake builds; the metrics gate's expectation there. |
| `PYO3_PYTHON` | Set by the Justfile, for every Cargo invocation, to the absolute path of the tool provider's own `python`: pixi's, or the dev shell's inside `nix develop`. Never the virtual environment's, so the value does not move when py-develop first runs. py-develop and wheel-smoke build their environments on it. |
| `VIRTUAL_ENV` | Set on py-develop to `target/py-develop/`, where maturin installs the extension editable. |
| `CONDA_PREFIX` | Unset on py-develop: maturin refuses to choose between it and `VIRTUAL_ENV`. |
| `RUSTDOCFLAGS` | Set on doc to `-D warnings --cfg docsrs`. |
| `RUSTC` | If set, check-toolchain checks this compiler, as cargo would run it, in place of the `rustc` on `PATH`. |
| `RUSTUP_AUTO_INSTALL` | Set to 0 by check-toolchain, so an uninstalled toolchain is refused where rustup provides cargo. |
| `PREK_HOME` | Hook cache; CI places it outside the workspace. |
| `GITHUB_TOKEN`, `GH_TOKEN` | Release lookup credentials; unset for install-tools' source-build pass, with token discovery disabled. |
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
| `pyproject.toml` | pixi tooling environment, exact tool pins, supported tooling platforms and ordered gate recipes. No Rust compiler package. |
| `pixi.lock` | Generated tooling resolution; never hand-edited. |
| `crates/alliumpy/pyproject.toml` | maturin build backend, static distribution metadata, entry point, module layout, locked builds and trusted-publishing settings; no pixi table. |
| `tools.txt` | Binary-only extra tools, currently cargo-hack and cargo-fuzz. |
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
| `flake.nix`, `flake.lock` | The dev shell's contents and their pinned sources ([decision 0018](../decisions/0018-nix-owns-the-tools.md)). |
| `.envrc` | `use flake`, for direnv; inert until the directory is allowed. |
| `.pre-commit-config.yaml` | Installed read-only hooks. |
| `.pre-commit-fix.yaml` | Mutating hooks invoked by fix; excludes deliberately invalid Python controls. |
| `.pre-commit-nix.yaml`, `.pre-commit-nix-fix.yaml` | The same two configurations in the dev shell's form: identical local and builtin hooks, and the third-party checkers as the shell's own tools by name, so nothing is fetched. Selected by the Justfile when the shell is the provider. |
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
| `.github/workflows/ci.yml` | CI gate layout: six gate jobs and the required `check` aggregate. |
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
