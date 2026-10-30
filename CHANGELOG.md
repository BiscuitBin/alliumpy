# Changelog

This is a T00 stub; T12 replaces it.

This document will describe release changes and the upstream version each release wraps for the two-crate workspace and its Python
wheel. This page is new to this repository. The owning lane will supply the operational details,
examples, rationale and verification evidence when its ticket is implemented.
Until then this text records the intended scope and ownership of the document.

## [Unreleased]

Release notes will be added when changes are ready for users.

- Mutation testing (`just mutants`, weekly `mutants.yml`), a divan benchmark (`just bench`)
  and a stable fuzz target over `alliumpy_core::parse` (`just fuzz`, weekly `fuzz.yml`),
  all reports outside the gate (decision 0016).
- The `allium` command is upstream's `allium-cli` 3.6.1, vendored, with stdout and exit-code parity proved by `just parity` (decision 0014).
