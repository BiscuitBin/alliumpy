---
title: "Python packaging"
kind: "explanation"
audience: ["user", "contributor", "maintainer", "agent"]
canonical_for: ["python_packaging"]
requires: []
---

# Python packaging

One wheel installs the Python parser API and the `allium` console script together.
Users receive the parser version the command wraps, with no separately resolved command
package. [Architecture](architecture.md) owns the two-crate implementation;
[decision 0001](../decisions/0001-one-wheel-two-crates.md) records that choice.

## ABI and platforms

pyo3 uses `abi3-py311`: a platform's stable-ABI wheel serves CPython 3.11 and newer.
Free-threaded Python 3.14 additionally needs the separate `cp314t` wheel. T14 verifies
the maturin generator's output and rehearses that matrix before publishing.

| Platform target | Wheel coverage planned for T14 |
| --- | --- |
| Linux x86_64 | manylinux and musllinux |
| Linux aarch64 | manylinux and musllinux |
| macOS arm64 | Native wheel |
| macOS x86_64 | Native wheel |
| Windows x86_64 | Native wheel and console launcher |

`just check` builds and smokes only the developer's platform, using pixi Python 3.14.
The POSIX Justfile and pixi platforms cover Linux x86_64 and macOS arm64. T01's CI adds
a Python 3.11 smoke of the Linux wheel to prove the abi3 floor. Other targets,
musllinux and `cp314t` are release-matrix evidence, not a claim made by a local gate.
T14's rehearsal supplies the Windows launcher and exit-code proof.

## Versions

The wheel tracks upstream: `3.6.1` wraps upstream `3.6.1`, and packaging-only fixes use
`3.6.1.postN`. Cargo cannot express that suffix, so `[project] version` in the wheel
manifest is static; it must never become `dynamic = ["version"]`.
`version-check` compares the suffix-stripped wheel version, root workspace version,
upstream pin, core constant and installed command output. Both crate manifests currently
inherit that workspace version; the script assumes this inheritance and does not read
the member manifests to verify it.
[Decision 0010](../decisions/0010-version-tracks-upstream.md) owns this policy.

## Two manifests, two owners

The root `pyproject.toml` owns pixi's tooling environment, exact tool pins, Python and
the ordered gate recipes. `pixi.lock` records its resolution. pixi searches the current
directory and parents, never nested manifests; run recipes from the repository root.

`crates/alliumpy/pyproject.toml` belongs to maturin alone and has no `[tool.pixi]` table.
It owns the distribution name, static version, Python floor, metadata, console entry
point and native module layout. `locked = true` makes its builds honour `Cargo.lock`.
Release LTO remains enabled; panic behaviour remains unwind so pyo3 can turn a panic
into a Python exception. maturin sets `PYO3_BUILD_EXTENSION_MODULE`; the deprecated
pyo3 `extension-module` feature is not enabled.

## Licences

The repository is Apache-2.0, and upstream is MIT. Both texts ship under the wheel's
`.dist-info/licenses/`. The copies are `crates/alliumpy/LICENSE` and
`crates/alliumpy/LICENSE-allium-tools`, with upstream version and copyright attribution.
PEP 639 licence globs cannot leave maturin's project root, so a root-only licence
would omit a required text. T14 asserts the released wheel's contents.
[Decision 0003](../decisions/0003-apache-2-0-with-upstream-mit.md) owns the rationale.

## Source distribution

The sdist ruling is pending S01. A bundled-binary route makes it unbuildable without the
binary; other routes can cause installers on uncovered platforms to fall back to a
source build requiring Rust and network access. Python 3.10 is refused by metadata,
rather than supported by a source build. T14 keeps or drops the sdist according to
S01's ruling and checks `Cargo.lock`, licences and any vendored sources if one ships.

## Related pages

- [Install and run](../how-to/install-and-run.md)
- [Decision 0012](../decisions/0012-abi3-wheels-and-platforms.md)
