# alliumpy

`alliumpy` brings the Allium specification parser and checker to Python users in one
wheel: a native parser API and the `allium` command for checking `.allium` files. It
uses an exact pin of upstream's `allium-parser` and vendors upstream's CLI; command
behaviour and diagnostics follow the upstream version named by the package version.
A `.postN` suffix identifies a packaging-only fix.

Upstream: <https://github.com/juxt/allium-tools>. Repository:
<https://github.com/BiscuitBin/alliumpy>.

## Install and run

Run once with uv:

```console
uvx --from alliumpy allium check <path>
```

Install the command persistently:

```console
uv tool install alliumpy
allium check <path>
```

Install into your Python environment:

```console
pip install alliumpy
```

`allium check` prints one JSON object per successfully read file to stdout and reports
read failures to stderr. Its exit status is 0 when clean, 1 on any error or warning,
and 2 when no inputs are found.

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

The Python API exposes parse diagnostics; use the command to run the checker.

## Supported platforms

Python 3.11 or newer is required. Wheels cover Linux x86_64 and aarch64 (manylinux
and musllinux), macOS arm64 and x86_64, and Windows x86_64. CPython uses `abi3-py311`
wheels, with a separate `cp314t` wheel for free-threaded Python 3.14.

On a platform without a compatible wheel, uv or pip silently falls back to building
the source distribution, which includes the vendored sources and requires a Rust
toolchain and network access.

## Licences

This repository is Apache-2.0 and upstream's parser and CLI are MIT-licensed. Both
texts ship in the wheel's `.dist-info/licenses/` directory as `LICENSE` and
`LICENSE-allium-tools`.
