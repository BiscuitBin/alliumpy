---
name: rust-change
description: Implement or review a change to the core or the bindings crate with the layering, tests and documentation evidence the invariants require.
---

# Change a crate

1. Read `AGENTS.md` and `docs/explanation/architecture.md`. Identify the crate:
   `crates/alliumpy-core` holds conversions and constants without an interpreter;
   `crates/alliumpy` is the thin bindings crate. Cargo enforces the direction
   `alliumpy` → `alliumpy-core` → `allium-parser`, never the reverse; pyo3 appears only
   in `crates/alliumpy`. A public core item exposed to Python is part of that API's shape.
2. Find upstream's behaviour at the pin. For a conversion, read how `allium-cli`
   computes the same value and assert it in a test. Ticket-scoped scaffolding without
   parser or command behaviour may cite the ticket instead; behaviour still follows
   invariant 1.
3. Keep the lint boundary: the core inherits the workspace table; the bindings crate
   has its own `[lints]` table, including `unsafe_code = "forbid"`. A lint pyo3's macro
   output trips may be allowed there with a comment naming the macro, never in the
   workspace table. Keep pedantic enabled and unsafe code forbidden in both crates.
4. Derive the test from upstream's result before implementing, and confirm it fails
   first. Unit tests live in the core module they test under `#[cfg(test)]`; public
   items carry doctests that assert. The bindings crate has no Rust tests. An item the
   binding exposes needs a pytest case under `crates/alliumpy/tests/`, with the stub
   and Rust binding changed together. Use `python-change` for that evidence.
5. Public core types are `Send + Sync + 'static`, `Clone` and `Debug`; public enums and
   structs are `#[non_exhaustive]`. Errors have stable `Display` text: it becomes the
   Python exception's message (invariant 3).
6. Silence an item lint only with `#[expect(lint, reason = "...")]` on the item it names;
   the macro-output exception belongs in the bindings table as step 3 describes.
7. Run `just fmt-check`, `just clippy`, `just test`, `just coverage` and, for public
   documentation, `just doc`, then `just check` before handoff. These test and coverage
   recipes exclude the bindings crate. Snapshot checks validate locks first and run
   offline because cargo-insta cannot forward `--locked`; cargo shear has no such flag
   either (the invariant 7 wording gap is recorded in T05).
8. Report by `file:line`: what changed, which upstream behaviour it reproduces, and
   which test proves it.
