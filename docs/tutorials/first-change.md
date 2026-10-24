---
title: "Make your first change"
kind: "tutorial"
audience: ["contributor", "agent"]
canonical_for: ["first_change_tutorial"]
requires: []
---

# Make your first change

About half an hour after setup, from a green baseline through one small change and its
tests. The first run needs network access, rustup and pixi;
[Develop locally](../how-to/develop-locally.md) describes them. The change crosses the
core, native binding, Python stub and pytest case. Work in a disposable branch or
worktree: this exercise demonstrates a field addition, rather than asking you to ship it.

## 1. Get the workspace running

```console
just initialize
just check
```

Initialization installs pinned tools and dependencies. It installs hooks only from the
primary checkout, never formats, and never stages, commits, tags or pushes.
Read the first gate failure before editing; start only from a green baseline.

## 2. See the crates

```console
just doc
```

Open `target/doc/alliumpy_core/index.html` and find `Diagnostic` and `parse`.
Their source is `crates/alliumpy-core/src/lib.rs`. Then read the separate pyclass in
`crates/alliumpy/src/lib.rs` and the canonical Python description in
`crates/alliumpy/python/alliumpy/_alliumpy.pyi`.

## 3. Read what decides the behaviour

The core converts upstream byte spans with `allium_parser::lexer::SourceMap`.
`line_col` returns zero-based line and byte column; the public values add one.
This exercise exposes `end_col: u32`, the one-based byte column of the exclusive span
end, converted through that same map. For `?` at the start of the second line, the
start column is 1 and the exclusive end column is 2.

Before repeating the exercise on a later main, inspect `Diagnostic` in all three layers.
If `end_col` already exists, use a disposable checkout of the pre-field revision named
in this ticket's evidence, or remove that field and its tests in your disposable branch
before beginning. Do not overwrite a real later feature in a branch you intend to keep.
Later refactoring may move the functions; find them by name and preserve their structure.

## 4. Change something: the core test first

Add this inside the existing `tests` module in `crates/alliumpy-core/src/lib.rs`:

```rust
#[test]
fn diagnostic_end_column_is_one_based() {
    let diagnostics = super::parse("-- allium: 1\n?\n");
    assert_eq!(diagnostics[0].end_col, 2);
}
```

Run `just test`. It must fail to compile with `E0609`, no field `end_col` on
`Diagnostic`. A test green before the change is either already covered or vacuous.

## 5. Add the field, then cross the Python boundary

Add the documented field to the core struct after `col`:

```rust
/// One-based byte column of the exclusive span end.
pub end_col: u32,
```

In `parse`, immediately after the existing `line_col(diagnostic.span.start)` call, add:

```rust
let (_, end_col) = source_map.line_col(diagnostic.span.end);
```

Set `end_col: end_col + 1` in the struct literal built there. Add `end_col: 1` to the
empty-source test's expected diagnostic literal: its empty span ends at offset zero.
Run `just test` again; the new assertion and existing doctest must pass.

A core field alone does not expose a Python attribute. The core type is
`#[non_exhaustive]`, and Python has a separate pyclass. In the current binding that
class stores `inner: alliumpy_core::Diagnostic`; `parse` moves each core value into it.
There is no field-copying `From` implementation to update in this baseline. If a later
binding uses one, carry the new field through it as well.

Append this test to `crates/alliumpy/tests/test_parse.py`:

```python
def test_diagnostic_end_column() -> None:
    """Expose the one-based exclusive end column."""
    diagnostics = alliumpy.parse("-- allium: 1\n?\n")
    expected_end_col = 2
    assert diagnostics[0].end_col == expected_end_col
```

Run `just py-test`: it rebuilds, then fails with `AttributeError`. pytest reads the
built extension, never the stub. In the binding's existing `#[pymethods]` block add:

```rust
/// One-based byte column of the exclusive span end.
#[getter]
const fn end_col(&self) -> u32 {
    self.inner.end_col
}
```

Append `, end_col={}` immediately before `)` in the Rust `__repr__` format string and
append `self.end_col()` after `code` in its argument list, with a comma after `code`.
In `TestDiagnostic.test_repr`, replace the assertion with adjacent strings to stay
within the 100-character Python line limit:

```python
assert repr(broken_diagnostic()) == (
    f"Diagnostic(line=5, col=9, severity='error', message={BROKEN_MESSAGE!r}, "
    "code=None, end_col=10)"
)
```

Keep the method's existing indentation. That test uses the broken fixture, whose `?`
starts at byte column 9 and ends at column 10. Keep the separate new test above, which
checks column 2 for its smaller input.

Run `just py-test` again: all tests pass. Then run `just py-stubtest`, which rebuilds
through `py-develop` and reports `Diagnostic.end_col` missing from the stub.
Inside `class Diagnostic` in `_alliumpy.pyi`, after the other properties, add:

```python
@property
def end_col(self) -> int:
    """One-based byte column of the exclusive span end."""
```

Match the surrounding indentation and blank lines. Run `just py-stubtest` again.
This time it passes: the runtime and declared API agree.

## 6. Run the whole gate

```console
just check
```

It runs every recipe in order and proves the run did not modify the worktree. Read only
the first failure; later ones are often consequences. If a gate fails, do not work
around it — [Troubleshooting](../operations/troubleshooting.md) covers common causes.

## 7. Commit or discard the exercise

Inspect the diff. A real API change lands the core field, binding, representation,
stub and asserting tests together. The pre-commit hook runs read-only lint checks;
it does not replace the whole gate. In a disposable exercise, remove the worktree when
you have read the results. Nothing is pushed without explicit authorization.

## What you just touched

One upstream span, a core assertion and conversion, a Python assertion and getter,
the representation contract, and the stub. Each failure showed which boundary remained
unimplemented. That is the loop for a real conversion change too.

## Related pages

- [Develop locally](../how-to/develop-locally.md)
- [Test and debug](../how-to/test-and-debug.md)
- [API reference](../reference/api.md)
