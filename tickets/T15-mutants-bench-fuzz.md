---
id: T15
title: "Mutation testing, benchmarks and fuzzing over `alliumpy-core`"
status: open
depends_on: [T11]
parallel_with: [T12, T13, T14]
branch: ticket/t15-mutants-bench-fuzz
estimated_size: M
---

# T15: Mutation testing, benchmarks and fuzzing over `alliumpy-core`

## Context

L's spike S03 measured cargo-mutants, divan and cargo-fuzz on L's crate and drafted three
build tickets: L `tickets/S03-bench-fuzz-mutants.md` lines 553-687 (mutation testing),
688-752 (benchmarks) and 753-911 (fuzzing), with the evidence above them from line 154
(stable fuzzing with `--sanitizer none` is argued from line 255; cargo-mutants' exit codes
and its `.cargo/mutants.toml` from line 375). P adapted those drafts as its T15 and T16,
P `tickets/T15-mutation-testing.md` and P `tickets/T16-bench-and-fuzz.md`, which this
ticket folds into one (`README.md`, "Index"). Read the three drafts and P's two tickets
first; they give the recipe text, the workflow shapes, the doc changes and the reasons,
and this ticket does not restate them.

What differs here. The subject is `crates/alliumpy-core` alone: the conversion layer over
upstream's parser (`CONVENTIONS.md` §9, "The T00 API") and, if S01 chose vendoring and
T13 has merged, the vendored CLI under `crates/alliumpy-core/src/cli/`, with one rule: if
S01 ruled that `src/cli/` is unit-tested in Rust to the coverage floor, its mutants are in
scope like the rest of the core; if S01 excluded it from the floor, `.cargo/mutants.toml`
excludes it too (`exclude_globs = ["crates/alliumpy-core/src/cli/**"]`, with a comment
that parity, T13, is the test of upstream's CLI and that upstream decides its behaviour,
`CONVENTIONS.md` §7), and the notes say which applied. The parser itself is upstream's,
pinned exactly (`CONVENTIONS.md` §1 fact 5); it is not mutated, benched or fuzzed here
beyond what passes through `alliumpy_core::parse`. The pyo3 crate `crates/alliumpy` is
excluded from all three: its only tests are Python's (`CONVENTIONS.md` §1 fact 3), so
cargo-mutants would report every mutant missed, and a Rust bench or fuzz target linking
it would need `libpython` at load time. The decision record is 0016, this ticket's alone
(`CONVENTIONS.md` §8). Wave-2 rules apply (`CONVENTIONS.md` §11): the frozen list has
lifted, every shared file is edited on its own lines, and this ticket merges rebased on
whatever wave-2 ticket merged before it.

P `tickets/CONVENTIONS.md` §11 explains why none of this could land in T00: the fuzz
crate's `--manifest-path fuzz/Cargo.toml` lines in `sync`, `lock`, `fmt-check` and
`clippy` would fail before `fuzz/` exists. This ticket adds those lines, and the same
line to `lock-check`, `lock-upgrade`, `format` and `fix` (step 5).

## Goal

`just mutants` runs cargo-mutants over `alliumpy-core` on a copy of the tree and reports
every mutant caught or unviable; `mutants.yml` runs it weekly and by hand and uploads
`mutants.out/`. `just bench` runs one divan benchmark of the conversion layer by hand and
is never in CI. `just fuzz <target>` runs a fuzz target over `alliumpy_core::parse` on the
pinned stable toolchain with `--sanitizer none` for a bounded time; `fuzz.yml` does the
same weekly and uploads any crash. The fuzz crate sits outside the workspace with its own
committed lockfile, every existing recipe that must see it does, the `rust` CI job keeps
it compiling, decision 0016 says why, and `just check` stays green.

## Non-goals

- No score threshold, no gate, no `--in-diff` on pull requests: the drafts' non-goals.
  `mutants.yml` and `fuzz.yml` are never in `check`'s `needs` (`CONVENTIONS.md` §10).
- No `mutants` crate dependency; an exclusion goes in `.cargo/mutants.toml` as
  `exclude_re`, created only when a mutant needs excluding.
- No nightly toolchain, ever (L's open point 1).
- No benchmark in CI: timings measure the machine.
- No mutant, bench or fuzz target over `crates/alliumpy`, and none over upstream's parser
  except through `parse`.
- No change to `alliumpy-core`'s public API for a bench or fuzz target beyond what one
  needs; if one needs a function, it is `#[doc(hidden)]` with a comment saying why, or it
  lives in the fuzz crate.
- No `check` recipe-list change: `mutants`, `bench`, `fuzz` and `fuzz-build` sit outside
  `check`
  (`CONVENTIONS.md` §4).

## Files touched

| Path | Class | Content |
| --- | --- | --- |
| `pyproject.toml` | shared, own lines | `cargo-mutants`, L's pin re-verified on conda-forge, with the comment L's draft gives |
| `pixi.lock` | shared, regenerated | `pixi lock` |
| `tools.txt` | shared, own lines | `cargo-fuzz`, L's pin re-verified (conda-forge does not carry it) |
| `Cargo.toml` | shared, own lines | `exclude = ["fuzz"]` in `[workspace]`; `divan` under `[workspace.dependencies]` with the decision-0004 note |
| `Cargo.lock` | shared, regenerated | divan's packages |
| `crates/alliumpy-core/Cargo.toml` | shared, own lines | `divan` under `[dev-dependencies]`; the `[[bench]]` table with `harness = false` |
| `crates/alliumpy-core/benches/parse.rs` | new | one divan bench of `parse` over the smoke fixtures, and over `tests/fixtures/parity/` if T13 has merged |
| `fuzz/Cargo.toml` | new | L's draft, the path dependency `../crates/alliumpy-core`, the repeated `forbid` lint table, `publish = false` |
| `fuzz/Cargo.lock` | new | committed |
| `fuzz/.gitignore` | new | what `cargo fuzz init` writes: `target`, `corpus`, `artifacts`, `coverage` |
| `fuzz/fuzz_targets/parse.rs` | new | arbitrary bytes, decoded as UTF-8 when valid, through `alliumpy_core::parse`; asserts no panic and that every `line` and `col` is at least 1 |
| `Justfile` | shared, own lines | `mutants`, `bench`, `fuzz`, `fuzz-build`; the fuzz crate's lines in `sync`, `lock`, `lock-upgrade`, `lock-check`, `fmt-check`, `clippy`, `format`, `fix` (step 5) |
| `.pre-commit-config.yaml` | shared, own lines | the `fmt-check` hook's `files:` widened to `fuzz/` |
| `.github/workflows/mutants.yml` | new | L's draft, `just mutants`, artefact kept 28 days |
| `.github/workflows/fuzz.yml` | new | L's draft: weekly and by hand, a target matrix with `fail-fast: false`, 300 s per target, crashes uploaded on failure |
| `.github/workflows/ci.yml` | shared, own lines | one step, `- run: just fuzz-build`, in the `rust` job after `just clippy` (step 5) |
| `.gitignore` | shared, own lines | the `mutants.out*/` comment names this ticket as done; `fuzz/corpus/`, `fuzz/artifacts/` and `fuzz/coverage/` beside the generated `fuzz/.gitignore` (root `target/` already covers `fuzz/target/`), so the root file is complete on its own |
| `AGENTS.md` | shared, own lines | `just fuzz` and `just fuzz-build` are not network recipes (their lock guard is `--offline`); nothing added to the network list. The Rust block names `just mutants` as the report to read after a change to the core |
| `docs/decisions/0016-mutation-bench-and-fuzz.md` | new | `CONVENTIONS.md` §8's five sections; Decision has three subsections, one per tool, each with what it watches and why it is a report |
| `docs/decisions/0004-dependency-policy.md` | shared, own lines | divan as a development dependency; libfuzzer-sys outside the workspace, locked by its own lockfile |
| `docs/manifest.yml` | shared, own lines | 0016's entry, slug `decision_mutation_bench_fuzz` |
| `docs/README.md` | shared, own lines | 0016 reachable under Decisions |
| `docs/decisions/README.md` | shared, own lines | 0016's row |
| `docs/reference/testing.md` | shared, own lines | "Mutation testing", "Benchmarks", "Fuzzing"; the scope sentence (the core, never upstream's parser) |
| `docs/reference/quality-gates.md` | shared, own lines | the three among the checks outside the gate on purpose; `lock-check`, `fmt-check` and `clippy` rows name the fuzz crate; `fuzz-build` in the `rust` job |
| `docs/reference/commands.md` | shared, own lines | `mutants`, `bench`, `fuzz`, `fuzz-build` rows; `sync`, `lock`, `lock-upgrade`, `lock-check` rows name the fuzz lockfile |
| `docs/reference/configuration.md` | shared, own lines | the `tools.txt` row gains cargo-fuzz; `.cargo/mutants.toml` named as the exclusion file, absent until needed |
| `docs/how-to/develop-locally.md` | shared, own lines | Prerequisites: a C++ compiler for libfuzzer-sys's build script; Rosetta 2 on Apple silicon for `just fuzz` and `just fuzz-build`, which run the x86_64 cargo-fuzz binary, if L's finding about the macOS archive still holds; `just check`'s clippy line over `fuzz/` is plain cargo and needs none |
| `docs/how-to/maintain-dependencies.md` | shared, own lines | `fuzz/Cargo.lock` and the `tools.txt` line move too |
| `docs/explanation/quality-philosophy.md` | shared, own lines | the paragraph L's mutation draft gives: coverage says a line ran, a mutant says whether a test would notice |
| `docs/operations/maintenance.md` | shared, own lines | Weekly: read the `mutants` and `fuzz` runs beside `audit` |
| `docs/project/repository-map.md` | shared, own lines | `fuzz/` and `crates/alliumpy-core/benches/` |
| `CHANGELOG.md` | shared, own lines | one `[Unreleased]` line |
| `tickets/T15-mutants-bench-fuzz.md` | ticket | `status:` and hand-back notes |

## Steps

1. Create the worktree after T11 has merged; rebase on any wave-2 ticket merged since.
   `just initialize` (network, authorised); `just check` on the untouched worktree; quote
   its last line as the baseline. Note whether T13 has merged: if so,
   `crates/alliumpy-core/src/cli/` may exist and `tests/fixtures/parity/` holds a corpus
   the bench runs over (step 4).
2. **Pins, re-verified on the day** (each read below is network, authorised).
   cargo-mutants on conda-forge for `linux-64` and `osx-arm64` with no `rust` dependency
   (`pixi search cargo-mutants --platform <p>`; L's draft found `27.1.0`); cargo-fuzz
   still absent from conda-forge (`pixi search cargo-fuzz --platform <p>` for both
   platforms must find no package; if one appears, the pin moves to `pyproject.toml` and
   the `tools.txt` line is dropped), then its newest release and its assets (`gh api
   repos/rust-fuzz/cargo-fuzz/releases/latest --jq '.tag_name, (.assets[].name)'`; L
   found `0.13.2`, x86_64 only on macOS); libfuzzer-sys and divan on crates.io (`cargo
   search`); divan's maintenance (`gh api repos/nvzqz/divan --jq
   '.archived, .pushed_at'`). If divan is archived, criterion with `default-features =
   false` is the fallback L names; record the choice. Each pin's comment says what it is
   for; cargo-mutants' and divan's say they are never a gate, and cargo-fuzz's says that
   `fuzz-build`, the one line the `rust` job runs, only proves the target compiles.
3. **Mutation testing.** Apply L's mutation draft with these changes: the recipe is two
   lines, a positive control and then the run:

   ```sh
   [ "$(cargo mutants --list --package alliumpy-core --all-features | grep -c .)" -gt 0 ] || { printf '%s\n' 'mutants: no mutants found; the --package filter is wrong' >&2; exit 1; }
   cargo mutants --package alliumpy-core --all-features --gitignore=true --cargo-arg=--locked "$@"
   ```

   `mutants.yml` inherits the control through the recipe, and the recipe's comment says
   why the package is named (the pyo3 crate's tests are Python's, so every mutant there
   would be missed, and its test binary needs `libpython`). After the `pyproject.toml`
   line: `pixi lock`, then `just sync` (network, authorised). `just mutants`; quote the
   summary line. Every mutant must be caught or unviable; a missed one is a missing test,
   added in this ticket in the core. If the control fires, or cargo-mutants reports no
   mutants found, that is a failure of this step, not a pass (`CONVENTIONS.md` §11,
   "Checks fail closed"): the core has functions, so the filter is wrong. `mutants.yml` as
   L's draft, action SHAs re-read against `ci.yml`.
4. **The bench.** Apply L's benchmark draft with `alliumpy-core` for `pawdoku` and
   `parse.rs` for `solver.rs`: `divan` as a `[workspace.dependencies]` entry and a
   dev-dependency, the `[[bench]]` table, `benches/parse.rs` benchmarking
   `alliumpy_core::parse` over `tests/fixtures/smoke/ok.allium` and `broken.allium`
   through `divan::black_box`, and, when step 1 found T13 merged, over each file of
   `tests/fixtures/parity/`. Cargo runs a bench binary from the package directory, so no
   path is bare: the two smoke files by `include_str!` relative to the source file
   (`../../../tests/fixtures/smoke/ok.allium`); the parity directory read at run time with
   `std::fs::read_dir` on
   `Path::new(env!("CARGO_MANIFEST_DIR")).join("../../tests/fixtures/parity")`, panicking
   on a missing or empty directory rather than skipping it, and the notes quote how many
   files it benched. The `bench` recipe as L's draft (`--bench '*'`, the comment about
   unit tests in bench mode). After the manifest edits: `just lock`, then `just sync`
   (network, authorised). `just bench`; quote the table. Confirm `just deps-unused` still
   passes with divan present (cargo-shear sees the bench target's use; L proved it on
   1.98.1, quote it here on the pin) and that `just deny` is unchanged (dev-only, outside
   `exclude-dev`'s graph).
5. **The fuzz crate.** Apply L's fuzzing draft: the `tools.txt` line, then
   `just install-tools` (network, authorised); `cargo fuzz init --target parse` at the
   root (L's form; it writes files only, and the generated `[[bin]]` reads
   `name = "parse"`, `path = "fuzz_targets/parse.rs"`). Before resolving dependencies,
   change the path dependency to `../crates/alliumpy-core`, add
   `exclude = ["fuzz"]` in the root `[workspace]`, set `libfuzzer-sys` as a full caret
   range with the decision-0004 note, and add the repeated `forbid` lint table and
   `publish = false`. Only after those manifest edits, run
   `cargo generate-lockfile --manifest-path fuzz/Cargo.toml` and `just sync` (network,
   authorised); commit `fuzz/Cargo.lock`. The target
   `fuzz_targets/parse.rs`: `std::str::from_utf8(data)` and, when it is valid,
   `alliumpy_core::parse(s)`; assert every diagnostic's `line >= 1` and `col >= 1`
   (one-based by `CONVENTIONS.md` §9) and that none of the span conversions panics. The
   recipe lines in `sync`, `lock`, `lock-upgrade`, `lock-check`, `fmt-check`, `clippy`,
   `format` and `fix` that name `--manifest-path fuzz/Cargo.toml`: `sync`, `lock`,
   `lock-check`, `fmt-check` and `clippy` as L's draft prints them; `lock-upgrade` gains
   `cargo update --manifest-path fuzz/Cargo.toml` after `cargo update`; `format` gains
   `cargo fmt --manifest-path fuzz/Cargo.toml` after `cargo fmt --all`; `fix` gains
   `cargo clippy --manifest-path fuzz/Cargo.toml --all-targets --locked --fix
   --allow-dirty --allow-staged` after its clippy line (P `Justfile` lines 71-73, 134-136
   and 140-144 are the recipes). The `fuzz target seconds="300"` recipe as L's draft,
   with `--sanitizer none` and the host triple from `rustc -vV`, except that its first
   line is the offline guard
   `cargo update --workspace --locked --offline --manifest-path fuzz/Cargo.toml` (the
   `lock-check` form, which L proved on the fuzz manifest) in place of L's
   `cargo fetch --locked`: `cargo fetch` is a network command (`CONVENTIONS.md` §11) and
   `fuzz` is not in `AGENTS.md`'s network list; the recipe comment says so, and the
   hand-back notes record the departure. One more recipe, outside `check`, with a comment:

   ```just
   # The fuzz crate compiles on the pinned stable, without running it. The weekly
   # job would otherwise be the only thing that notices a fuzz target that no
   # longer builds, and weekly jobs rot. Not in check's recipe list: clippy
   # already lints the crate every run; this is the one line ci.yml runs so a
   # broken target names itself in the step list. cargo-fuzz takes no --locked
   # and would rewrite a stale fuzz/Cargo.lock, so the offline lock guard runs first.
   fuzz-build:
       cargo update --workspace --locked --offline --manifest-path fuzz/Cargo.toml
       cargo fuzz build --sanitizer none --target "$(rustc -vV | sed -n 's/^host: //p')"
   ```

   `just fuzz parse 60`; quote the libFuzzer summary. Then L's offline proof with the real
   target: a planted `unsafe {}` in the target fails `just clippy`; remove it. Then the
   run's positive control: plant an unconditional `panic!()` on the line after the
   `alliumpy_core::parse(s)` call, inside the valid-UTF-8 branch, so that it fires only
   once an input has gone through `parse` (a panic at the top of the body would fire even
   if `parse` were never called); run `just fuzz parse 5`, and require a non-zero exit
   status and a file under `fuzz/artifacts/parse/`; quote both, remove the plant and the
   artefact, and confirm `git status --short` prints nothing. A target the fuzzer cannot
   be made to crash proves nothing about the real one. Record the outcome of L's
   `--sanitizer none` finding on this pin (P `tickets/CONVENTIONS.md` §12 claim 8, which
   this repository's §12 does not carry), and whether cargo-fuzz's release now carries an
   `aarch64-apple-darwin` archive, which decides the Rosetta row.
6. **`fuzz.yml` and `ci.yml`.** `fuzz.yml` as L's draft, matrix over `[parse]`,
   `fail-fast: false`, `just fuzz ${{ matrix.target }} 300` through an `env:` indirection
   rather than `${{ }}` inside the shell line (P `.github/workflows/ci.yml`'s rule),
   artefact `fuzz/artifacts/<target>` under `if: failure()`. In `ci.yml`, the `rust` job
   gains `- run: just fuzz-build` after `- run: just clippy`; nothing joins `check`'s
   `needs`. `just lint` (actionlint over both workflows).
7. **Decision 0016 and the pages.** Write the record (`CONVENTIONS.md` §8): Context (a
   thin core whose only consumer is the wheel), Decision (three reports, none a gate; the
   scope is the core and never upstream's parser), Consequences (a C++ compiler and a
   second lockfile; minutes on a private repository, `CONVENTIONS.md` §13), What would
   reopen this (a mutation score worth gating on; a crash the weekly job finds in
   upstream's parser, which is reported upstream, not fixed here), Related pages
   (`docs/reference/testing.md`, `docs/reference/quality-gates.md`,
   `docs/reference/commands.md`, `docs/how-to/develop-locally.md`,
   `docs/explanation/quality-philosophy.md`, decision 0004). Then every page row of Files
   touched. `just check-docs`.
8. `just check`, the final adversarial review, `just check` again if fixes landed, then
   commit. **Authorisation required: push and open a pull request.** After the merge, a
   `workflow_dispatch` of `mutants.yml` and one of `fuzz.yml` (each separately
   authorised); download and read the `mutants` artefact; for `fuzz.yml` read the job log,
   since its artefact exists only when a crash was found (step 6).

   **Adversarial review** (`CONVENTIONS.md` §14): the lane's diff, the mutant summary and
   the fuzz run, before the push. Ask: whether `just mutants` can print a green summary
   with zero mutants tested, and whether the recipe or the notes fail closed on it;
   whether the fuzz target compiles on the pin without nightly, shown by
   `rustup toolchain list` listing no nightly and by recipes that name no `+toolchain`;
   whether any recipe added here reaches the network inside `check` (the fuzz crate's
   `cargo fetch --locked` runs in `sync`; `fuzz` and `fuzz-build` guard the lock with
   `--offline`, and neither is a gate); whether `check-clean` would see `fuzz/corpus/`,
   `fuzz/artifacts/`, `fuzz/target/` or `mutants.out/` after a run; which missed mutant
   was explained away rather than tested;
   whether the pyo3 crate is excluded from all three tools and the exclusion is stated.

## Acceptance criteria

- `just mutants` output is quoted, with a non-zero `--list` count quoted, no missed and
  no timed-out mutant, and exit status 0 (L S03 (d): 2 means missed, 3 a timeout, 4 a
  failing baseline). The `src/cli/` exclusion, if any, is quoted with S01's ruling.
- `just bench` and `just fuzz parse 60` outputs are quoted; `just fuzz-build` exits 0.
- The fuzz manifest and root workspace are corrected before the first fuzz lockfile
  generation and `just sync`; `fuzz/Cargo.lock` is committed.
- The planted `panic!()` run is quoted: a non-zero exit status and a file under
  `fuzz/artifacts/parse/`, both since removed.
- `just fuzz` ran on the pinned stable: `rustup toolchain list` lists no nightly,
  `RUSTUP_TOOLCHAIN` is unset in the shell that ran it, and the `fuzz` and `fuzz-build`
  recipes name no `+toolchain`, each quoted (`rustup show active-toolchain` from `fuzz/`
  only reads the root `rust-toolchain.toml`, so it says nothing about the run).
- `mutants.yml` and `fuzz.yml` are not in `check`'s `needs`; `ci.yml`'s `rust` job runs
  `just fuzz-build`; `check` is still the only required check.
- After `just mutants`, `just bench` and `just fuzz`, `git status --short` prints nothing.
- `just deps-unused`, `just deny`, `just features` and `just coverage` are green with
  divan present and the fuzz crate excluded (coverage still measures the core alone).
- `just check` is green.
- The adversarial reviews in Steps ran (`CONVENTIONS.md` §14), and every valid finding is
  fixed or handed back.

## Verification

```sh
cargo mutants --list --package alliumpy-core --all-features | grep -c .
just mutants; echo "exit $?"   # must be 0
just bench
just fuzz parse 60; echo "exit $?"
just fuzz-build; echo "exit $?"
rustup toolchain list; printf 'RUSTUP_TOOLCHAIN=%s\n' "${RUSTUP_TOOLCHAIN-unset}"   # no nightly; unset
just --show fuzz; just --show fuzz-build   # neither body names a +toolchain
git status --short
just deps-unused && just deny && just features && just coverage
rg -n 'needs:' .github/workflows/ci.yml
gh api repos/BiscuitBin/alliumpy/branches/main/protection/required_status_checks --jq '[.checks[] | {context, app_id}]'
just check
```

The `gh api` line is read only if T01 applied protection (`CONVENTIONS.md` §1 fact 6); if
protection was deferred, say so and quote the `rg` line instead.

## Hand-back notes

To be written by the executing agent: the pins and the day, divan's maintenance status
and the choice made; the mutant summary and any test added for a missed mutant; the bench
table; the fuzz run and the `--sanitizer none` outcome on the pin; whether the Rosetta
row stayed; whether T13 had merged and the bench covered the parity corpus (how many
files); the two dispatch run URLs; the review record for each checkpoint
(`CONVENTIONS.md` §14); where this ticket departed from L's drafts and P's tickets. This
ticket owns no `CONVENTIONS.md` §12 claim, so T17 carries nothing from these notes; the
`--sanitizer none` outcome answers P's §12 claim 8 and is stated plainly here and in
decision 0016. If it failed on the pin, that is a design change handed back as a `main`
pull request on `CONVENTIONS.md` (§12's preamble), never fixed by installing nightly or
edited from this lane.

## Open points

- If the fuzz crate's `clippy` and `fuzz-build` lines make `just check` or the `rust` job
  slower than the maintainer accepts, both can move to `fuzz.yml`; say so with the timing.
- If S01 chose vendoring and the vendored CLI reads files, a second fuzz target over its
  argument parsing belongs here once T13 has merged; if T13 merges after this ticket,
  that target is T13's or a follow-up's, stated in the notes.
