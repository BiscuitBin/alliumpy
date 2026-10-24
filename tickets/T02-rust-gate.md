---
id: T02
title: "Rust quality gate: tool configs, the bindings crate's lint table, metrics"
status: open
depends_on: [T00]
parallel_with: [T01, T03, T05, T07, S01]
branch: ticket/t02-rust-gate
estimated_size: M
---

# T02: Rust quality gate: tool configs, the bindings crate's lint table, metrics

## Context

T00 landed both crates and working copies of P's Rust tool configuration, with the deltas
`CONVENTIONS.md` §3 names, green on the day's stable. This lane makes that configuration
final and green on this workspace: an rlib over an exact upstream pin, a pyo3 cdylib
with a lint table of its own, two dependencies, and the T00 API of `CONVENTIONS.md` §9
(nothing more is added here).

P's T02, P `tickets/T02-rust-gate.md` at `bf51e0d`, is the procedure for the tool
configuration; the metrics half of P's T10, P `tickets/T10-metrics-and-effects.md`
(its Context, step 6 and the `rustqual.toml` row), is the procedure for making
`rustqual.toml` final. The effects half of P's T10 is not carried (`CONVENTIONS.md` §1
decision 5). L's T02 already proved these recipes fire on the configuration both
repositories copy (L `tickets/T02-rust-gate.md`, its step 10 and hand-back notes), so
this lane does not repeat those proofs. It proves only what differs here: the lint
tables on the pin and on pyo3's macro output (step 2), coverage scoped to the core
(step 4), the snapshot harness with no `insta` and a stray `.snap` (step 5), rustqual
over a crate of pyo3-wrapped functions (step 6), and `deny.toml` over the
`allium-parser` and `pyo3` dependency trees on seven targets (step 7).
L `docs/decisions/0009-rust-quality-gate.md` at `ccdd001` says why each setting is what
it is (P's record at `bf51e0d` is a stub, `CONVENTIONS.md` §6);
L `tickets/T29-snapshot-harness.md` is the snapshot harness and
L `tickets/T22-metrics-gate.md` is rustqual's.

The bindings crate's own `[lints]` table is the one design decision this lane owns.
`CONVENTIONS.md` §3 "The two crates" states the rule: a copy of the workspace table with
`unsafe_code = "forbid"` kept, and any lint pyo3's macro output trips set to `allow` with
a comment naming the macro and the reason. T00 wrote whatever that table needed to be
green on the day (`CONVENTIONS.md` §12 claims 3 and 8); this lane makes every entry in
it proven and justified, or returns it to the workspace table's entry.

## Goal

`fmt-check`, `toml-check`, `clippy`, `metrics`, `features`, `test`, `test-doc`,
`coverage`, `doc`, `deny`, `deps-unused` and `snapshots-check` are each green on real
code, every configuration file this lane owns is final with a comment for each
non-default setting, and every `allow` in `crates/alliumpy/Cargo.toml`'s `[lints]`
table that differs from the workspace table (`module_name_repetitions` and
`multiple_crate_versions` are the workspace's own) is one that clippy fires on pyo3's
macro output when the entry is set to `warn`.

## Non-goals

- No dependency, so `Cargo.lock` changes only if a manifest field does
  (`CONVENTIONS.md` §11). `serde_json` waits for S01 or T13 (`CONVENTIONS.md` §2).
- No new public item in either crate beyond what a proof needs and then removes; the API
  is `CONVENTIONS.md` §9's and grows in T03 and T13.
- No edit to the `Justfile`, `crates/alliumpy/pyproject.toml` or any file under
  `crates/alliumpy/python/`, `crates/alliumpy/tests/` or `tests/` (frozen, T03's or
  T13's; `CONVENTIONS.md` §3).
  A recipe flag found wrong is handed back as a T00 follow-up.
- No effect-crate ban anywhere: this repository has no effects boundary
  (`CONVENTIONS.md` §1 decision 5).
- No change to the coverage floor or its scope: `coverage_floor` and `-p alliumpy-core`
  are the `Justfile`'s (`CONVENTIONS.md` §4).

## Files touched

| Path | Class | Content |
| --- | --- | --- |
| `Cargo.toml` | final | the lint table, `[workspace.dependencies]`, profiles |
| `Cargo.lock` | generated | only if a manifest field moves |
| `rustfmt.toml` | final | P's, verified on the pin |
| `clippy.toml` | final | P's keys, verified on the pin |
| `taplo.toml` | final | P's, plus `tests/fixtures/**` excluded |
| `deny.toml` | final | licences, seven targets, L's `openssl-sys` ban, crates.io only |
| `.config/nextest.toml` | final | P's profiles |
| `rustqual.toml` | final | P's thresholds, the comments rewritten for this workspace |
| `crates/alliumpy-core/Cargo.toml` | final | package metadata the `cargo` lint group needs; `allium-parser` from the workspace |
| `crates/alliumpy-core/src/lib.rs` | final | crate docs, the constants, `Severity`, `Diagnostic`, `parse`, tests |
| `crates/alliumpy/Cargo.toml` | final | package metadata, `cdylib`, the path dependency, `pyo3` from the workspace, its own `[lints]` table |
| `crates/alliumpy/src/lib.rs` | final | the `#[pymodule]`, every item documented where the table requires it |
| `tickets/T02-rust-gate.md` | ticket | `status:` and hand-back notes |

## Steps

1. Create the worktree after T00 has merged. Run `just check` on the untouched worktree
   and quote its last line as the baseline (`CONVENTIONS.md` §11).
2. **The lint tables on the pin.** Run `just clippy` and read the clippy changelog between
   1.98 and the pin for lints added to the pedantic, cargo or restriction groups the
   workspace table names. Each new lint is either kept (and satisfied) or set in the table
   with a comment. The changelog is fetched (network, authorised) with
   `curl -fsS -o ai_tmp/clippy-changelog/CHANGELOG.md` from
   `https://raw.githubusercontent.com/rust-lang/rust-clippy/master/CHANGELOG.md` into
   that new, empty directory and read as data (`CONVENTIONS.md` §11). Confirm every
   `clippy.toml` key still exists under its name on the pin
   (`CONVENTIONS.md` §12 claim 3): a green `just clippy` is the check, because clippy
   errors on a key it does not know (L `tickets/T02-rust-gate.md` step 10 quoted that
   error on a misspelt key). Then the bindings crate's table: for each `allow` T00
   wrote in `crates/alliumpy/Cargo.toml`, set it to `warn` in turn and run `just clippy`
   (removing the line is not a probe: an allow-by-default lint, like rustc's
   `missing_docs` or any clippy restriction lint, is silent when its line is removed,
   whether or not the macro trips it); keep the `allow` only if the diagnostic then
   carries the note `this error originates in the attribute macro` (or
   `in this macro invocation`) naming a pyo3 macro (`#[pymodule]`, `#[pyclass]`,
   `#[pymethods]`, `#[pyfunction]`, `create_exception!`); a diagnostic without that note
   is on a hand-written line. Write the macro's name and the lint's message into its
   comment. An `allow` that stays silent at `warn` is returned to what the workspace
   table has for that lint: the workspace's own line when the workspace names the lint,
   or deleted when the workspace reaches it only through the `pedantic` or `cargo` group,
   so the table stays a copy of the workspace's (`CONVENTIONS.md` §3). An `allow` that
   hides a lint on a hand-written line is replaced by a fix in the code or an
   `#[expect(lint, reason = "...")]` on that line (`CONVENTIONS.md` §12 claim 8).
   Confirm `unsafe_code = "forbid"` is in that table and that the crate compiles under it
   (`CONVENTIONS.md` §1 fact 3). Last, the workspace table: diff `[workspace.lints]`
   against P `Cargo.toml` at `bf51e0d`; for each entry T00 added or changed for the core
   (T00 step 5), restore P's level, run `just clippy`, and either fix the core, use
   `#[expect(lint, reason = "...")]` there, or keep the entry with a comment quoting the
   message.
3. **The manifests.** Both package tables carry what the `cargo` lint group requires
   (`description`, `keywords`, `categories`, `readme`, `license`, `repository`), every
   shared field `.workspace = true`, and `publish.workspace = true` inheriting the
   workspace's `publish = false`. `[workspace.dependencies]` holds
   `allium-parser = "=3.6.1"` and
   `pyo3 = { version = "0.30.1", features = ["abi3-py311"] }`
   exactly once each (`CONVENTIONS.md` §3); neither crate manifest writes a registry
   dependency's version, and the path dependency's `version = "3.6.1"` stays (§3).
   `[profile.release]` keeps `lto = "fat"`, `codegen-units = 1` and the default `panic`
   with L's comment that pyo3 needs `unwind`; `[profile.test]` keeps `opt-level = 1`.
   `taplo fmt` after every edit, because the dependency-table rule reorders keys.
4. **Coverage scoped to the core** (`CONVENTIONS.md` §12 claim 13). `just coverage`, then
   `cargo llvm-cov report --show-missing-lines`, its table quoted in full: every file row
   is under `crates/alliumpy-core/src/` with a non-zero `Lines` count and an empty
   missing-lines column, and no row names `crates/alliumpy/` (the quoted rows are the
   positive control, `CONVENTIONS.md` §11).
   If a core branch is uncovered, add the unit test that covers it; never lower the floor.
5. **The snapshot harness without insta** (`CONVENTIONS.md` §12 claim 16).
   `just snapshots-check` green on the tree, which proves `cargo insta test` accepts
   `--workspace --exclude alliumpy`; then add a stray
   `crates/alliumpy-core/src/snapshots/stray.snap` in a scratch commit (where insta would
   put one, L `tickets/T29-snapshot-harness.md`) and confirm `--unreferenced reject`
   fails on it: quote `just snapshots-check; echo "exit $?"` there, non-zero, in the
   hand-back notes. Record that the first ticket to take a snapshot adds `insta` with the
   decision-0004 note.
6. **`rustqual.toml`** (`CONVENTIONS.md` §12 claim 17). P's thresholds and every comment
   that still holds; the header names `crates/alliumpy-core` and `crates/alliumpy` and
   the renumbered decision (`CONVENTIONS.md` §8, 0007); comments that name P's crates
   rewritten or removed. `just metrics` green on both crates, both
   `(N functions analyzed)` lines quoted in the hand-back notes with N > 0. If rustqual
   reports a finding on a hand-written fn a pyo3 attribute wraps, the hand-back notes
   record the finding and whether a `qual:allow` pin, a threshold or a code change
   answered it; a threshold is changed only with a comment saying which macro forced it.
7. **`deny.toml`.** P's `[licenses]`, `[bans]` and `[sources]` as they are; `[graph]
   targets` stays the seven triples T00 wrote, the wheels' (`CONVENTIONS.md` §1
   decision 6): `x86_64-unknown-linux-gnu`, `aarch64-unknown-linux-gnu`,
   `x86_64-unknown-linux-musl`, `aarch64-unknown-linux-musl`, `aarch64-apple-darwin`,
   `x86_64-apple-darwin`, `x86_64-pc-windows-msvc`, with a comment saying why. Read
   `cargo deny --locked list --threshold 0.9` (the `list` default is 0.8 and overrides
   `deny.toml`'s 0.9; `just deny` is the gate, `list` the reading) and confirm every
   licence in the `allium-parser` and `pyo3` trees is on P's allow-list, and that the
   `MIT` entry is what admits upstream; add nothing to the list without a comment naming
   the crate that needs it. `just sync` (`cargo fetch` and `pixi install`) ran inside
   `just initialize`; rerun it only on a cold cache (network, authorised). Run
   `just deny` under `CONVENTIONS.md` §11's network denial and quote it with both
   negative-control exit codes.
8. **`taplo.toml`.** P's, plus `tests/fixtures/**` in `exclude` (T13's corpus and T03's
   fixtures are not this repository's TOML to format) and the two `pyproject.toml` files
   confirmed covered by the `**/*.toml` include (`CONVENTIONS.md` §5). `just toml-check`.
9. `just check`, the final adversarial review, `just check` again if fixes landed, then
   commit.

   **Adversarial review** (`CONVENTIONS.md` §14): the lane's diff. Ask: which lint-table
   decision on the pin is unjustified or has no comment; whether each `allow` in
   `crates/alliumpy/Cargo.toml`'s `[lints]` table that differs from the workspace table
   names a lint clippy fires on macro-emitted code, shown by step 2's `warn` runs, and
   none hides a hand-written line; whether the evidence for `CONVENTIONS.md` §12 claims
   3, 8, 13, 16 and 17 proves each claim; whether `deny.toml`'s seven targets are the
   release matrix's and the offline `just deny` ran under a denial its negative controls
   proved.

## Acceptance criteria

- The twelve recipes in the Goal are green.
- The quoted `cargo llvm-cov report --show-missing-lines` table shows every file row
  under `crates/alliumpy-core/src/` with a non-zero `Lines` count, no missing line, and
  no path under `crates/alliumpy/`.
- `crates/alliumpy/Cargo.toml` carries `unsafe_code = "forbid"`, and for every other
  entry that differs from the workspace table the hand-back notes quote the clippy
  failure that appears when the entry is set to `warn`, including its
  `this error originates in the attribute macro` (or `in this macro invocation`) note
  naming the pyo3 macro (step 2); a failure without that note is on a hand-written line
  and does not justify the entry.
- `rg -n 'version' crates/*/Cargo.toml` shows no dependency version outside
  `[workspace.dependencies]` (the path dependency's `version = "3.6.1"` and each package's
  `version.workspace = true` and `rust-version.workspace = true` lines are the allowed
  matches).
- `deny.toml`'s `[graph] targets` lists exactly the seven triples of step 7, and
  `just deny` passes under `CONVENTIONS.md` §11's network denial with both
  negative-control probes failing.
- `just snapshots-check` fails on a stray `.snap` and passes without one.
- Every non-default setting in the files this lane owns has a comment saying why.
- `just check` is green, and no file outside the Files-touched table changed.
- The adversarial review in Steps ran (`CONVENTIONS.md` §14), and every valid finding is
  fixed or handed back.

## Verification

Commands below that do not start with `just` run with the pixi tools first on `PATH`, as
the `Justfile` does: `export PATH="$PWD/.pixi/envs/default/bin:$PATH"` in the shell first
(no cargo lives there, so rustup's stays the compiler).

```sh
just fmt-check && just toml-check && just clippy && just features
just test && just test-doc && just coverage && just doc && just deny && just deps-unused
just metrics
just snapshots-check
# at the scratch commit holding crates/alliumpy-core/src/snapshots/stray.snap (expected 1)
just snapshots-check; echo "exit $?"
# per `allow` in crates/alliumpy/Cargo.toml with the entry at warn (expected non-zero)
just clippy; echo "exit $?"
cargo llvm-cov report --show-missing-lines
cargo deny --locked list --threshold 0.9
rg -n 'version' crates/*/Cargo.toml
rg -n -B2 '= "allow"' crates/alliumpy/Cargo.toml
# macOS; on Linux, unshare -rn in place of sandbox-exec (CONVENTIONS.md §11)
deny='(version 1)(allow default)(deny network*)'
sandbox-exec -p "$deny" curl -fsS --max-time 10 https://static.rust-lang.org; echo "exit $?"
sandbox-exec -p "$deny" curl --noproxy '*' -fsS --max-time 10 https://1.1.1.1; echo "exit $?"
sandbox-exec -p "$deny" just deny; echo "exit $?"
just check
git status --short
```

## Hand-back notes

To be written by the executing agent: the baseline `just check` line; each lint the pin
added and what was done about it; for each `allow` in the bindings crate's table that
differs from the workspace table, the macro, the lint and the clippy output from the
`warn` run, or the note that it was returned to the workspace table's entry; the
outcome of `CONVENTIONS.md` §12 claims 3,
8, 13, 16 and 17; the licences `cargo deny --locked list` reported and which allow-list
entry admits each; the offline `just deny` run with its negative controls; the review
record (`CONVENTIONS.md` §14); any `Justfile` or frozen-file change handed back; the
sentences T11 should carry into `docs/reference/configuration.md` about the two lint
tables (T07 writes that page to the design in parallel; T11 reconciles).

## Open points

- `[profile.release]`: `lto = "fat"` and `codegen-units = 1` are what the published wheel
  is built with, and `just wheel-smoke` builds that profile on every `just check`
  (`CONVENTIONS.md` §4, "Cost"). Measure `just wheel` on the pinned machine here twice,
  once after `cargo clean --release` (the fresh-clone and CI cost) and once after a
  one-line edit to `crates/alliumpy-core/src/lib.rs` (what each `just check` after an
  edit pays, since fat LTO redoes final codegen); record both times, and if the latter
  dominates `just check`, say so and propose the trade (a thinner
  LTO for the gate is not an option, because the gate smokes the release artefact), and
  the maintainer decides.
- Whether `missing_docs` should stay `warn` for the bindings crate with documentation
  written on every hand-written item, or be allowed crate-wide. `create_exception!` takes
  a fourth, doc argument (pyo3 0.30.1 `src/exceptions.rs`); use it. Allow crate-wide only
  if step 2's `warn` probe shows a generated item that is not `#[doc(hidden)]` tripping
  the lint, and quote that item; record which.
- Whether `rustqual` should run over `crates/alliumpy` at all once T13 lands, if every
  function there is a one-line wrapper (rustqual parses source with `syn` and never sees
  macro output). Keep it
  until T13 shows a reason not to.
