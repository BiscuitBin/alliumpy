---
name: review-change
description: Review a change in this repository against its invariants, specifications, tests, and documentation contract.
---

# Review a change

1. Read `AGENTS.md`, `crates/alliumpy/python/alliumpy/_alliumpy.pyi` and upstream's
   behaviour at the pin for the value in question. Review the whole diff.
2. Check the nine invariants in `AGENTS.md` one at a time:
   - Upstream decides behaviour: command stdout and exit-code parity over the corpus;
     Python results converted, never reinterpreted.
   - `alliumpy` depends on `alliumpy-core`, which depends on `allium-parser`; never the
     reverse, with pyo3 only in `crates/alliumpy`.
   - Public core types are `Send + Sync + 'static`, `Clone` and `Debug`; public enums
     and structs are `#[non_exhaustive]`; errors have stable `Display` text.
   - `#![forbid(unsafe_code)]` in every crate, through the core's inherited workspace
     table and the bindings crate's own table.
   - Clippy pedantic with the lint tables; `#[expect(lint, reason = "...")]` only,
     with the documented pyo3 macro-output exception confined to the bindings table.
   - Coverage stays at or above 90% over `crates/alliumpy-core/src/**`; pytest,
     stubtest and wheel smoke exercise the bindings through `just check`.
   - `Cargo.lock` is the pin; full `x.y.z` caret ranges except the exact parser pin;
     cargo gates use `--locked` and maturin has `locked = true`. Snapshot recipes check
     locks first and run offline; cargo shear cannot accept the flag (T05's known gap).
   - No dependency is added without the decision-0004 note.
   - One version: stripping `.postN` from the wheel version gives both crate versions,
     the parser pin and the command version. `just version-check` rejects a bare pin bump.
3. Check the change against upstream at the pin: a reinterpreted diagnostic, reordered
   field or different exit code is a finding unless a decision record authorises it.
   Check command changes with `just parity`.
4. Check evidence: a core unit test asserts the converted upstream value; a pytest case
   exercises an exposed item; stubtest covers a stub change. A test that only asserts
   a function was called is insufficient. A public core item without an asserting
   doctest is a finding.
5. Check invariant 2's boundaries and that no public core type lost `#[non_exhaustive]`
   or `Clone`. A change to `_alliumpy.pyi` without the matching Rust and pytest change
   is a finding. The bindings crate carries no Rust tests.
6. Check documentation ownership: add durable facts to the page owning their topic in
   `docs/manifest.yml`.
7. Check scope: unrelated refactors, new dependencies and speculative abstractions are
   findings in themselves.
8. Report findings by severity with `file:line`, what breaks and the smallest fix.
   Run `just check` before concluding.
