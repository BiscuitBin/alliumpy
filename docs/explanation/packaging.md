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
Free-threaded Python 3.14 additionally needs the separate `cp314t` wheel.
`release-pypi.yml` builds both for each of seven build targets, from maturin 1.15.0's
`generate-ci` output narrowed to decision 0012's platforms: 15 files with the sdist.

| Platform target | Runner | Wheels | Smoke of the abi3 wheel | Smoke of the `cp314t` wheel |
| --- | --- | --- | --- | --- |
| Linux x86_64, manylinux | `ubuntu-22.04` | abi3, `cp314t` | Host, Python 3.11 | Host, Python 3.14t |
| Linux aarch64, manylinux | `ubuntu-22.04` | abi3, `cp314t` | `python:3.11-slim` under QEMU | Built, never imported |
| Linux x86_64, musllinux | `ubuntu-22.04` | abi3, `cp314t` | `python:3.11-alpine` | Built, never imported |
| Linux aarch64, musllinux | `ubuntu-22.04` | abi3, `cp314t` | `python:3.11-alpine` under QEMU | Built, never imported |
| macOS x86_64 | `macos-15-intel` | abi3, `cp314t` | Host, Python 3.11 | Host, Python 3.14t |
| macOS arm64 | `macos-latest` | abi3, `cp314t` | Host, Python 3.11 | Host, Python 3.14t |
| Windows x64 | `windows-latest` | abi3, `cp314t` | Host, Python 3.11 | Host, Python 3.14t |

The containers are pinned by digest, and no pinned image ships a free-threaded
interpreter. Each smoke installs the one wheel its job built, offline, and checks the
version line, the exit codes of `allium check` on both fixtures, that stdout carries no
CR byte (the Windows launcher's evidence) and both licence entries. The manylinux floor
is whatever maturin-action's `manylinux: auto` image produces, and whether each runner
label exists is settled by the first rehearsal run, not by this page.
[Cut a release](../how-to/release.md) runs the matrix.

`just check` builds and smokes only the developer's platform, using pixi Python 3.14.
The POSIX Justfile and pixi platforms cover Linux x86_64 and macOS arm64. T01's CI adds
a Python 3.11 smoke of the Linux wheel to prove the abi3 floor. Other targets,
musllinux and `cp314t` are release-matrix evidence, not a claim made by a local gate.
The release workflow's rehearsal supplies the Windows launcher and exit-code proof.

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
would omit a required text. Every release build job asserts both entries in its wheel.
[Decision 0003](../decisions/0003-apache-2-0-with-upstream-mit.md) owns the rationale.

## Source distribution

The sdist is kept, as S01 ruled under the vendoring route that
[decision 0014](../decisions/0014-cli-strategy.md) records. Under that route the sdist is
complete, but installers on platforms the release matrix misses fall back to a source
build requiring Rust and network access. Python 3.10 is refused by metadata, rather than
supported by a source build. The release workflow's `sdist` job fails unless the archive
lists `Cargo.lock`, `LICENSE`, `LICENSE-allium-tools`, `crates/alliumpy-core/src/cli.rs`
and the three modules under `crates/alliumpy-core/src/cli/` as whole entries, and fails
on any `_bin/` entry. `tests/fixtures/parity/` is absent by design, so `cargo test` from
the sdist is not expected to pass.

## Attestation

The `release` job attests every file in `dist/` with `actions/attest` before anything is
published. GitHub's documentation, read on 2026-11-04, offers artifact attestations on
public repositories on every current plan and on private ones only under Enterprise
Cloud; this repository is public.
[Decision 0015](../decisions/0015-release-process.md) records what changes if that stops
holding.

## Related pages

- [Install and run](../how-to/install-and-run.md)
- [Decision 0012](../decisions/0012-abi3-wheels-and-platforms.md)
- [Cut a release](../how-to/release.md)
