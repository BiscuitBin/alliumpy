# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
A version `X.Y.Z` means the wheel wraps allium-tools `X.Y.Z`; `X.Y.Z.postN` is the
Nth packaging-only fix of that wheel (decision 0010). Only this repository's changes
are listed here; upstream's own changes belong to upstream's release notes.

## [Unreleased]

## [3.6.1.post1] - 2026-11-23

A packaging-only release of the wheel that wraps allium-tools 3.6.1: the crates, the
`allium-parser` pin and `allium --version` stay at 3.6.1 (decision 0010). Because
`3.6.1.post1` is a distinct version, `alliumpy==3.6.1` does not select it, while
`alliumpy==3.6.1.*` and `alliumpy>=3.6.1` do.

### Added

- Renovate over every pin except `allium-parser` (`renovate.json`, decision 0017), and
  the upstream-bump runbook,
  `docs/how-to/bump-upstream.md`, with `scripts/vendor_cli.py`, which generates the
  vendored command.
- `alliumpy.check` and `alliumpy.analyse`, which run upstream's command in process and
  return its reports as immutable `Report`, `FileReport` and `Finding` values with the
  command's exit status; a panic, or output that is not the command's reports, raises
  `AlliumError`.
- The `alliumpy` console script with one subcommand, `alliumpy gate PATHS`, which runs
  `check` and `analyse`, prints each diagnostic and finding, and exits 1 on any error or
  warning or an unreadable file (decision 0019). `uvx alliumpy gate specs/` needs no
  `--from`. `--fail-on error|warning|info` and `--fail-on-findings` choose what fails,
  and `--format github` prints GitHub Actions annotations.
- Typer, the wheel's first runtime dependency (`typer>=0.29.2,<0.30`), which brings
  pydantic, rich, shellingham and annotated-doc with their own dependencies; only the
  gate script imports it.

## [3.6.1] - 2026-11-05

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

[Unreleased]: https://github.com/BiscuitBin/alliumpy/compare/v3.6.1.post1...HEAD
[3.6.1.post1]: https://github.com/BiscuitBin/alliumpy/releases/tag/v3.6.1.post1
[3.6.1]: https://github.com/BiscuitBin/alliumpy/releases/tag/v3.6.1
