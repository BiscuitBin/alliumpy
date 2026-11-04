# alliumpy

[![CI](https://github.com/BiscuitBin/alliumpy/actions/workflows/ci.yml/badge.svg)](https://github.com/BiscuitBin/alliumpy/actions/workflows/ci.yml)

`alliumpy` packages the Allium specification parser and checker for Python code, and
the `allium` command for `uv` users, in one wheel. It builds against an exact pin of
upstream's `allium-parser`: <https://github.com/juxt/allium-tools>.

## Install and run

Nothing is on PyPI yet; these installation commands and supported platforms describe
the release T14 will publish.

Run once with uv:

```console
uvx --from alliumpy allium check <path>
```

Install the command persistently:

```console
uv tool install alliumpy
allium check <path>
```

Install into a Python environment:

```console
pip install alliumpy
```

Python 3.11 or newer is required. The release targets Linux x86_64 and aarch64
(manylinux and musllinux), macOS arm64 and x86_64, and Windows x86_64, with
`abi3-py311` wheels and a separate `cp314t` wheel for free-threaded Python 3.14.
See `docs/how-to/install-and-run.md` and `docs/explanation/packaging.md` for details.

## Python API

`parse(source: str) -> list[Diagnostic]` returns upstream parse diagnostics in source
order. `Diagnostic` has immutable `line`, `col`, `severity`, `message` and `code`
properties; locations use one-based lines and byte columns. `AlliumError` subclasses
`ValueError`, and `ALLIUM_VERSION: str` identifies the upstream release.

```python
import alliumpy

diagnostics = alliumpy.parse("-- allium: 1\n?\n")
print(diagnostics[0])
print(alliumpy.ALLIUM_VERSION)
```

The command's behaviour and diagnostics are upstream's, at the upstream version named
by the package version; packaging fixes add a `.postN` suffix. `just parity` proves
command stdout and exit-code parity over the corpus. The Python API exposes parse
diagnostics; the command also runs the checker. See `docs/reference/api.md`.

## Contribute

Read the prerequisites in `docs/how-to/develop-locally.md`, then from a clone run:

```console
just initialize
just check
```

The handbook starts at `docs/README.md`. The repository is public, and the hosted Rust
API reference is at <https://biscuitbin.github.io/alliumpy/>. Agents read `AGENTS.md`
first.

## Licences

This repository is Apache-2.0 (`LICENSE`). Upstream's MIT text ships in the wheel as
`LICENSE-allium-tools`; see `docs/explanation/packaging.md`.
