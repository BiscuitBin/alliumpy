---
title: "Test and debug"
kind: "how-to"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["test_workflow"]
requires: []
---

# Test and debug

## Run the suites

```console
just test        # nextest over unit and integration tests, then the doctests
just test-doc    # the doctests alone: nextest cannot run them
just coverage    # nextest under instrumentation, with the coverage floor enforced
just clippy      # every lint the manifests declare, as errors
```

To iterate on one test, call nextest directly with its filter language, keeping the
flags `just test` passes so the run sees the same features and cannot touch the lockfile:

```console
INSTA_UPDATE=no cargo nextest run -p alliumpy-core --all-features --locked -E 'test(name)'
INSTA_UPDATE=no RUST_BACKTRACE=1 cargo nextest run -p alliumpy-core --all-features --locked -E 'test(name)'
```

The tools live in `.pixi/envs/default/bin` and `.tools/bin`, which the `Justfile` puts on
`PATH` for every recipe and your shell does not. From a shell, prefix
`PATH="$PWD/.pixi/envs/default/bin:$PWD/.tools/bin:$PATH"`, or use
`pixi run --frozen cargo nextest ...`.

Framework configuration and conventions are described in
[Testing](../reference/testing.md); this page is about narrowing down a failure.

## Narrow down a failing test

1. Run the single test first, by filter. A failure that only appears in the whole suite
   is usually shared state, and there is very little of it here: the engine has no
   globals, and every stream is constructed per test.
2. Read the assertion's left and right and, for a panic, the backtrace
   `RUST_BACKTRACE=1` prints. CI sets it for every job, so a failure in CI already
   carries one.
3. If the expectation concerns parser behaviour, compare with the pinned upstream
   implementation and documentation. Upstream is the arbiter, not the current conversion.
4. Do not weaken an assertion to make it pass. Correct the conversion or report the
   upstream issue with a reproducing input.

For bindings failures, run `just py-test`, then narrow to a file with
`.pixi/envs/default/bin/python -m pytest crates/alliumpy/tests/test_parse.py` after
`just py-develop`. Run `just py-stubtest` to compare the built module with its stub.
Run `just wheel-smoke` to test the release wheel in a fresh isolated environment.

## Read and accept a changed snapshot

1. Run `just test` or `just snapshots-check`. A mismatch prints the old and new text
   and names the snapshot. These recipes leave no pending file.
2. Read the diff and decide whether the interface change was intended. Keep the
   behaviour's asserting tests green; the snapshot establishes no correctness.
3. For an intended change, run `just snapshots-accept`. It checks both locks, reruns
   all unit and integration tests with every feature and accepts pending snapshots
   without prompting. It also deletes a `.snap` file no test refers to, such as one a
   renamed or removed test left behind. It works for an agent without a terminal as well.
4. Read `git diff -- crates/alliumpy-core` before committing and explain the change in the
   pull request or hand-back notes. Run `just snapshots-check` again: it also rejects
   a `.snap` file no test refers to.

If a run outside these recipes has left pending files, `just snapshots-review` opens
cargo-insta's interactive review at a terminal. Read each change there before accepting
it. The full rule and file locations belong to [Testing](../reference/testing.md).

## Debug a coverage failure

`just coverage` prints the summary per file and fails below the floor. For the lines
themselves, render the HTML report, which lands at `target/llvm-cov/html/index.html`:

```console
cargo llvm-cov report --html
```

That reuses the profile data a `just coverage` run left behind. From cold,
`INSTA_UPDATE=no cargo llvm-cov nextest -p alliumpy-core --all-features --locked --html`
does both at once.
Two cases look alike and are not:

- **Untested behaviour.** Add the test. This is the common case.
- **Unreachable code.** A defensive branch no input can reach, such as a `match` arm for
  a value the types already rule out. Remove the branch, or make the types say so, rather
  than inventing a test that reaches it artificially.

Doctests are not measured, so a doc example does not count toward the floor; the lines
it exercises need a unit or integration test as well. Never lower `coverage_floor` in the
`Justfile`.

## Debug a locked-resolution failure

A `--locked` failure means `Cargo.lock` disagrees with a manifest: a dependency was edited
without relocking. Read [Maintain dependencies](maintain-dependencies.md) and relock
deliberately; never run `cargo update` from inside a fix for something else.

## Related pages

- [Testing](../reference/testing.md)
- [Quality gates](../reference/quality-gates.md)
- [Troubleshooting](../operations/troubleshooting.md)
