# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
A version `X.Y.Z` means the wheel wraps allium-tools `X.Y.Z`; `X.Y.Z.postN` is the
Nth packaging-only fix of that wheel (decision 0010). Only this repository's changes
are listed here; upstream's own changes belong to upstream's release notes.

## [Unreleased]

### Added

- The two-crate foundation: interpreter-independent `alliumpy-core` over an exact
  `allium-parser` pin, and thin pyo3 bindings packaged as one `alliumpy` wheel.
- The Python API: `parse`, immutable `Diagnostic`, `AlliumError` and `ALLIUM_VERSION`.
- The `allium` command through vendored upstream CLI modules in the core
  (decision 0014).
- The read-only `just check` gate, pinned tools and hooks, the handbook and decision
  records, and the agent contract with its skills and bridges.

- Mutation testing (`just mutants`, weekly `mutants.yml`), a divan benchmark (`just bench`)
  and a stable fuzz target over `alliumpy_core::parse` (`just fuzz`, weekly `fuzz.yml`),
  all reports outside the gate (decision 0016).
- The `allium` command is upstream's `allium-cli` 3.6.1, vendored, with stdout and exit-code parity proved by `just parity` (decision 0014).

[Unreleased]: https://github.com/BiscuitBin/alliumpy/commits/main/
