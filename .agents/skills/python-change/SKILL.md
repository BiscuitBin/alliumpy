---
name: python-change
description: Implement or review a change to the Python package, its stub, its tests or the console script with the stubtest, pytest and wheel-smoke evidence the invariants require.
---

# Change the Python surface

1. Read `AGENTS.md` and `crates/alliumpy/python/alliumpy/_alliumpy.pyi` first. The stub
   is the canonical description of the Python API; what it does not describe does not
   exist to a user of the extension.
2. Decide where the change lands: a conversion or a constant belongs in the core
   (`rust-change`); a class, function or exception exposed to Python belongs in
   `crates/alliumpy/src/lib.rs`; a re-export belongs in `__init__.py`; the console
   script is `_cli.py`. Its behaviour is upstream's (invariant 1), so a change there is
   a parity change and goes through `just parity` (from T13).
3. For an exposed API change, change the three artefacts together: the stub, the Rust
   binding and the pytest case under `crates/alliumpy/tests/`. Write the pytest case
   first and watch it fail against a rebuilt extension. The bindings crate has no
   Rust tests; the core's unit tests and doctests stay in the core.
4. Every class is `#[pyclass(frozen, eq, hash)]` and `Send + Sync`, with a `__repr__`
   in `tickets/CONVENTIONS.md` §9's form: for `Diagnostic`, every field in order,
   `Diagnostic(line=1, col=2, severity='error', message='...', code=None)`, with
   severity, message and code written as Python reprs. Every error reaches Python as
   `AlliumError` with the stable `Display` text (invariant 3). Nothing derives
   `__version__` from `ALLIUM_VERSION_STRING` or the reverse (decision 0010): package
   metadata supplies the wheel's version, while upstream supplies the command's string.
5. Run `just py-lint`, `just py-typecheck`, `just py-test`, `just py-stubtest`,
   `just wheel-smoke` and `just version-check`, in that order, then `just check`.
   A stubtest failure is a disagreement to resolve, never an allowlist entry without
   a reason beside it. `just py-test` rebuilds the extension before running pytest.
6. Report by `file:line`: what changed in the stub, binding and test, and which
   upstream behaviour it reproduces.
