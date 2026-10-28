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
config file, with a comment saying why. Here that file is `ruff.toml`, whose `ignore`
list carries one comment per rule, and `mypy.ini`. At a call site the only form is
`# noqa: RULE` with a reason on the line it names, never a file-wide suppression, and
ruff's `unused-noqa` rule reports a suppression that no longer suppresses anything.

## Unreachable is not untested

A branch no input can reach is not a gap in the tests; it is code that should not exist,
whether a bounds check after a modulo, a null fallback after an exhaustive assignment,
or a defensive default no caller can trigger. Delete it rather than cover it with a
contrived test. There is no coverage floor here; the golden suite over captured pages is
what proves the pipeline, and a construct it lacks is a fixture to capture.

## Evidence must be able to fail

Tests assert observable results rather than that an internal function was called.
The linter positive controls must fail with the fixture's own named violations;
a missing input or a tool error is no evidence. The offline wheel smoke installs the
built artefact into a fresh environment and runs Python with `-I`, so an editable
checkout cannot hide a broken wheel. A golden snapshot that changes is a fidelity change
made visible; the quality gates on every page are measured, never asserted, and a page
that fails one is flagged rather than passed.

## The page is the arbiter

When a snapshot and a normalizer disagree, compare both against the fixture's HTML. The
output that keeps more of the page wins; neither is adjusted merely until it passes. A
construct Markdown cannot carry is kept as sanitized HTML, never dropped.

## Related pages

- [Quality gates](../reference/quality-gates.md)
- [Commands](../reference/commands.md)
