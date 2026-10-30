---
title: "Architecture"
kind: "explanation"
audience: ["contributor", "maintainer", "operator", "agent"]
canonical_for: ["system_architecture"]
requires: []
---

# Architecture

This workspace packages upstream behaviour through an interpreter-independent core and
a thin Python boundary. The parser remains upstream's; conversion and distribution are
this repository's responsibility. [Decision 0001](../decisions/0001-one-wheel-two-crates.md)
records why the tested core and the binding are separate crates.

## Workspace

The root `Cargo.toml` is a virtual manifest: it names the members, the package fields
every crate inherits, the dependency table every crate draws from, and the
`[workspace.lints]` table. `Cargo.lock` beside it is the pin.

| Layer | Responsibility |
| --- | --- |
| `allium-parser` | Upstream parser at an exact dependency pin; see [decision 0011](../decisions/0011-exact-pin-on-allium-parser.md). |
| `crates/alliumpy-core` | Converts upstream byte spans through `SourceMap` into one-based locations, preserves diagnostics, and exposes version constants. Rust unit tests, doctests and the coverage floor live here. |
| `crates/alliumpy` | Thin pyo3 cdylib with its own lint table, native functions and frozen classes. Python tests exercise the built module. |
| `crates/alliumpy/python/alliumpy` | Public imports, canonical native stub, package metadata version, and the `allium` console shim. |

## What goes where

Anything that can be unit-tested without an interpreter lives in the core. The bindings
crate holds only `#[pymodule]`, `#[pyclass]`, `#[pyfunction]` and conversions into pyo3
types. The current diagnostic pyclass stores a core diagnostic and exposes getters.
Its wrapper is separate from the non-exhaustive core type: adding a core field does not
make it a Python attribute. The tutorial demonstrates each boundary independently.

The core depends on upstream and the binding depends on the core;
[Layering](layering.md) owns the direction. [Python packaging](packaging.md) owns the
wheel argument, manifests, versions, ABI coverage and licences.

## What crosses each boundary

The Python API returns converted diagnostic values in upstream order. Errors reaching
Python use stable Rust `Display` text as the message of `AlliumError`, a `ValueError`
subclass. There is no fallible parse path yet. Public core values are
`Send + Sync + 'static`, `Clone` and `Debug`; public structs and enums are
`#[non_exhaustive]`. Python diagnostics are frozen, comparable and hashable.

## The command route

The `allium` command is upstream's, vendored. Upstream's `main.rs`, `test_plan.rs` and
`domain_model.rs` at the pinned tag live in `crates/alliumpy-core/src/cli/`, transformed
so that `alliumpy_core::cli::run(args, stdout, stderr)` returns the exit status; the
bindings expose it as the private `_run_cli`, and the console shim `_cli.py` restores
SIGINT's default unless it was inherited as ignored, points a closed standard descriptor at the null device, and exits
with that status. [Record 0014](../decisions/0014-cli-strategy.md) gives the route and
why S01 chose it over bundling a binary or waiting for upstream. `just parity` proves
stdout and exit-code parity with upstream's `allium-cli` at the pin.

T14 adds the release process and first PyPI publication.
T15 adds mutation testing, benchmarks and fuzzing; [Testing](../reference/testing.md)
will carry their evidence.
T17 adds Renovate and the upstream-bump runbook; [Maintenance](../operations/maintenance.md)
will carry that routine. None of these future deliverables is present here yet.

## Related pages

- [Repository map](../project/repository-map.md)
- [Security model](security-model.md)
- [API reference](../reference/api.md)
