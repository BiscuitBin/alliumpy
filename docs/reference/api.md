---
title: "API reference"
kind: "reference"
audience: ["user", "contributor", "maintainer", "agent"]
canonical_for: ["api_reference"]
requires: []
---

# API reference

The Python API's canonical native description is
`crates/alliumpy/python/alliumpy/_alliumpy.pyi`. `__init__.py` re-exports the nine names
below in its `__all__`; this page describes the current surface, not the larger upstream
API. Upstream documentation is at <https://github.com/juxt/allium-tools>.

## Python API

| Name | Contract |
| --- | --- |
| `parse(source: str) -> list[Diagnostic]` | Return upstream parse diagnostics in source order, with locations converted to one-based byte columns and lines. |
| `Diagnostic` | Immutable, final diagnostic with properties `line: int`, `col: int`, `severity: str`, `message: str`, `code: str \| None`. Severity is error, warning or info, not a Python enum. |
| `AlliumError(ValueError)` | Importable exception for a failed Allium operation. A Rust error maps its Display text to this message; `check` and `analyse` raise it, `parse` never does. |
| `ALLIUM_VERSION: str` | The upstream release version, currently 3.6.1. |
| `check(paths: list[str]) -> Report` | Run upstream's `allium check` on the paths, in process, and return what it printed as values: the same files, diagnostics and exit status the command gives the same arguments. |
| `analyse(paths: list[str]) -> Report` | The same for `allium analyse`, whose files also carry findings. |
| `Report` | Immutable, final result with `status: int`, `files: list[FileReport]` and `stderr: str`. |
| `FileReport` | Immutable, final per-file result with `spec_file: str`, `diagnostics: list[Diagnostic]` and `findings: list[Finding]`. |
| `Finding` | Immutable, final `analyse` finding with `type: str`, `summary: str`, `affected_entities: list[str]` and `json: str`, the finding's complete JSON object with every key the command printed. |

`check` and `analyse` follow the command exactly, because they run it (invariant 1).
`status` is the command's exit status: `check` gives 1 when any file has an error or a
warning, `analyse` gives 1 only when a file has a finding, so an error alone leaves it
0. A file that cannot be read gives 1, is named in `stderr` and has no `FileReport`; a
directory that cannot be listed is skipped silently; when no `.allium` file is found,
an empty path list included, the status is 2. A panic in the command (status 101) and
output that is not the command's JSON reports, such as `--help` among the paths, raise
`AlliumError` with a fixed message. Each `Diagnostic` in a `FileReport` sits in that
file, so it carries no file of its own. The command runs with the interpreter's lock
released.

`Diagnostic` supports value equality, hashing and an exact representation with every
field in order: `Diagnostic(line=1, col=2, severity='error', message='...', code=None)`.
The severity, message and code use Python repr quoting. Its properties are read-only;
parse supplies instances rather than a public field constructor. `Report`, `FileReport`
and `Finding` behave the same way, with a representation of every field in the order
listed above, such as `Report(status=2, files=[], stderr='No .allium files found.\n')`.

The package also defines `__version__` using installed distribution metadata. It includes
any `.postN` suffix and is outside `__all__`, as a dunder module attribute.
`alliumpy._alliumpy.ALLIUM_VERSION_STRING` is an internal native attribute serving the
console shim and stubtest only. It is not re-exported and is not public API.

## Building the Rust reference

`just doc` builds the workspace with every feature, no dependencies and
`RUSTDOCFLAGS="-D warnings --cfg docsrs"`. Open `target/doc/alliumpy_core/index.html`
for the core and `target/doc/alliumpy/index.html` for the native wrapper.
The core exposes parse, Diagnostic, Severity, the two version constants, the vendored
command under `cli`, and `report::check` and `report::analyse` with their result types. The binding's
Rust functions and pyclass are implementation details of the Python surface.

Missing documentation and broken or private intra-doc links fail the relevant gates.
Examples describe a contract and `just test-doc` compiles and runs them. Doctests are
outside stable llvm-cov's floor, so core unit tests also exercise the conversion.

## Hosted reference

`just site` empties target/doc, runs doc and writes an index linking both crates.
The reference is published at <https://biscuitbin.github.io/alliumpy/>. Deployment
runs for main while the repository is public, and does not establish that a PyPI release
exists. Both Cargo crates are `publish = false`; crates.io
and docs.rs publication are not targets.

## What the core API promises

Public core values are `Send + Sync + 'static`, Clone and Debug; public structs and enums
are non-exhaustive. New fields therefore require explicit exposure through the separate
Python wrapper and stub, as [the tutorial](../tutorials/first-change.md) demonstrates.
The parser's results are converted, never reinterpreted.

## Related pages

- [Deploy to GitHub Pages](../how-to/deploy-to-github-pages.md)
- [Architecture](../explanation/architecture.md)
- [Testing](testing.md)
