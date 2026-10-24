---
title: "Testing"
kind: "reference"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["testing_reference"]
requires: []
---

# Testing

Tests distinguish the interpreter-independent conversion from the native Python API and
the installed distribution. [Test and debug](../how-to/test-and-debug.md) describes
iteration; this page owns frameworks, scope and conventions.

## Rust tests and doctests

`just test` runs core unit and integration tests through cargo-nextest, excluding the
bindings cdylib, then runs `cargo test --doc`. nextest cannot run doctests. The bindings'
Rust test executable would need libpython at load time; pytest exercises that boundary.
Unit tests live in `#[cfg(test)] mod tests` beside their module; integration tests belong
under the core crate's `tests/` when public-boundary scenarios need them. Test names
state the behaviour. The existing core tests cover diagnostic conversion, source
coordinates, each severity and version identification; a doctest parses valid source.

The nextest default profile fails fast; CI's profile can retain all results and a JUnit
report. Keep `--all-features` and `--locked` when filtering a test directly.
Expected values come from a worked upstream example, not a second copy of the conversion.

## Python tests and the stub

`just py-test` rebuilds the native module through `py-develop` and runs pytest under
`crates/alliumpy/tests/`. Tests import the built extension, never the stub. Current cases
cover valid and invalid source, locations, equality and hashing, exact Python repr,
versions and exception pickle identity. Runtime changes therefore need both asserting
pytest cases and the matching native implementation.

`just py-stubtest` also rebuilds, then imports `alliumpy._alliumpy` and compares it with
`_alliumpy.pyi`, the canonical native API description. Its allowlist is reviewed in T03;
an entry hides a discrepancy and must remain narrow. A deliberate runtime/stub mismatch
must fail. mypy checks declared types; it does not prove the native module implements them.

## Installed wheel smoke

`just wheel-smoke` empties dist and builds the release wheel, requires exactly one real
wheel, creates a fresh venv on pixi's interpreter with no Python download, and installs
with `--offline --no-index --no-deps`. Isolated Python (`-I`) imports that installation,
parses the clean and broken smoke fixtures and checks versions. The installed console
script must print upstream's version string. T13 adds a clean `check` invocation.
A release build on every gate is the cost of testing the artefact that will ship.

## Coverage

cargo-llvm-cov runs core nextest tests under instrumentation; `just coverage` fails when
lines over `crates/alliumpy-core/src/**` fall below 90 percent. The bindings are measured
by pytest, stubtest and wheel smoke, outside llvm-cov. Doctests are not counted on the
stable toolchain, so `test-doc` runs them uncovered. The floor lives in the Justfile.
One untested branch matters on a small denominator. The recipe writes ignored
`target/llvm-cov/lcov.info`; HTML can be rendered from the same data.

Coverage counts a snapshot test like any other test. That count establishes no
behaviour: every guarantee needs its own asserting test even if a snapshot runs the
same code. Delete unreachable defensive code rather than contrive a way to cover it.

## Snapshots

A snapshot has two purposes and no other:

1. Show a reviewer what a value looks like without running the code.
2. Detect interface changes as a diff in a committed file.

A snapshot never verifies correctness. The first one records what the code printed
that day, not an independently proved answer. Each behaviour keeps its own asserting
test. Add snapshots after those tests are green, never as the red test in a TDD loop.
The insta dependency arrives with the first snapshot; no snapshot harness exists yet.

Use `snapshot_` names and fixed inputs. Render pictures from public values in test code;
add no production API just to feed a snapshot. Small values can use Debug or a serialized
form. Pictures have no trailing whitespace and end with a newline. Store `.snap` files
beside the source's directory in `snapshots/`, never inline in Rust; commit them.
Pending `*.snap.new` and `*.pending-snap` files stay ignored.

`test`, `coverage` and `snapshots-check` refuse mismatches without writing pending files.
The snapshot gate runs all core tests and rejects unreferenced snapshots. Because
cargo-insta cannot forward `--locked`, snapshot recipes validate both locks and then run
offline. Review a changed picture, run `snapshots-accept` for intended changes, read its
diff and explain it. `snapshots-review` offers interactive review at a terminal.

## Future evidence

T13 adds POSIX parity: the exact crates.io-built CLI reference stays off PATH, the
harness compares stdout byte for byte and exit status across upstream files and directory
inputs, and an empty corpus or a non-firing positive control fails. This proves the
corpus, not every input. T15 adds mutation testing, benchmarks and fuzzing outside the
aggregate gate; their tools and results are not present yet.

## Related pages

- [Quality gates](quality-gates.md)
- [Quality philosophy](../explanation/quality-philosophy.md)
- [Decision 0005](../decisions/0005-rust-quality-gate.md)
