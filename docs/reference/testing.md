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
versions, exports, argument conversion and the public exception. Runtime changes need
both asserting pytest cases and the matching native implementation.

`just py-stubtest` also rebuilds, then imports `alliumpy._alliumpy` and compares it with
`_alliumpy.pyi`, the canonical native API description. Its current allowlist contains no
discrepancies; an entry hides a discrepancy and must have a named, ticketed reason. A
deliberate runtime/stub mismatch must fail. mypy checks declared types; it does not prove the native module implements them.

## Installed wheel smoke

`just wheel-smoke` empties dist and builds the release wheel, requires exactly one real
wheel, creates a fresh venv on pixi's interpreter with no Python download, and installs
with `--offline --no-index --no-deps`. Isolated Python (`-I`) imports that installation,
parses the clean and broken smoke fixtures and checks versions. The installed console
script must print upstream's version string and exit 0 from `allium check` on the clean
fixture.
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
No snapshot harness exists yet; the first ticket that takes a snapshot adds the insta
dependency with its decision-0004 note.

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

## Command parity

`just parity` is POSIX-only and outside `check`, because its reference needs the network
to build; the `parity` CI job runs it on Linux. The reference is upstream's `allium-cli`
built from crates.io at the pin into `.tools/parity/`, off `PATH`.
`tests/parity/run.py` runs both commands over `tests/fixtures/parity/` (upstream's
`.allium` files at the tag, plus one cross-module pair of this repository's) and the
argument matrix in `tests/parity/README.md`, and compares stdout bytes and exit status;
stderr is reported, never compared. It fails closed on an empty corpus, runs a positive
control and two negative controls, and prints `N compared, M differ`. This proves the
corpus, not every input.

`crates/alliumpy/tests/test_cli.py` then runs against the same candidate what no
argument list reaches: a broken pipe, a full or closed stdout, an argument that is not
UTF-8, SIGINT during a blocked read and the order of both streams on a terminal, each
against the reference's recorded result, plus `alliumpy.parse` against `allium check`'s
leading diagnostics over the corpus. It reads `ALLIUMPY_SMOKE_BIN`, which only
`just parity` sets, and is skipped under `py-test`. `test_run_cli.py` covers the
`_run_cli` binding itself.

## Mutation testing

`just mutants` runs cargo-mutants over `alliumpy-core` alone, on a copy of the tree that
leaves out what Git ignores, and writes `mutants.out/`. Each mutant is a small edit to
the core, such as a `+` turned into `-` or a function body replaced by a default. A
caught mutant failed a test; a missed one passed every test, so an assertion is missing;
an unviable one did not compile; a timed-out one ran past the limit cargo-mutants set
from the baseline. The run uses `cargo test`, not nextest, so a doctest can catch a
mutant. Exit 2 means a mutant was missed, 3 a timeout and 4 a failing baseline.

The scope is the core, never upstream's parser and never the pyo3 crate, whose tests are
Python's: every mutant there would be missed. The recipe's first line is a positive
control: a `--package` filter that matched nothing would otherwise report a green run
over zero mutants. cargo-mutants never mutates a function named `new` and leaves some
expressions alone, such as the `code` conversion's `map`, so tests a person wrote are the
only guard there. A missed mutant is answered with a test; only a mutant that makes no
observable difference is excluded, in `.cargo/mutants.toml`, which does not exist until
one needs it. `mutants.yml` runs the recipe weekly and by hand.

## Benchmarks

`just bench` runs the divan benchmarks under `crates/alliumpy-core/benches/` by hand.
`parse.rs` times `alliumpy_core::parse` over the two smoke fixtures, `ok.allium` and
`broken.allium`, each passed through `divan::black_box`. Timings measure the machine and
its load, so no benchmark runs in CI or the gate; `just clippy` compiles the bench, so
one that stops building still fails the gate.

## Fuzzing

`fuzz/` is its own crate outside the workspace, with its own `fuzz/Cargo.lock`. An
excluded crate cannot inherit `[workspace.lints]`, so its manifest repeats the root's
`forbid` levels and its Clippy table; `lock-check`, `fmt-check` and `clippy` reach it
by `--manifest-path`. Its one target, `parse`, decodes arbitrary bytes as UTF-8 and, when
they are valid, passes them through `alliumpy_core::parse`, asserting that every line and
column is at least one. A panic anywhere below that call is a crash libFuzzer records
under `fuzz/artifacts/parse/`.

`just fuzz <target> [seconds]` runs on the pinned stable toolchain with
`--sanitizer none`, because AddressSanitizer needs nightly and every crate forbids unsafe
code. `just fuzz-build` only compiles the targets; the `rust` CI job runs it. `fuzz.yml`
fuzzes each target for 300 seconds weekly and uploads any crash. A crash inside
upstream's parser is reported upstream, not fixed here; the first local run found one
([decision 0016](../decisions/0016-mutation-bench-and-fuzz.md)).

## Related pages

- [Quality gates](quality-gates.md)
- [Quality philosophy](../explanation/quality-philosophy.md)
- [Decision 0005](../decisions/0005-rust-quality-gate.md)
- [Decision 0016](../decisions/0016-mutation-bench-and-fuzz.md)
