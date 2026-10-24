---
title: "Repository map"
kind: "project"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["repository_layout"]
requires: []
---

# Repository map

The repository root is a Cargo workspace with two members. Their responsibilities
follow [Architecture](../explanation/architecture.md); the dependency direction is
[Layering](../explanation/layering.md)'s.

```text
.
├── Cargo.toml                 Workspace members, dependencies, lints and profiles
├── Cargo.lock                 Locked Cargo resolution
├── rust-toolchain.toml        Rust compiler and components
├── pyproject.toml             pixi tooling manifest
├── pixi.lock                  Tool environment resolution
├── tools.txt                  Binary-only extra tools
├── tools-source.txt           Extra tools with source builds accepted
├── Justfile                   Supported recipes
├── crates/
│   ├── alliumpy-core/
│   │   ├── Cargo.toml
│   │   └── src/lib.rs         Conversion, public values, unit tests and doctests
│   └── alliumpy/
│       ├── Cargo.toml         Thin pyo3 crate and its lint table
│       ├── pyproject.toml     maturin wheel metadata
│       ├── src/lib.rs         Native Python wrappers
│       ├── python/alliumpy/   Package, console shim, stub and py.typed
│       ├── tests/            pytest and stubtest allowlist
│       ├── LICENSE           Apache-2.0 copy for wheel
│       └── LICENSE-allium-tools  Upstream MIT text and attribution
├── tests/fixtures/            Smoke inputs and linter positive controls
├── docs/                      Handbook, manifest and decisions
├── tickets/                   Work and acceptance evidence
├── scripts/                   initialize.sh and version_check.py
├── .agents/skills/            Canonical house skills
├── .claude/skills/            Discovery bridges
├── .codex/skills/             Discovery bridges
├── .github/                   Adapters, workflows and setup action
└── target/ dist/ .pixi/ .tools/ ai_tmp/  Ignored output and scratch
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
`.pixi/envs/default/bin` holds the tooling environment; `.tools/bin` holds tools
conda-forge lacks. Neither holds the repository's compiler.

## Related pages

- [Commands](../reference/commands.md)
- [Develop locally](../how-to/develop-locally.md)
