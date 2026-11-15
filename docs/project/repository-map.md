---
title: "Repository map"
kind: "project"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["repository_layout"]
requires: []
---

# Repository map

The repository root is a Cargo workspace with two members, and excludes the fuzz
crate under `fuzz/`, which has its own lockfile. Their responsibilities
follow [Architecture](../explanation/architecture.md); the dependency direction is
[Layering](../explanation/layering.md)'s.

```text
.
├── Cargo.toml                 Workspace members, dependencies, lints and profiles
├── Cargo.lock                 Locked Cargo resolution
├── rust-toolchain.toml        Rust compiler and components
├── flake.nix                  Dev shell inputs and outputs
├── flake.lock                 Locked flake inputs, and so every tool version
├── nix/                       The dev shell and the two packages nixpkgs lacks
├── pyproject.toml             Ordered gate recipes for the shared checkers
├── .envrc                     Opt-in direnv entry to the dev shell
├── Justfile                   Supported recipes
├── crates/
│   ├── alliumpy-core/
│   │   ├── Cargo.toml
│   │   ├── benches/parse.rs   divan benchmark of parse, run by just bench
│   │   └── src/lib.rs         Conversion, public values, unit tests and doctests
│   └── alliumpy/
│       ├── Cargo.toml         Thin pyo3 crate and its lint table
│       ├── pyproject.toml     maturin wheel metadata
│       ├── src/lib.rs         Native Python wrappers
│       ├── python/alliumpy/   Package, console shim, stub and py.typed
│       ├── tests/            pytest and stubtest allowlist
│       ├── LICENSE           Apache-2.0 copy for wheel
│       └── LICENSE-allium-tools  Upstream MIT text and attribution
├── fuzz/                      Fuzz crate outside the workspace, its own Cargo.lock
│   └── fuzz_targets/parse.rs  Arbitrary bytes through alliumpy_core::parse
├── tests/fixtures/            Smoke inputs and linter positive controls
├── docs/                      Handbook, manifest and decisions
├── tickets/                   Work and acceptance evidence
├── scripts/                   initialize.sh, version_check.py and the hook shim
├── .agents/skills/            Canonical house skills
├── .claude/skills/            Discovery bridges
├── .codex/skills/             Discovery bridges
├── .github/                   Adapters, workflows and setup action
└── target/ dist/ .nix/ .tools/ ai_tmp/  Ignored output and scratch
```

## What each part is responsible for

The core has no interpreter dependency. The bindings expose its values and functions;
Python tests exercise the built module rather than the stub. Fixtures are inputs and
positive controls, never authority for a behaviour change. Agent bridges point to the
canonical skills and add nothing. Hooks are installed only from the primary checkout,
because all worktrees share their hook directory.

The configuration files at the root include `rustfmt.toml`, `clippy.toml`,
`rustqual.toml`, `taplo.toml`, `deny.toml`, `ruff.toml`, `mypy.ini` and
`.config/nextest.toml`; [Configuration](../reference/configuration.md) owns their meanings.
The dev shell `flake.nix` defines holds the compiler, Python and every tool, all in the
Nix store; `.nix/dev-shell` is its GC root. `.tools/parity/` holds only the parity
reference, off `PATH`. `target/py-env` is the venv `just py-develop` builds into.

## Related pages

- [Commands](../reference/commands.md)
- [Develop locally](../how-to/develop-locally.md)
