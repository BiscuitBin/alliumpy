# alliumpy-core

`alliumpy-core` is the interpreter-independent layer over an exact pin of
`allium-parser` from <https://github.com/juxt/allium-tools>. It converts upstream parse
diagnostics to owned types with one-based lines and byte columns and provides the
upstream version constants. It also holds the vendored CLI modules and entry points
used by the wheel's `allium` command (decision 0014).

The core has no Python or pyo3 dependency. It preserves upstream behaviour rather than
defining another parser or checker. The sibling bindings crate exposes it to Python;
this crate is not published to crates.io.

Run `just doc` from the workspace root and open `target/doc/alliumpy_core/index.html`
for its Rust API. The handbook starts at `docs/README.md`; architecture and packaging
are owned by `docs/explanation/architecture.md` and `docs/explanation/packaging.md`.

This repository is Apache-2.0; the upstream parser and vendored CLI are MIT-licensed.
