---
title: "Quality philosophy"
kind: "explanation"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["quality_philosophy"]
requires: []
---

# Quality philosophy

Gates encode decisions, not taste. Each one exists because someone decided something, and
the gate is what stops the decision quietly reverting. If a gate cannot be traced back to
a decision, it should be deleted rather than tolerated.

## Checks are read-only

Every recipe under `just check` reports and never repairs. Recipes outside it do write —
`just format` and the lock recipes among them — and `just fix` is the
one whose job is repairing what a check reported. `bg-project-check`, the runner behind
`just check`, enforces the split by snapshotting every path Git does not ignore and
comparing after every recipe, so a check that rewrites a file fails the run rather than
hiding drift.

This is why the pre-commit configuration is split in two. `.pre-commit-config.yaml` is
the gate and is what gets installed; `.pre-commit-fix.yaml` holds the mutating hooks and
runs only from `just fix`.

## Fix the cause, not the report

A suppression is a last resort: one rule, one line, with a stated reason. Lowering the
coverage threshold, disabling a lint rule at a call site, or loosening an assertion until
it passes are all ways of deleting the signal while keeping the machinery.

Where a rule is genuinely wrong for this project, the fix is to configure it once, in the
config file, with a comment saying why. Here that file is the `[workspace.lints]` table in
the root `Cargo.toml`, with `clippy.toml` beside it: `module_name_repetitions` is allowed
there because the readable name is the repeated one, and the comment says so. At a call
site the only form is `#[expect(lint, reason = "...")]` on the item it names, never a
blanket `allow`, because an expectation that stops being met is itself a warning, so a
suppression that no longer suppresses anything reports itself.

## Unreachable is not untested

Coverage distinguishes two things that look alike. A branch no input can reach is not a
gap in the tests; it is code that should not exist, whether a bounds check after a
modulo, a null fallback after an exhaustive assignment, or a defensive default no caller
can trigger. Delete it rather than cover it with a contrived test.

The corollary: do not chase the last few percent. The floor is 90 per cent of lines over
`crates/alliumpy-core/src/**`, and while the crate is small so is the denominator, so one
untested conversion branch can breach the floor on its own. Doctests are not counted,
so an example is documentation and a test of its contract, but not evidence for the
floor.

## Evidence must be able to fail

Tests assert observable results rather than that an internal function was called.
The linter positive controls must fail with the fixture's own named violations;
a missing input or a tool error is no evidence. The offline wheel smoke installs the
release artefact into a fresh environment and runs Python with `-I`, so an editable
checkout cannot hide a broken wheel. T13 adds byte-for-byte stdout and exit-code parity
against a reference built from the exact upstream release; an empty corpus must fail.

## Upstream is the arbiter

When a test and conversion disagree, compare both against upstream. Neither is adjusted
merely until it passes. The repository converts parser results, never reinterprets them.

## Related pages

- [Quality gates](../reference/quality-gates.md)
- [Testing](../reference/testing.md)
- [Architecture](architecture.md)
