---
title: "Decision 0005: The Rust quality gate"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_rust_gate"]
requires: []
---

# Decision 0005: The Rust quality gate

Carried from pachinko's decision 0009 at `bf51e0d`, which carried libpawdoku's decision 0009 at `ccdd001`.

## Context

`just check` runs twenty-two recipes in order, then check-clean proves the tree
unchanged. The Rust half covers formatting, TOML, clippy, metrics, feature combinations,
doctests, core coverage, rustdoc, dependency policy and unused dependencies. [Quality
gates](../reference/quality-gates.md) owns their complete order; [decision
0007](0007-metrics-gate.md) owns the added metrics argument.

Two facts shape them. The toolchain is pinned to an exact stable release in
`rust-toolchain.toml`, so the clippy lint set is stable between deliberate bumps and `-D
warnings` cannot break with no diff. And nextest, which runs the tests, cannot run
doctests, while llvm-cov cannot measure them on stable, so doctests are a gate of their
own and sit outside the coverage figure.

## Decision

Clippy's `pedantic` and `cargo` groups, and a named set beyond them, at `warn` in the
`[workspace.lints]` table of the workspace `Cargo.toml`, and `-D warnings` on the
`clippy` recipe alone: a local build never breaks mid-edit, and the gate still fails. A
lint is silenced with `#[expect(lint, reason = "...")]` on the item it names, never a
blanket `allow`, so a suppression that stops being needed reports itself;
`allow_attributes` and `allow_attributes_without_reason` enforce that. A line-coverage
floor of 90 over `crates/alliumpy-core/src/**`, measured by `cargo llvm-cov nextest` and
enforced by `--fail-under-lines`, lowered by lowering complexity and never by lowering
the number. `cargo hack --feature-powerset` on the host checks both workspace crates,
including the Python cdylib.
rustdoc with `-D warnings --cfg docsrs`, so a broken intra-doc link fails the gate.
taplo for every TOML file, formatting and lint. `cargo-shear` for a dependency nothing
uses. nextest for unit and integration tests and `cargo test --doc` for doctests, which
run uncovered. Tool binaries come through pixi, cargo-hack through `tools.txt`, and
rustqual through `tools-source.txt`, one owner per pin (decision 0006). Clippy runs at
gate 6 and in CI but never as a commit hook, because a cold run blocks every commit for
tens of seconds to minutes.

The binding has its own `[lints]` table. Cargo does not let a member inherit the
workspace table and lower an inherited `forbid`; a local table lets the thin boundary
state its own lint choices while still forbidding unsafe code. Both tables retain that
boundary. Public core structs and enums are non-exhaustive and documented.

Unit tests live in `#[cfg(test)] mod tests` inside the module they test; integration
tests live under `crates/alliumpy-core/tests/` when needed, and doc examples are tests.
Rust's privacy model is the reason: `tests/` sees only public API, while private items
can be tested from their own module. `tests_outside_test_module` holds that shape. The
cdylib's evidence is pytest, stubtest and the installed wheel smoke; it is excluded from
nextest, doctests and coverage to avoid a libpython loader dependency there.

## Consequences

The ones that hurt. Pedantic lints produce false positives, and each needs an `expect`
with a reason rather than a shrug. The lint set moves with the toolchain pin, so every
bump is a clippy pass before anything else. The feature powerset doubles with each
feature added, on the host. The floor is a statement about unit and integration tests
only; a crate whose behaviour is best shown in doc examples earns no coverage for them.
And a cold `just check` is minutes, because clippy, the powerset, coverage and rustdoc
each build.

## What would reopen this

llvm-cov measuring doctests on stable, which would fold them into the floor. Clippy's
cold time falling enough to run as a hook. A required mutation-testing or fuzzing gate
would change what "tested" means, so the floor would be restated rather than raised. T15
adds development workflows outside `just check`, not such a required gate.

## Related pages

- [Quality gates](../reference/quality-gates.md)
- [Testing](../reference/testing.md)
- [Quality philosophy](../explanation/quality-philosophy.md)
