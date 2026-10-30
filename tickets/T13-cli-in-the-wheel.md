---
id: T13
title: "The `allium` command in the wheel: S01's decision built, with parity proved"
status: done
depends_on: [S01, T11]
parallel_with: [T15]
branch: ticket/t13-cli-in-the-wheel
estimated_size: L
---

# T13: The `allium` command in the wheel: S01's decision built, with parity proved

## Context

T00 left `allium --version` working and every other invocation answered with one stderr
line and exit 2 (`CONVENTIONS.md` §9 "The T00 API"). S01 chose the route by which the
rest of the command gets into the wheel, proved it on a prototype with a parity harness,
and drafted the route-specific steps and decision record 0014 in its hand-back notes.
This ticket builds that decision on `main`: the recipes, the corpus, the harness, the
command, the record and the pages, and proves parity with the crates.io build of
`allium-cli` at the pinned version over the whole corpus, byte for byte on stdout and
exactly on exit codes (`CONVENTIONS.md` §7 invariant 1).

This is a wave-2 ticket: it edits only its own lines in the shared files and merges
rebased on whichever wave-2 ticket merged last (`CONVENTIONS.md` §11). It also edits
existing gates: `allium check` joins `wheel-smoke` (`CONVENTIONS.md` §11, "Wave 2 shares
files by rebasing") and `version-check` compares the whole `--version` string
(`CONVENTIONS.md` §9).

Parity is POSIX-only (`CONVENTIONS.md` §1 fact 9). The Windows half of whatever shim
`_cli.py` becomes is written here and proved once, by T14's rehearsal smoke
(`CONVENTIONS.md` §12 claim 18).

Read first: `CONVENTIONS.md` §1 (decisions 3 and 4; facts 5 and 9), §4, §9 ("The parity
reference", "The sdist", "`wheel-smoke`, `version-check` and the fixtures"), §10, §11,
§12 claims 12 and 18, §13 ("CLI drift"), §14; `tickets/S01-cli-strategy-spike.md`'s
hand-back notes in full, which hold the harness design and its full text, the chosen
route, its drafted steps and the drafted record; T11's hand-back notes for what wave 1
handed back about `_cli.py` or `version_check.py`.

## Goal

`allium check`, `analyse`, `parse`, `plan`, `model`, `help`, `-h`, `--help`, `-V` and
`--version` work from the installed wheel on Linux and macOS with the same stdout bytes
and exit codes as the reference `allium` built from crates.io at `ALLIUM_VERSION`, over
S01's corpus and argument matrix, as `just parity` proves and a `parity` CI job repeats;
`wheel-smoke` runs `allium check` on the smoke fixture; `version-check` compares the
whole `--version` string; decision 0014 is landed; the pages say what exists.

## Non-goals

- Choosing a route. S01 chose; the route-specific steps below are copied from S01's
  notes, and an agent that finds the route unworkable stops and hands back rather than
  switching.
- Windows parity. Designed in the shim, proved by T14.
- The sdist's fate in the release: T14 applies S01's ruling. This ticket only makes sure
  the route's files are in the source tree maturin would pack.
- The version bump, `release-pypi.yml`, or anything PyPI: T14.
- Renovate's treatment of the pin and the upstream-bump runbook: T17. This ticket's
  hand-back notes record what a bump costs under the chosen route, for T17 to write up.
- Changing the corpus to hide a difference. A real difference is either a defect fixed
  here or a decision recorded in 0014 and named in the harness as an expected exception,
  with the maintainer's agreement.

## Files touched

| Path | Class | Content |
| --- | --- | --- |
| `tests/fixtures/parity/` | new | U's `.allium` files at `v3.6.1`, upstream's directory shape, plus `README.md` naming origin, tag and licence; any pair this repository adds for cross-module coverage, attributed to this repository |
| `tests/parity/run.py` | new | S01's harness, copied verbatim from the "The harness, verbatim" section of its hand-back notes |
| `tests/parity/README.md` | new | how to run it, what it compares, what it never compares |
| `crates/alliumpy/python/alliumpy/_cli.py` | final | the route's shim, POSIX and Windows branches |
| `crates/alliumpy/python/alliumpy/_alliumpy.pyi`, `__init__.py` | shared, own lines | whatever the route exposes (for example `_run_cli`) |
| `crates/alliumpy/LICENSE-allium-tools` | shared, own lines | the header paragraph's route sentence: which upstream version's code and fixtures the wheel carries and under which route (`CONVENTIONS.md` §9 "Licences"; T00 wrote it as pending S01) |
| `crates/alliumpy/tests/test_cli.py` | new | exit codes 0, 1 and 2 by fixture, `-V`, broken pipe, flush order, an argument that is not UTF-8, a closed stdout, SIGINT |
| `crates/alliumpy/tests/test_run_cli.py` | new | the `_run_cli` binding's own pytest case (S01 route step 5) |
| `crates/alliumpy-core/**`, `crates/alliumpy/src/lib.rs`, `Cargo.toml` | shared, own lines | the route's Rust, if any (route-specific steps; under route (a), the new `crates/alliumpy-core/src/cli.rs` and the three vendored files under `crates/alliumpy-core/src/cli/` of S01 route steps 2 and 3) |
| `rustqual.toml` | shared, own lines | `exclude_files` for the three vendored files (S01 route step 4; decision 0014) |
| `.editorconfig` | shared, own lines | `indent_size = unset` for the three vendored files (S01 route step 4; decision 0014) |
| `Cargo.lock` | shared, regenerated | by cargo, after the rebase, if the route adds a dependency (`CONVENTIONS.md` §11) |
| `crates/alliumpy/pyproject.toml` | shared, own lines | a `[tool.maturin]` key, only if the route's drafted steps need one (`CONVENTIONS.md` §2); `[project]` untouched |
| `Justfile` | shared, own lines | `install-parity-reference`, `parity`; `allium check` in `wheel-smoke`; the `coverage` scope line only if S01's gate ruling says so |
| `scripts/version_check.py` | shared, own lines | the full `--version` string |
| `mypy.ini` | shared, own lines | `tests/parity` appended to `files` |
| `AGENTS.md`, `.agents/skills/python-change/SKILL.md` | shared, own lines | drop the "from T13" qualifiers T05 left (`install-parity-reference` in the network-recipe list, `just parity` in invariant 1 and in the skill); add no entry |
| `.github/workflows/ci.yml` | shared, own lines | the `parity` job; `check`'s `needs`; one `allium check` line in `wheel-smoke-py311` |
| `docs/decisions/0014-cli-strategy.md` | stub -> final | S01's draft |
| `docs/decisions/README.md` | shared, own lines | 0014's row |
| `docs/decisions/0007-metrics-gate.md` | shared, own lines | one line pointing to 0014's `exclude_files` |
| `docs/explanation/architecture.md`, `docs/how-to/install-and-run.md`, `docs/reference/commands.md`, `docs/reference/testing.md`, `docs/reference/quality-gates.md` | shared, own lines | the command, the two recipes, the parity test |
| `docs/explanation/quality-philosophy.md`, `docs/explanation/security-model.md` | shared, own lines | parity and the reference in the present tense (T07 named them as arriving with T13) |
| `CHANGELOG.md` | shared, own lines | one `[Unreleased]` line |
| `tickets/T13-cli-in-the-wheel.md` | ticket | `status:` and hand-back notes |

## Steps

1. Create the worktree after S01 and T11 have merged, rebased on the last merged wave-2
   ticket (`CONVENTIONS.md` §11); `just initialize` (network, authorised); `just check`
   on the untouched worktree, last line quoted as the baseline.

2. **The reference recipe.** Add to the `Justfile`, in a new `# ---- parity ---` section
   before `# ---- aggregate ---`:

   ```just
   # The reference allium: upstream's own CLI, built from crates.io at the version
   # the core wraps, into a root that is never on PATH, so that nothing can shadow
   # the wheel's allium or be shadowed by it (CONVENTIONS.md §9). Network; outside
   # `check`. The version is read from Cargo.toml so the pin cannot drift from it.
   install-parity-reference:
       #!/bin/sh
       set -eu
       pin=$(python -I scripts/version_check.py --print-pin)
       cargo install "allium-cli@${pin}" --locked --root .tools/parity
       .tools/parity/bin/allium --version

   # Byte-for-byte stdout and exit-code parity between the wheel's allium (the venv
   # wheel-smoke, which this recipe depends on, has just rebuilt from this worktree,
   # so the candidate is never stale) and the reference, over tests/fixtures/parity/
   # and the argument matrix tests/parity/README.md lists. POSIX-only; outside
   # `check` because the reference needs the network to build. Fails closed on an
   # empty corpus and runs its own positive and negative controls first, then the
   # behaviours beyond the corpus (`test_cli.py`) against the same candidate.
   parity: wheel-smoke
       test -x .tools/parity/bin/allium || { printf '%s\n' 'parity: no reference; run just install-parity-reference' >&2; exit 2; }
       python -I tests/parity/run.py --reference "$PWD/.tools/parity/bin/allium" --candidate "$PWD/target/wheel-smoke/venv/bin/allium" --corpus tests/fixtures/parity
       ALLIUMPY_SMOKE_BIN="$PWD/target/wheel-smoke/venv/bin/allium" python -m pytest crates/alliumpy/tests/test_cli.py -rs
   ```

   `scripts/version_check.py` gains `--print-pin`: it prints the `allium-parser` pin it
   already reads, with its `=` stripped (`3.6.1`), and exits 0 before anything but
   `Cargo.toml` is read, so that a missing smoke venv is not a failure on this path (the
   CI job runs it before `wheel-smoke`); it fails only if `Cargo.toml` cannot be read or
   holds no pin. In `AGENTS.md`, drop the "from T13" qualifiers T05 left on
   `install-parity-reference` in the network-recipe list and on `just parity` in
   invariant 1, and in `.agents/skills/python-change/SKILL.md` the one on `just parity`;
   the entries already exist, so add none. Run `install-parity-reference` (network,
   authorised; `CONVENTIONS.md` §12 claim 12's build) and quote the version line.

3. **The corpus and the harness.** Copy S01's corpus list from U at `v3.6.1` into
   `tests/fixtures/parity/`, with the same `gh api` reads S01 used (network,
   authorised), preserving directory shape, plus the `README.md`. List `.path` and
   `.sha` from the `v3.6.1` tree (S01 step 2's `--jq`, emitting `"\(.path) \(.sha)"`);
   after the copy, `git hash-object <file>` must equal the listed sha for every file and
   `find tests/fixtures/parity -name '*.allium' -empty` must print nothing; quote the
   count and the hash check. A `gh api … | base64 -d > file` pipeline exits 0 and writes
   an empty file when the read fails, so the count alone proves nothing. Copy S01's
   harness, verbatim from the "The harness, verbatim" section of its hand-back notes,
   into `tests/parity/run.py`, and write `tests/parity/README.md`, carrying S01's
   argument-matrix table and its row count. `ruff check .` already covers the harness;
   `mypy.ini`'s `files` list (T03) does not name `tests/parity`, so append
   `tests/parity` to it as `shared, own lines`, with a comment naming this ticket, and
   show `mypy -v 2>&1 | grep tests/parity/run.py` printing the file. `_typos.toml` and
   both prek configs' `exclude:` already leave the corpus alone (T00, `CONVENTIONS.md`
   §5). If `ruff` or `mypy` then fails on the harness, fix the harness, never the
   configuration.
   Run `just parity` (which runs `wheel-smoke` first) **before** the command exists.
   With T00's `_cli.py` a comparison can match in only two ways: `-V` and `--version`,
   which T00's shim already answers with `ALLIUM_VERSION_STRING` and exit 0
   (`CONVENTIONS.md` §9); and any matrix row whose reference stdout is empty and whose
   reference exit status is 2, because the shim prints nothing to stdout and exits 2 for
   everything else (at least the no-argument invocation and the empty directory, and
   whichever others the reference's own output shows). Every per-file corpus comparison
   and both directory forms over the corpus must differ. The agent quotes the actual
   summary, lists every matching row by name with the way it matches, and checks each
   against the reference's own stdout and exit status; a match that fits neither way is
   a harness defect. This is the harness's own positive control at full scale.

4. **Route-specific steps.** Copy here, verbatim, the numbered steps S01's hand-back
   notes drafted for the chosen route, under the heading `### Route-specific steps (from
   S01, route <letter>)`, then execute them. They end with `_cli.py` final, the
   `__init__.py` and `.pyi` lines the route needs, the Rust the route needs (vendored
   modules with attribution, `serde` and `serde_json` with the decision-0004 notes, and
   the Rust unit tests or `coverage` scope line, the `#[expect]` attributes and the
   `rustqual.toml` and `.editorconfig` sections S01's gate ruling names, and the
   binding's `test_run_cli.py`, under (a); the binary as package data and its executable
   bit under (b); the dependency bump under (c)), and `just check` green. If a step
   cannot be executed as drafted, stop and hand back: the fix is a pull request to
   `main` amending S01's drafted steps in `tickets/S01-cli-strategy-spike.md`, never
   another route chosen here. A red `clippy`, `metrics` or `coverage` gate on the
   vendored code that the ruling did not foresee is such a step.

5. **The behaviours beyond the corpus.** `crates/alliumpy/tests/test_cli.py`, through
   `subprocess` against the smoke venv's `allium` (the test takes the path from an
   environment variable `ALLIUMPY_SMOKE_BIN` that only the `parity` recipe sets, to
   `"$PWD/target/wheel-smoke/venv/bin/allium"` on its last line, and is skipped with
   the stated reason `ALLIUMPY_SMOKE_BIN unset; run just parity` when it is unset, so
   that `py-test` in `check`, which runs before `wheel-smoke` and never sets it, is not
   the place it runs; `parity`'s last line runs `python -m pytest
   crates/alliumpy/tests/test_cli.py -rs` with the variable set): exit 0 on
   `tests/fixtures/smoke/ok.allium`,
   1 on `broken.allium`, 2 with no arguments and on an empty directory; `-V` and
   `--version` print `ALLIUM_VERSION_STRING` and exit 0; `allium check <corpus dir> |
   head -c 1` ends with the exit status and stderr S01 recorded for the reference, and
   never a Python traceback; writing to `/dev/full` ends as the reference does on Linux
   (the test carries `@pytest.mark.skipif(sys.platform != "linux", reason=...)` because
   `/dev/full` does not exist on macOS, and runs in the `parity` CI job); an argument
   that is not UTF-8, stdout closed (`>&-`) and SIGINT during a blocked read each end as
   S01 recorded for the reference, never with a Python traceback (the SIGINT case runs
   `check` on a FIFO made with `os.mkfifo` under `tmp_path` and sends the signal 2 s
   after the child starts, as S01 did, because `_cli.py` restores `SIG_DFL` only once
   `main()` runs and an earlier signal meets Python's handler and its traceback; the
   child must end within 6 s of the signal with `returncode == -signal.SIGINT` and empty
   stderr, and the test opens the FIFO for writing in a `finally` so that a child that
   survives is released); when both
   streams are written, their order on a pseudo-terminal matches the reference's (S01's
   finding). Each expectation cites the S01 note it comes from. The module imports
   nothing from `alliumpy`: the `parity` recipe and its CI job never run `py-develop`, so
   the pixi interpreter has no extension (or a stale debug one); every Python-side value
   comes from the smoke venv's interpreter, `Path(os.environ["ALLIUMPY_SMOKE_BIN"]).parent
   / "python"`, run with `-I -c` through `subprocess` and its stdout parsed as JSON
   (`ALLIUM_VERSION_STRING` is read as `from alliumpy._alliumpy import
   ALLIUM_VERSION_STRING` there). One more case, parametrised over every `.allium` file
   under `tests/fixtures/parity/` and over `tests/fixtures/smoke/broken.allium` (whose
   `parse` is non-empty by `CONVENTIONS.md` §9, so the case cannot pass on empty lists
   alone): `alliumpy.parse(text)` run in that interpreter (the text read as
   `path.read_bytes().decode("utf-8")`, never `read_text`, so that no newline translation
   moves the byte offsets), as `(line, col, severity, message, code)` tuples, equals the
   leading `len(parse(text))` entries of the `diagnostics` list in the JSON that
   `ALLIUMPY_SMOKE_BIN check <file>` prints for that file, taking `location.line` and
   `location.col`, and `len(parse(text))` equals the length of the `diagnostics` list that
   `ALLIUMPY_SMOKE_BIN parse <file>` prints (the parser's diagnostics alone, the same
   count T03 step 2 uses), so that a conversion which drops diagnostics cannot pass on the
   leading entries alone; a mismatch is a parity failure. A final case asserts that the
   total number of parse diagnostics over all parametrised files is at least one and
   prints it for the hand-back notes, which quote it. Upstream's `cmd_check` prints the
   parser's diagnostics before the analyser's (U `crates/allium/src/main.rs` at `v3.6.1`),
   and `just parity` has just proved the candidate's `check` output equal to the
   reference's byte for byte, so this is the Python API's line and column against
   upstream's own conversion (`CONVENTIONS.md` §7 invariant 1, second sentence), which no
   other gate compares: T00's unit test and T03's fixtures hold recorded values, and the
   harness compares binaries.

6. **`wheel-smoke` and `version-check`.** Append to `wheel-smoke`, as its last line,
   `target/wheel-smoke/venv/bin/allium check tests/fixtures/smoke/ok.allium` (exit 0 is
   the assertion; the recipe's `set -eu` carries it). Tighten
   `scripts/version_check.py`'s last clause: the whole of `allium --version`'s output
   must equal `ALLIUM_VERSION_STRING` as written in `crates/alliumpy-core/src/lib.rs`,
   and, when `.tools/parity/bin/allium` exists and the second word of its `--version`
   equals the pin, the reference's output too; a missing or stale reference is a note
   naming `just install-parity-reference`, not a failure, because `check` is offline and
   a stale reference is not drift. If S01 found the suffix derivable (`CONVENTIONS.md`
   §12 claim 12), the literal becomes the derivation and `version_check.py` drops its
   regex over `lib.rs`: it reads the derived string as `target/wheel-smoke/venv/bin/python
   -I -c "from alliumpy._alliumpy import ALLIUM_VERSION_STRING;
   print(ALLIUM_VERSION_STRING)"` (the wheel under test, never the pixi environment's
   build), asserts it starts with `allium` and a space plus the pin, equals the whole of
   `allium --version`'s output, and equals the reference's output when the reference
   exists.

7. **The first green parity run.** `just wheel-smoke`, `just parity`: `0 differ` over the
   whole corpus, both controls fired, quoted and headed by the commit. Any difference is
   fixed in the shim or the route's code; a difference that is upstream's platform
   behaviour (case-insensitive filesystem resolution, 3.6.1's changelog) is reproduced,
   not excluded.

   **Adversarial review** (`CONVENTIONS.md` §14): the harness as landed, the corpus and
   the first green run. Ask: how `0 differ` could print while the candidate is wrong;
   whether the candidate path is the wheel's `allium` and not the reference or a
   worktree script; whether `cwd` and the relative corpus paths make `spec_file` print
   identically for both for the wrong reason; which argument shape or subcommand the
   matrix misses; whether every match in the step 3 run before the command existed was
   `-V`, `--version` or a row whose reference stdout is empty and exit status 2, each
   checked against the reference's own output, and everything else, every corpus and
   directory-form comparison included, differed; whether the
   Python-API case of step 5 would fail on a core whose `line` or `col` is off by one.

8. **CI.** In `ci.yml`, a `parity` job with `needs: [python]` (so that `python`'s
   post-job save of the setup action's `.tools` cache always precedes this job, and
   `.tools/parity` never enters that tools-keyed cache): the setup action,
   `actions/cache` on `.tools/parity` keyed on the pin (`hashFiles('Cargo.toml')` and the
   runner OS), `just install-parity-reference` (network is allowed in CI), `just parity`
   (which runs `wheel-smoke` first), `just version-check` (the one job where the
   reference exists, so step 6's reference clause fires in CI; quote that step's log in
   the hand-back notes), then `just check-clean` (`CONVENTIONS.md` §10, every gate job).
   Add `parity` to `check`'s `needs` (`CONVENTIONS.md` §10). In the `wheel-smoke-py311`
   job, after `venv/bin/allium --version`, add the own line `venv/bin/allium check
   tests/fixtures/smoke/ok.allium`, so the 3.11 mirror runs what `wheel-smoke` now runs.
   Re-read the SHA of any action this job adds, as T01 did.

9. **The record and the pages.** `docs/decisions/0014-cli-strategy.md` from S01's draft
   (replacing T00's stub; frontmatter equal to the manifest entry); 0014's row in
   `docs/decisions/README.md`; in `docs/decisions/0007-metrics-gate.md`, one line
   pointing to 0014's `exclude_files`; the pages in Files touched, own lines; the
   `CHANGELOG.md` line. `just check-docs`.

10. `just check`, then the final adversarial review, `just check` again if fixes landed,
    then commit.

    **Adversarial review** (`CONVENTIONS.md` §14): the lane's diff. Ask: which
    route-specific step was executed differently from S01's draft, and whether the
    hand-back notes say so; whether `version-check` can pass while the wheel's `allium`
    prints a different suffix from the reference; whether `test_cli.py` can be skipped in
    `parity` by an unset variable; whether the `parity` CI job's cache can serve a
    reference built at an older pin; whether any shared file was edited beyond this
    ticket's own lines.

11. **Authorisation required: push and open a pull request.** Stop and ask. The `parity`
    job's first run is on this pull request; quote its summary line and the run URL.

### Route-specific steps (from S01, route (a))

Step 4's copy, verbatim from `tickets/S01-cli-strategy-spike.md` lines 1742-2400.

1. **Dependencies** (`Cargo.toml`, `crates/alliumpy-core/Cargo.toml`, `Cargo.lock`). In
   `[workspace.dependencies]`, after `pyo3`:

   ```toml
   # Caret range; Cargo.lock is the pin (decision 0004). The vendored CLI's
   # test_plan and domain_model derive Serialize (decision 0014).
   serde = { version = "1.0.229", features = ["derive"] }
   # Caret range; Cargo.lock is the pin (decision 0004). The vendored CLI writes
   # its JSON output with it (decision 0014).
   serde_json = "1.0.154"
   ```

   (the versions `Cargo.lock` already holds through `allium-parser`; if they have moved
   by the day, write the locked ones), and under the core's `[dependencies]`:
   `serde = { workspace = true }` and `serde_json = { workspace = true }`. Run
   `cargo update -p serde -p serde_json --offline`. Proof: `git diff Cargo.lock` adds
   exactly `"serde",` and `"serde_json",` to `alliumpy-core`'s dependency list and moves
   no version; `just deny` exit 0.

2. **Vendor** (`crates/alliumpy-core/src/cli/main.rs`, `test_plan.rs`,
   `domain_model.rs`). Fetch the three files at the pin's tag into an empty
   `ai_tmp/upstream/` with S01 step 2's `gh api` lines (network, authorised; under
   `set -o pipefail`, each exit status quoted, `test -s` on each), and check each
   against the tag's tree with `git hash-object`. Save the script below as
   `ai_tmp/vendor_cli.py` and run, from the worktree root,
   `mkdir -p crates/alliumpy-core/src/cli && .pixi/envs/default/bin/python -I ai_tmp/vendor_cli.py v3.6.1 ai_tmp/upstream crates/alliumpy-core/src/cli`
   (the pixi interpreter by path: this runs from the agent's shell, where nothing puts
   `python` on `PATH`).
   Proof: exit 0; `diff ai_tmp/upstream/<file> crates/alliumpy-core/src/cli/<file>`
   counts +79 −65 for `main.rs`, +28 −7 for `test_plan.rs` and +18 −0 for
   `domain_model.rs`, as S01 measured. If the script stops on a count, upstream changed
   a line the transform rewrites: stop and hand back.

   ```python
   # Copyright 2026 Steven Cutting
   """Vendor upstream's allium CLI modules into crates/alliumpy-core/src/cli/ (decision 0014).

   Usage: python -I vendor_cli.py <tag> <dir holding upstream's three files> <dest cli dir>

   Every substitution asserts how many times it matched, so an upstream change to a line
   the transform rewrites stops the script instead of producing a silent partial copy.
   """

   import re
   import sys
   from pathlib import Path

   HEADER = """\
   // Vendored from juxt/allium-tools at {tag}: crates/allium/src/{name}
   // (https://github.com/juxt/allium-tools/blob/{tag}/crates/allium/src/{name}).
   // MIT License, Copyright (c) 2026, as upstream's LICENSE reads at that tag; the full
   // text ships as crates/alliumpy/LICENSE-allium-tools. Changes from upstream are listed in
   // crates/alliumpy-core/src/cli.rs; nothing else differs.
   """
   SAME = "upstream's code, vendored unchanged (decision 0014)"
   HASH = (
       "upstream's hash iteration, vendored unchanged; its output order is proved only as far"
       " as the parity corpus exercises it (decision 0014)"
   )
   PANIC = (
       "upstream panics here, vendored unchanged; cli::run returns 101 for it, as upstream's"
       " binary exits (decision 0014)"
   )
   PUB = "upstream's pub items, vendored unchanged inside a private module (decision 0014)"
   # Per file: (lint, reason, cfg) in order; cfg is "", "test" or "not(test)".
   LINTS = {
       "main.rs": [
           ("clippy::bool_to_int_with_if", SAME, ""),
           ("clippy::cognitive_complexity", SAME, ""),
           ("clippy::disallowed_types", HASH, ""),
           ("clippy::excessive_nesting", SAME, ""),
           ("clippy::iter_over_hash_type", HASH, ""),
           ("clippy::manual_let_else", SAME, ""),
           ("clippy::redundant_closure_for_method_calls", SAME, ""),
           ("clippy::str_to_string", SAME, ""),
           ("clippy::too_many_lines", SAME, ""),
           ("clippy::unnested_or_patterns", SAME, ""),
           ("clippy::unreachable", PANIC, ""),
           ("clippy::unwrap_used", PANIC, ""),
       ],
       "test_plan.rs": [
           ("unreachable_pub", PUB, ""),
           ("clippy::cognitive_complexity", SAME, ""),
           ("clippy::collapsible_if", SAME, ""),
           ("clippy::disallowed_types", HASH, ""),
           ("clippy::doc_markdown", SAME, ""),
           ("clippy::excessive_nesting", SAME, ""),
           ("clippy::if_not_else", SAME, ""),
           ("clippy::map_unwrap_or", SAME, ""),
           ("clippy::missing_const_for_fn", SAME, ""),
           ("clippy::redundant_closure_for_method_calls", SAME, ""),
           ("clippy::str_to_string", SAME, ""),
           ("clippy::too_many_arguments", SAME, ""),
           ("clippy::too_many_lines", SAME, ""),
           ("clippy::uninlined_format_args", SAME, ""),
           ("clippy::wildcard_imports", SAME, "not(test)"),
           ("clippy::assert_is_empty", SAME, "test"),
       ],
       "domain_model.rs": [
           ("unreachable_pub", PUB, ""),
           ("clippy::cognitive_complexity", SAME, ""),
           ("clippy::collapsible_if", SAME, ""),
           ("clippy::doc_markdown", SAME, ""),
           ("clippy::excessive_nesting", SAME, ""),
           ("clippy::map_unwrap_or", SAME, ""),
           ("clippy::missing_const_for_fn", SAME, ""),
           ("clippy::redundant_closure_for_method_calls", SAME, ""),
           ("clippy::str_to_string", SAME, ""),
           ("clippy::too_many_lines", SAME, ""),
           ("clippy::uninlined_format_args", SAME, ""),
           ("clippy::wildcard_imports", SAME, "not(test)"),
           ("clippy::assert_is_empty", SAME, "test"),
       ],
   }
   COMMANDS = ("check", "analyse", "parse", "plan", "model")
   HANDLES = "stdout: &mut dyn Write, stderr: &mut dyn Write"


   def replace(text: str, old: str, new: str, count: int = 1) -> str:
       """Replace exactly `count` occurrences, or stop."""
       found = text.count(old)
       if found != count:
           sys.exit(f"vendor_cli: expected {count} of {old!r}, found {found}")
       return text.replace(old, new)


   def substitute(text: str, pattern: str, new: str, count: int) -> str:
       """Regex-replace exactly `count` matches, or stop."""
       result, found = re.subn(pattern, new, text)
       if found != count:
           sys.exit(f"vendor_cli: expected {count} matches of {pattern!r}, found {found}")
       return result


   def transform_main(s: str) -> str:
       """Upstream's main.rs as alliumpy_core::cli's main module (cli.rs lists each change)."""
       s = replace(
           s, "mod domain_model;\nmod test_plan;\n\n", "use super::{domain_model, test_plan};\n"
       )
       s = replace(s, "use std::process::ExitCode;\n", "use std::io::Write;\n")
       s = replace(
           s,
           "fn main() -> ExitCode {\n    let args: Vec<String> = std::env::args().skip(1).collect();\n\n",
           f"pub(super) fn main(args: &[String], {HANDLES}) -> i32 {{\n",
       )
       s = replace(
           s,
           '            println!(\n                "allium {} (language versions: 1, 2, 3)",\n'
           '                env!("CARGO_PKG_VERSION")\n            );',
           '            println_to!(stdout, "{}", crate::ALLIUM_VERSION_STRING);',
       )
       s = substitute(s, r"\beprintln!\(", "eprintln_to!(stderr, ", 12)
       s = substitute(s, r"\bprintln!\(", "println_to!(stdout, ", 3)
       s = substitute(s, r"\bprint!\(", "print_to!(stdout, ", 4)
       s = substitute(s, r"ExitCode::SUCCESS", "0", 7)
       s = substitute(s, r"ExitCode::from\((\d)\)", r"\1", 10)
       s = substitute(s, r"-> ExitCode", "-> i32", 9)
       s = replace(
           s,
           '"help" => return cmd_help(&args[1..]),',
           '"help" => return cmd_help(&args[1..], stdout, stderr),',
       )
       for name in COMMANDS:
           s = replace(
               s, f'"{name}" => cmd_{name}(rest),', f'"{name}" => cmd_{name}(rest, stdout, stderr),'
           )
           s = replace(
               s,
               f"fn cmd_{name}(args: &[String]) -> i32 {{",
               f"fn cmd_{name}(args: &[String], {HANDLES}) -> i32 {{",
           )
       s = replace(
           s,
           "fn cmd_help(args: &[String]) -> i32 {",
           f"fn cmd_help(args: &[String], {HANDLES}) -> i32 {{",
       )
       for name in ("check", "analyse"):
           s = replace(
               s,
               f'run_multi_file("{name}", args, |',
               f'run_multi_file("{name}", args, stdout, stderr, |',
           )
       for name in ("plan", "model"):
           old = f'run_single_file("allium {name} <file.allium>", args, |'
           s = replace(s, old, old.replace("args, |", "args, stdout, stderr, |"))
       for first in ("command: &str,", "usage: &str,"):
           old = f"    {first}\n    args: &[String],\n"
           s = replace(s, old, old + "    stdout: &mut dyn Write,\n    stderr: &mut dyn Write,\n")
       return s


   def transform_test_plan(s: str) -> str:
       """Upstream's tests read a fixture by its workspace path; read the parity corpus's copy."""
       return replace(
           s,
           '"../allium-parser/tests/fixtures/v3-lifecycle.allium"',
           '"../../tests/fixtures/parity/crates/allium-parser/tests/fixtures/v3-lifecycle.allium"',
           7,
       )


   def attributes(name: str) -> str:
       """The file-level expectations for one vendored file, one lint per line."""
       lines = []
       for lint, reason, cfg in LINTS[name]:
           body = f'expect({lint}, reason = "{reason}")'
           lines.append(f"#![cfg_attr({cfg}, {body})]" if cfg else f"#![{body}]")
       return "\n".join(lines) + "\n"


   def main() -> None:
       """Write the three vendored files."""
       tag, source, dest = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
       transforms = {"main.rs": transform_main, "test_plan.rs": transform_test_plan}
       for name in LINTS:
           text = (source / name).read_text(encoding="utf-8")
           text = transforms.get(name, lambda s: s)(text)
           out = HEADER.format(tag=tag, name=name) + attributes(name) + text
           (dest / name).write_text(out, encoding="utf-8")


   if __name__ == "__main__":
       main()
   ```

3. **The module** (`crates/alliumpy-core/src/cli.rs`, `crates/alliumpy-core/src/lib.rs`).
   In `lib.rs`, after the crate doc line and a blank line, `pub mod cli;`. `cli.rs`,
   whole:

   ```rust
   //! Upstream's `allium` command, vendored from `juxt/allium-tools` at v3.6.1.
   //!
   //! `cli/main.rs`, `cli/test_plan.rs` and `cli/domain_model.rs` are upstream's
   //! `crates/allium/src/` files with a provenance header and a block of file-level
   //! `#![expect]` attributes. `domain_model.rs` is otherwise unchanged;
   //! `test_plan.rs`'s tests read upstream's `v3-lifecycle.allium` from the parity
   //! corpus (`tests/fixtures/parity/`) instead of upstream's workspace path; and
   //! `main.rs` differs only in these ways:
   //!
   //! - `mod domain_model; mod test_plan;` became `use super::{domain_model, test_plan};`.
   //! - `fn main() -> ExitCode` became `main(args, stdout, stderr) -> i32`, and every
   //!   function that prints takes the two handles; `ExitCode::SUCCESS` and
   //!   `ExitCode::from(n)` became `0` and `n`.
   //! - `print!`, `println!` and `eprintln!` became the macros below, which write to
   //!   the handles and panic on a failed write, as upstream's do.
   //! - `--version` prints [`crate::ALLIUM_VERSION_STRING`] instead of building the
   //!   string from `CARGO_PKG_VERSION`.

   use std::ffi::OsString;
   use std::io::Write;
   use std::panic::{self, AssertUnwindSafe};

   /// Upstream's `print!`, on a handle: a failed write panics, as upstream's does.
   macro_rules! print_to {
       ($w:expr, $($arg:tt)*) => {
           if let Err(error) = write!($w, $($arg)*) {
               panic!("failed printing to stdout: {error}")
           }
       };
   }

   /// Upstream's `println!`, on a handle: a failed write panics, as upstream's does.
   macro_rules! println_to {
       ($w:expr, $($arg:tt)*) => {
           if let Err(error) = writeln!($w, $($arg)*) {
               panic!("failed printing to stdout: {error}")
           }
       };
   }

   /// Upstream's `eprintln!`, on a handle: a failed write panics, as upstream's does.
   macro_rules! eprintln_to {
       ($w:expr, $($arg:tt)*) => {
           if let Err(error) = writeln!($w, $($arg)*) {
               panic!("failed printing to stderr: {error}")
           }
       };
   }

   // Upstream's formatting is kept, so that a re-vendor is a plain copy.
   #[rustfmt::skip]
   mod domain_model;
   #[rustfmt::skip]
   mod main;
   #[rustfmt::skip]
   mod test_plan;

   /// The exit status of a Rust program whose `main` panicked, as upstream's does on a
   /// failed write to a closed pipe.
   const PANIC_EXIT_STATUS: i32 = 101;

   /// Run upstream's `allium` command on `args` (without the program name), writing
   /// to `stdout` and `stderr`, and return its exit status.
   ///
   /// A panic in upstream's code, a failed write included, returns 101 as upstream's
   /// binary exits, after the panic hook has reported it.
   ///
   /// ```
   /// let mut out = Vec::new();
   /// let mut err = Vec::new();
   /// let status = alliumpy_core::cli::run(&["--version".into()], &mut out, &mut err);
   /// assert_eq!((status, out), (0, format!("{}\n", alliumpy_core::ALLIUM_VERSION_STRING).into_bytes()));
   /// ```
   pub fn run(args: &[String], stdout: &mut dyn Write, stderr: &mut dyn Write) -> i32 {
       panic::catch_unwind(AssertUnwindSafe(|| main::main(args, stdout, stderr)))
           .unwrap_or(PANIC_EXIT_STATUS)
   }

   /// [`run`] on arguments as the operating system passed them.
   ///
   /// Upstream reads its arguments with `std::env::args`, which panics on one that is
   /// not UTF-8; this writes that panic's message and returns 101, as upstream's binary
   /// exits.
   ///
   /// ```
   /// let mut out = Vec::new();
   /// let status = alliumpy_core::cli::run_os(vec!["-V".into()], &mut out, &mut Vec::new());
   /// assert_eq!(status, 0);
   /// ```
   #[expect(
       clippy::unnecessary_debug_formatting,
       reason = "upstream's panic message prints the argument with Debug"
   )]
   pub fn run_os(args: Vec<OsString>, stdout: &mut dyn Write, stderr: &mut dyn Write) -> i32 {
       match args
           .into_iter()
           .map(OsString::into_string)
           .collect::<Result<Vec<_>, _>>()
       {
           Ok(args) => run(&args, stdout, stderr),
           Err(arg) => {
               // The message is upstream's panic's; a failure to write it changes nothing.
               let _ = writeln!(
                   stderr,
                   "called `Result::unwrap()` on an `Err` value: {arg:?}"
               );
               PANIC_EXIT_STATUS
           }
       }
   }

   #[cfg(test)]
   mod tests {
       use std::io::{self, Write};

       // Expected statuses are the reference `allium-cli` 3.6.1's, observed on the
       // parity corpus (`tests/fixtures/parity/`, upstream's files unedited).
       const CORPUS: &str = "../../tests/fixtures/parity";
       const LIFECYCLE: &str =
           "../../tests/fixtures/parity/crates/allium-parser/tests/fixtures/v3-lifecycle.allium";
       const EDGE_CASES: &str = "../../tests/fixtures/parity/crates/allium-parser/tests/fixtures/comprehensive-edge-cases.allium";

       fn run(args: &[&str]) -> (i32, String, String) {
           let args: Vec<String> = args.iter().map(|&arg| arg.to_owned()).collect();
           let (mut out, mut err) = (Vec::new(), Vec::new());
           let status = super::run(&args, &mut out, &mut err);
           (
               status,
               String::from_utf8(out).unwrap(),
               String::from_utf8(err).unwrap(),
           )
       }

       #[test]
       fn version_prints_the_copied_literal_and_exits_0() {
           for flag in ["-V", "--version"] {
               let expected = format!("{}\n", crate::ALLIUM_VERSION_STRING);
               assert_eq!(run(&[flag]), (0, expected, String::new()));
           }
       }

       #[test]
       fn no_arguments_exit_2_with_usage_on_stderr() {
           let expected = "allium: missing command\nRun `allium --help` for usage.\n";
           assert_eq!(run(&[]), (2, String::new(), expected.to_owned()));
       }

       #[test]
       fn unknown_commands_exit_2_with_nothing_on_stdout() {
           for args in [&["frobnicate"][..], &["help", "frobnicate"]] {
               let (status, out, err) = run(args);
               assert_eq!((status, out.as_str()), (2, ""));
               assert!(err.starts_with("allium: unknown command `frobnicate`\n"));
           }
       }

       #[test]
       fn help_forms_print_help_on_stdout_and_exit_0() {
           for args in [&["help"][..], &["-h"], &["--help"]] {
               let (status, out, _) = run(args);
               assert_eq!(status, 0);
               assert!(out.starts_with("allium - validate, parse and analyse"));
           }
           for command in ["check", "analyse", "parse", "plan", "model"] {
               for args in [
                   &["help", command][..],
                   &[command, "--help"],
                   &[command, "-h"],
               ] {
                   let (status, out, _) = run(args);
                   assert_eq!(status, 0);
                   assert!(out.starts_with(&format!("allium {command} - ")));
               }
           }
       }

       /// The number of `.allium` files under the corpus, walked with an explicit stack.
       fn corpus_files() -> usize {
           let mut pending = vec![std::path::PathBuf::from(CORPUS)];
           let mut count = 0;
           while let Some(dir) = pending.pop() {
               let paths = std::fs::read_dir(dir)
                   .unwrap()
                   .map(|entry| entry.unwrap().path());
               let (dirs, files): (Vec<_>, Vec<_>) = paths.partition(|path| path.is_dir());
               count += files
                   .iter()
                   .filter(|path| path.extension().is_some_and(|ext| ext == "allium"))
                   .count();
               pending.extend(dirs);
           }
           count
       }

       #[test]
       fn check_and_analyse_of_the_corpus_report_every_file_and_exit_1() {
           let files = corpus_files();
           assert!(files > 0);
           for command in ["check", "analyse"] {
               let (status, out, _) = run(&[command, CORPUS]);
               assert_eq!(status, 1);
               let reported = out.matches(&format!("\"command\": \"{command}\"")).count();
               assert_eq!(reported, files);
           }
       }

       #[test]
       fn check_exits_1_on_a_file_with_an_error_or_warning() {
           let (status, out, _) = run(&["check", EDGE_CASES]);
           assert_eq!(status, 1);
           assert!(
               out.contains("\"severity\": \"error\"") || out.contains("\"severity\": \"warning\"")
           );
       }

       #[test]
       fn single_file_commands_exit_0_on_a_file_that_parses() {
           for command in ["parse", "plan", "model"] {
               let (status, out, _) = run(&[command, LIFECYCLE]);
               assert_eq!(status, 0);
               assert!(out.contains("\"diagnostics\""));
           }
       }

       #[test]
       fn missing_inputs_exit_2_and_unreadable_files_exit_1() {
           for command in ["parse", "plan", "model"] {
               assert_eq!(run(&[command]).0, 2);
               assert_eq!(run(&[command, LIFECYCLE, LIFECYCLE]).0, 2);
               assert_eq!(run(&[command, "does-not-exist.allium"]).0, 1);
           }
           assert_eq!(
               run(&["check"]),
               (2, String::new(), "No .allium files found.\n".to_owned())
           );
           assert_eq!(run(&["check", "does-not-exist.allium"]).0, 1);
       }

       struct ClosedPipe;

       impl Write for ClosedPipe {
           fn write(&mut self, _: &[u8]) -> io::Result<usize> {
               Err(io::ErrorKind::BrokenPipe.into())
           }

           fn flush(&mut self) -> io::Result<()> {
               Ok(())
           }
       }

       #[cfg(unix)]
       #[test]
       fn an_argument_that_is_not_utf8_exits_101_as_upstreams_panic_does() {
           use std::os::unix::ffi::OsStringExt;
           let args = vec![
               "check".into(),
               std::ffi::OsString::from_vec(b"\xff.allium".to_vec()),
           ];
           let (mut out, mut err) = (Vec::new(), Vec::new());
           assert_eq!(super::run_os(args, &mut out, &mut err), 101);
           assert_eq!(
               (out, String::from_utf8(err).unwrap()),
               (
                   Vec::new(),
                   "called `Result::unwrap()` on an `Err` value: \"\\xFF.allium\"\n".to_owned()
               )
           );
       }

       #[test]
       fn utf8_arguments_run_the_command() {
           let (mut out, mut err) = (Vec::new(), Vec::new());
           assert_eq!(super::run_os(vec!["-V".into()], &mut out, &mut err), 0);
           assert_eq!(
               out,
               format!("{}\n", crate::ALLIUM_VERSION_STRING).into_bytes()
           );
       }

       #[test]
       fn a_failed_write_exits_101_as_upstreams_panic_does() {
           assert_eq!(
               super::run(&["--version".to_owned()], &mut ClosedPipe, &mut Vec::new()),
               101
           );
       }
   }
   ```

   Proof: `just fmt-check`, `just clippy` (exit 0 with no change to the lint tables or
   `clippy.toml`), `just test` (157 tests at S01: 146 upstream and existing plus eleven in
   `cli.rs`; the corpus count is walked, not written, so T13's added files need no edit),
   `just doc`.

4. **rustqual and EditorConfig** (`rustqual.toml`, `.editorconfig`, both `shared, own
   lines`). In `rustqual.toml`, before `allow_recursion`:

   ```toml
   # Upstream's CLI, vendored unchanged under the core's src/cli/ (decision 0014), is
   # upstream's code, not this repository's: its shape is upstream's to change, and
   # parity, not these metrics, is its gate. cli.rs, this repository's own glue, stays
   # measured. Globs resolve against the target directory, as noted above.
   exclude_files = ["src/cli/main.rs", "src/cli/test_plan.rs", "src/cli/domain_model.rs"]
   ```

   Proof: `just metrics` exit 0, both crates `Quality score: 100.0%`. In
   `.editorconfig`, after the `[*.rs]` section:

   ```ini
   # Upstream's CLI, vendored unchanged under the core's src/cli/ (decision 0014),
   # indents its help text and its tests' Allium sources inside string literals by
   # upstream's amounts; reindenting would change the command's output. Only the
   # indent-size rule is lifted; cli.rs and any other file under src/cli/ stay checked.
   [crates/alliumpy-core/src/cli/{main,test_plan,domain_model}.rs]
   indent_size = unset
   ```

   Proof: with the vendored files staged (`git add`), `just lint` exit 0 with
   `EditorConfig` `Passed`; without the section it fails on the 28 lines S01 quoted.

5. **The binding, the stub and the shim** (`crates/alliumpy/src/lib.rs`,
   `crates/alliumpy/python/alliumpy/_alliumpy.pyi`, `_cli.py`,
   `crates/alliumpy/tests/test_run_cli.py`). In `lib.rs`, `use std::ffi::OsString;` and
   `use std::io::Write;` after the `pyo3` imports, and before the `#[pymodule]`:

   ```rust
   /// Run upstream's `allium` command on the process's own stdout and stderr.
   #[pyfunction(name = "_run_cli")]
   fn run_cli(args: Vec<OsString>) -> i32 {
       let mut stdout = std::io::stdout();
       let status = alliumpy_core::cli::run_os(args, &mut stdout, &mut std::io::stderr());
       // Upstream's binary flushes stdout as it exits and ignores a failure there.
       let _ = stdout.flush();
       status
   }
   ```

   and `module.add_function(wrap_pyfunction!(run_cli, module)?)?;` after `parse`'s. In
   the stub, `"_run_cli"` in `__all__` between `"Diagnostic"` and `"parse"` (pyo3 puts
   it in the runtime `__all__`, so stubtest requires it; ruff's formatter then wraps the
   list one name per line), and at the end:

   ```python
   def _run_cli(args: list[str]) -> int:
       """Run upstream's allium command on the process's stdout and stderr; return its status."""
   ```

   `_cli.py`, whole:

   ```python
   # Copyright 2026 Steven Cutting
   """Console entry point: upstream's allium command, vendored into the extension."""

   import os
   import signal
   import sys

   from ._alliumpy import _run_cli


   def main() -> int:
       """Run upstream's command on this process's arguments and return its exit status."""
       # Upstream's binary dies on SIGINT at once; Python's handler would wait for the
       # command to finish, then print a KeyboardInterrupt traceback.
       signal.signal(signal.SIGINT, signal.SIG_DFL)
       # Rust's runtime points a closed standard descriptor at the null device before
       # upstream's main runs, so its output goes nowhere rather than into a file it opens.
       for fd in (0, 1, 2):
           try:
               os.fstat(fd)
           except OSError:
               null = os.open(os.devnull, os.O_RDWR)
               if null != fd:
                   os.dup2(null, fd)
                   os.close(null)
       status = _run_cli(sys.argv[1:])
       for stream in (sys.stdout, sys.stderr):
           if stream is not None:
               stream.flush()
       return status
   ```

   There is no Windows branch to write under (a): the extension runs in-process on every
   platform, and `signal.SIG_DFL`, `os.fstat`, `os.devnull` and `os.dup2` exist on
   Windows too (designed, not run there). `test_run_cli.py`, whole (the binding's own case; T13's `test_cli.py` stays
   subprocess-only):

   ```python
   # Copyright 2026 Steven Cutting
   """Verify the vendored allium command through the extension, on the process's streams."""

   import pytest
   from alliumpy._alliumpy import ALLIUM_VERSION_STRING, _run_cli


   def test_version_prints_upstreams_string_on_the_process_stdout(
       capfd: pytest.CaptureFixture[str],
   ) -> None:
       """Upstream's --version line reaches file descriptor 1, and the status is 0."""
       assert _run_cli(["--version"]) == 0
       assert capfd.readouterr() == (ALLIUM_VERSION_STRING + "\n", "")


   def test_no_arguments_exit_2_with_upstreams_message_on_stderr(
       capfd: pytest.CaptureFixture[str],
   ) -> None:
       """Upstream's missing-command lines reach file descriptor 2, and the status is 2."""
       assert _run_cli([]) == 2
       assert capfd.readouterr() == ("", "allium: missing command\nRun `allium --help` for usage.\n")
   ```

   Proof: `just py-lint`, `just py-typecheck`, `just py-test` (19 passed at S01),
   `just py-stubtest`, `just wheel-smoke` printing `allium 3.6.1 (language versions: 1, 2, 3)`.

6. **Coverage** (no file). The `coverage` recipe and its floor are unchanged. Proof:
   `just coverage` exit 0, quoted with the per-file table; S01 measured 91.36% over the
   core (`cli/main.rs` 86.19%; the three vendored files 90.95%).

7. **The licence sentence** (`crates/alliumpy/LICENSE-allium-tools`, `shared, own
   lines`): the route sentence reads "The wheel carries upstream's `allium` command
   logic from allium-tools v3.6.1, vendored into the `alliumpy-core` crate
   (`crates/alliumpy-core/src/cli/`), and the source distribution carries the same
   files; the parity fixtures under `tests/fixtures/parity/` are upstream's files at
   the same tag." Proof: `just check-docs` unaffected, `just wheel-smoke` (the text
   ships in `.dist-info/licenses/`).

8. **The gate.** `just check` ends with `All checks passed and the worktree is
   unchanged.`; then T13's step 7 runs `just parity`, which must print `0 differ` with
   both controls fired.

## Acceptance criteria

- `just parity` prints `N compared, 0 differ` with `N` equal to the corpus count times
  the subcommand count plus the argument-matrix count `tests/parity/README.md` states,
  after both controls fired, headed by the commit; the same run at step 3, before the
  command existed, printed a difference for every corpus and directory-form comparison,
  and matched only on `-V`, `--version` and rows whose reference stdout is empty and
  exit status 2, each matching row listed by name in the hand-back notes and checked
  against the reference's own stdout and exit status.
- `just wheel-smoke` ends with `allium check tests/fixtures/smoke/ok.allium` exiting 0.
- `just version-check` passes with the full string, and fails when the literal (or the
  derivation) in `crates/alliumpy-core/src/lib.rs` is changed by one character in a
  scratch copy.
- `test_cli.py` runs inside `just parity`, not skipped: the pytest summary line of
  that run is quoted in the hand-back notes and carries no `skipped` count on Linux,
  and `-rs` prints no `SKIPPED` line there (on macOS the only `SKIPPED` line is the
  `/dev/full` case's); its broken-pipe case asserts the exit status S01 recorded for
  the reference; its `/dev/full` case does the same on Linux and is skipped, with its
  reason printed, on macOS; and its Python-API case compares `alliumpy.parse` over
  every corpus file and `broken.allium` with `allium check`'s `location.line` and
  `location.col`, its per-file count equals `allium parse`'s `diagnostics` length, and
  its total diagnostic count, printed, is at least one. Under
  `just py-test` the module is collected and skipped with the stated reason.
- `.tools/parity/bin` is not on the Justfile's `PATH`: `just --evaluate PATH | tr ':' '\n'
  | grep parity` exits 1. The harness invokes the reference only by absolute path and the
  candidate only as the smoke venv's `allium`, `$PWD/target/wheel-smoke/venv/bin/allium`
  (`CONVENTIONS.md` §9, "The parity reference"). The `allium` in
  `.pixi/envs/default/bin/` is the wheel's own console script, installed by `py-develop`,
  and is expected; it is neither the reference nor the candidate.
- The `parity` CI job is green on the pull request and is in `check`'s `needs`.
- Decision 0014 is landed and `just check-docs` is green.
- `just check` is green.
- The adversarial reviews in Steps ran (`CONVENTIONS.md` §14), and every valid finding is
  fixed or handed back.

## Verification

```sh
just install-parity-reference
.tools/parity/bin/allium --version; echo "exit $?"
just wheel-smoke; echo "exit $?"
target/wheel-smoke/venv/bin/allium --version; echo "exit $?"
just parity; echo "exit $?"
mkdir -p ai_tmp/empty-corpus && .pixi/envs/default/bin/python -I tests/parity/run.py --reference "$PWD/.tools/parity/bin/allium" --candidate "$PWD/target/wheel-smoke/venv/bin/allium" --corpus ai_tmp/empty-corpus; echo "exit $?"   # must be nonzero, with the harness's empty-corpus message, not a missing directory or an identical candidate
just version-check; echo "exit $?"
cp crates/alliumpy-core/src/lib.rs ai_tmp/lib.rs.orig && sed -i.bak 's/language versions: 1/language versions: 9/' crates/alliumpy-core/src/lib.rs && just version-check; echo "exit $?"   # must be nonzero; adapt the pattern if the string is derived
mv ai_tmp/lib.rs.orig crates/alliumpy-core/src/lib.rs && rm -f crates/alliumpy-core/src/lib.rs.bak && just version-check; echo "exit $?"   # must be 0 again
env -u ALLIUMPY_SMOKE_BIN .pixi/envs/default/bin/python -m pytest crates/alliumpy/tests/test_cli.py -rs; echo "exit $?"   # exit 0; every line is SKIPPED with the reason: ALLIUMPY_SMOKE_BIN unset; run just parity
just --evaluate PATH; echo "exit $?"   # must print the PATH and exit 0: the positive control for the next line
just --evaluate PATH | tr ':' '\n' | grep parity; echo "exit $?"   # must be 1: the reference root is off PATH
rg -n 'from T13' AGENTS.md .agents; echo "exit $?"   # must be 1
ls tests/fixtures/parity | head; find tests/fixtures/parity -name '*.allium' | wc -l
find tests/fixtures/parity -name '*.allium' -empty | wc -l   # must be 0
gh pr checks <number> --repo BiscuitBin/alliumpy
just check
```

The empty-corpus harness line and the `env -u` pytest line name the worktree's pixi
interpreter by path because they run from the agent's shell, where nothing puts `python`
on `PATH`; inside `just parity` the bare `python` is the same interpreter.

## Hand-back notes

Executed by Claude Code (Claude Opus 5.5) in this worktree on 2026-10-29. Commits:
`5bbc289` (the route, the corpus, the harness, `test_cli.py`, the recipes), `a3f32f0`
(checkpoint 1 fixes), `f358914` (CI, decision 0014, the pages), `d0a6841` (checkpoint 2
and code-review fixes), then this file's commit. Raw logs are in `ai_tmp/logs/`, never
committed.

### Baseline (step 1)

At `c09f6fa`, untouched: `just initialize` exit 0, then `just check` exit 0:

```text
All checks passed and the worktree is unchanged.
```

### The reference recipe (step 2)

`version_check.py --print-pin` red first, at `c09f6fa` with only that file changed: the
flag was ignored and the full check ran (`version-check: all five versions agree:
3.6.1`, exit 0, not `3.6.1`). After the change, with `target/wheel-smoke/` moved aside,
`--print-pin` printed `3.6.1`, exit 0, while the plain run failed with `run just
wheel-smoke first`, exit 1. `just install-parity-reference`, exit 0:

```text
allium 3.6.1 (language versions: 1, 2, 3)
```

The "from T13" qualifiers are gone from `AGENTS.md` (invariant 1, network-recipe list)
and `.agents/skills/python-change/SKILL.md`; see Deviations for the third, in
`review-change`.

### The corpus and the harness (step 3)

Under `bash` with `set -o pipefail`: the `v3.6.1` tree's `.truncated` printed `false`;
the `.allium` listing (`"\(.path) \(.sha)"`) held 27 lines; every file fetched by one
`gh api` read, `test -s` and `git hash-object` equal to the listed sha (`fetch exit 0`),
fetched into an empty `ai_tmp/parity-fetch/` and copied in; rechecked in place,
`hash check fail=0`. `find tests/fixtures/parity -name '*.allium' | wc -l` prints 29 (27
upstream plus the pair), `-empty` prints 0. The pair is
`alliumpy/xmod/core.allium` and `alliumpy/xmod/app/orders.allium` (`use
"../core.allium" as core`), S01's supplementary pair with its comment line re-attributed
to this repository; `broken_import.allium` is left out.

`tests/parity/run.py` sha-256
`db22c87f84f2aa202eb794e47f7f5afc65e86ffe4af4151baac880de205ae8ae`, equal to S01's;
`ruff check` `All checks passed!`, `ruff format --check` `1 file already formatted`, with
no edit. `mypy.ini` gained `tests/parity`; `mypy -v 2>&1 | grep tests/parity/run.py`
printed `LOG:  Found source: BuildSource(path='tests/parity/run.py', ...)` and two more
lines, exit 0, and `just py-typecheck` exit 0 (`Success: no issues found in 7 source
files`).

**The run before the command existed**, at `c09f6fa` with the corpus, harness and
recipes uncommitted, against T00's shim; `just parity` exit 1 at the harness line:

```text
positive control: check <corpus>/alliumpy/xmod/app/orders.allium exits 1 under the reference
202 compared, 187 differ
negative control: candidate plus one byte, check <corpus>/alliumpy/xmod/app/orders.allium: fired (stdout differs)
negative control: candidate forced to exit 0, check <corpus>/alliumpy/xmod/app/orders.allium: fired (exit status: reference 1, candidate 0)
```

The 15 `same` rows, each with the reference's own exit and stdout size from its row:

```text
same    check [reference: exit 2, stdout 0 bytes] (stderr differs, reported only)
same    analyse [reference: exit 2, stdout 0 bytes] (stderr differs, reported only)
same    check <empty directory> [reference: exit 2, stdout 0 bytes] (stderr differs, reported only)
same    analyse <empty directory> [reference: exit 2, stdout 0 bytes] (stderr differs, reported only)
same    (no arguments) [reference: exit 2, stdout 0 bytes] (stderr differs, reported only)
same    -V [reference: exit 0, stdout 42 bytes]
same    --version [reference: exit 0, stdout 42 bytes]
same    frobnicate [reference: exit 2, stdout 0 bytes] (stderr differs, reported only)
same    help frobnicate [reference: exit 2, stdout 0 bytes] (stderr differs, reported only)
same    parse [reference: exit 2, stdout 0 bytes] (stderr differs, reported only)
same    parse <corpus>/alliumpy/xmod/app/orders.allium <corpus>/extensions/allium/test/fixtures/refactor/extract-literal.input.allium [reference: exit 2, stdout 0 bytes] (stderr differs, reported only)
same    plan [reference: exit 2, stdout 0 bytes] (stderr differs, reported only)
same    plan <corpus>/alliumpy/xmod/app/orders.allium <corpus>/extensions/allium/test/fixtures/refactor/extract-literal.input.allium [reference: exit 2, stdout 0 bytes] (stderr differs, reported only)
same    model [reference: exit 2, stdout 0 bytes] (stderr differs, reported only)
same    model <corpus>/alliumpy/xmod/app/orders.allium <corpus>/extensions/allium/test/fixtures/refactor/extract-literal.input.allium [reference: exit 2, stdout 0 bytes] (stderr differs, reported only)
```

Thirteen match by empty stdout and exit 2, two (`-V`, `--version`) by the 42-byte
`ALLIUM_VERSION_STRING` line and exit 0: exactly S01's fifteen (S01:1017-1044), with
`first` now the pair's importer because `alliumpy/` sorts before `crates/`. All 145
per-file rows (`grep -cE '^DIFFER  (check|analyse|parse|plan|model) <corpus>/[^ ]+\.allium \['`
printed 145) and all four directory-form rows differ. The positive control is the pair's
importer, as S01 predicted for an `alliumpy/` file that exits 1; `orders.allium` exits 1
because `check` of it alone leaves `../core.allium` out of the check set.

### Route-specific steps as executed (step 4, route (a))

Copied verbatim from S01:1742-2400 under the heading the ticket names; see Deviations
for where.

1. `serde = { version = "1.0.229", features = ["derive"] }` and `serde_json = "1.0.154"`,
   the locked versions, with S01's comments; `cargo update -p serde -p serde_json
   --offline` (`Locking 0 packages`); `git diff Cargo.lock` adds only `"serde",` and
   `"serde_json",` to `alliumpy-core`; `just deny` exit 0 (`bans ok, licenses ok, sources
   ok`; its `unmatched license allowance` warning is in the baseline log too).
2. The three files fetched into `ai_tmp/upstream/`, each exit 0 and non-empty, hashes
   equal to the tree's (`main.rs` `dc10ec7f…`, `test_plan.rs` `a774e2be…`,
   `domain_model.rs` `f9b60de6…`). `vendor_cli.py`, extracted from S01:1776-1964, saved
   as `ai_tmp/vendor_cli.py` and run with the pixi interpreter: exit 0; diffs `main.rs
   +79 -65`, `test_plan.rs +28 -7`, `domain_model.rs +18 -0`, as S01 measured.
3. `cli.rs` verbatim, `pub mod cli;` in `lib.rs`. `just fmt-check` exit 0, `just clippy`
   exit 0 with no change to the lint tables or `clippy.toml`, `just test` `157 tests run:
   157 passed, 0 skipped`, `just doc` exit 0.
4. `exclude_files` and the `.editorconfig` section as drafted. `just metrics` exit 0,
   `Quality score: 100.0%` for both crates; with everything staged, `just lint`
   `EditorConfig ... Passed`. The without-section control was not rerun (S01 recorded
   it).
5. `test_run_cli.py` first: `just py-test` exit 2 at collection (`ERROR
   crates/alliumpy/tests/test_run_cli.py`). Then the binding, the stub (`__all__` wrapped
   one name per line by `ruff format`) and `_cli.py` verbatim: `py-lint`, `py-typecheck`,
   `py-stubtest` exit 0, `py-test` `19 passed`, `wheel-smoke` printing `allium 3.6.1
   (language versions: 1, 2, 3)`.
6. `just coverage` exit 0, lines:

   ```text
   cli.rs                 136 lines   3 missed   97.79%
   cli/domain_model.rs    639        43          93.27%
   cli/main.rs            485        40          91.75%
   cli/test_plan.rs      2134       185          91.33%
   lib.rs                 112         0         100.00%
   TOTAL                 3506       271          92.27%
   ```

   (S01: 91.36%, `main.rs` 86.19%; the pair lifts `main.rs`, as S01 predicted.)
7. `LICENSE-allium-tools` line 3, T11's leftover, replaced by S01's sentence verbatim.
8. `just check` exit 0, `All checks passed and the worktree is unchanged.`

### `/dev/full` on Linux (U17)

The reference, `cargo install allium-cli@3.6.1 --locked` in a `rust:latest` container
(`Linux ... aarch64`), `>/dev/full`, three runs each of `-V`, `--version`, `check` of
`v3-lifecycle.allium`, of `comprehensive-edge-cases.allium` and of the corpus directory,
and `parse`: every run exit 101 with stderr

```text

thread 'main' (<tid>) panicked at /rustc/58cf8f9c35b355199727627d07ae34a4e2846d67/library/std/src/io/stdio.rs:1168:9:
failed printing to stdout: No space left on device (os error 28)
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

so `test_cli.py` asserts exit 101, the `failed printing to stdout: No space left on
device (os error 28)` line and no `Traceback`. U17 is closed.

### The behaviours beyond the corpus (step 5)

`test_cli.py` reads `ALLIUMPY_SMOKE_BIN`, imports nothing from `alliumpy` and takes every
Python value from the smoke venv's interpreter. Each expectation was measured on the
reference with the test's own mechanism, by running the module against the reference
(`ai_tmp/refbin/allium`, a symlink to it beside a `python` wrapper for the smoke venv):

| Case | Reference | Candidate | Source |
| --- | --- | --- | --- |
| `check` ok / broken, no arguments, empty directory | 0 / 1, 2, 2 | same | S01:1109-1111 |
| `-V`, `--version` | `ALLIUM_VERSION_STRING\n`, exit 0, empty stderr | same | S01:1111-1112 |
| `parse`, `plan`, `model`, `analyse` on `broken.allium` | 1, 1, 1, 0 | same | measured here (checkpoint 1, A) |
| `check <corpus> \| head -c 1` | 101, `failed printing to stdout: Broken pipe (os error 32)`, no traceback | same | S01:981-1005, 1072-1080 |
| `>/dev/full`, `-V` and `check` (Linux) | 101, `... No space left on device (os error 28)` | same | measured here, above |
| `>&-`: `-V`, `check` ok, `check` broken | 0, 0, 1, empty stderr | same | S01:1116 |
| `check $'\xff.allium'` | 101, empty stdout, ``called `Result::unwrap()` on an `Err` value: "\xFF.allium"``, no traceback | same | S01:1115 |
| SIGINT 2 s into `check <FIFO>` | `-SIGINT` within 6 s, empty stderr | same | S01:1117; T13 step 5 |
| `check does-not-exist.allium v3-lifecycle.allium` on one pty | exit 1, 11908 bytes, sha-256 `b6ef8035…7559a`, stderr line first | same, 3 runs each | S01:1008-1015 |
| `parse` against `check`'s leading diagnostics, and `allium parse`'s count and status, 30 files | equal | equal | T13 step 5 |

The flush-order bytes are not S01's (S01 used `script`); the test's own `pty.openpty`
reading was recorded from the reference on macOS and matched on Linux. The total-count
case printed `parse diagnostics over 30 files: 1`: every corpus file parses with no
parser diagnostic, so the Python-API comparison rests on `broken.allium` alone (Open
points). Checkpoint 1's reviewers confirmed that shifting the API's `line` or `col` by
one fails it.

With the variable unset (`env -u`), every case is `SKIPPED ... ALLIUMPY_SMOKE_BIN unset;
run just parity`, `50 skipped`, exit 0; `just py-test` collects and skips the module the
same way.

### `version-check` and claim 12 (step 6)

Claim 12 as S01 ruled: not derivable, so the literal stays and `version_check.py` reads
it by regex from the core's `lib.rs`. The whole console output must equal that literal
plus a newline. When `.tools/parity/bin/allium` exists, it must run within 60 s, exit 0
and print a well-formed `allium x.y.z` line, or the check fails (checkpoints 1 and 2); at
the pin its output must equal the console's; at another version, or when absent, a note
names `just install-parity-reference`. At `d0a6841`, the passing run, the
one-character control (`language versions: 9`) failing, and the restored file passing:

```text
version-check: all five versions agree: 3.6.1
version-check: the reference prints the same: allium 3.6.1 (language versions: 1, 2, 3)
exit 0
version-check: console output 'allium 3.6.1 (language versions: 1, 2, 3)\n' differs from ALLIUM_VERSION_STRING='allium 3.6.1 (language versions: 9, 2, 3)'
error: recipe `version-check` failed on line 306 with exit code 1
exit 1
version-check: the reference prints the same: allium 3.6.1 (language versions: 1, 2, 3)
exit 0
```

With `.tools/parity` moved aside: `version-check: note: no reference allium 3.6.1 to
compare; run just install-parity-reference`, exit 0. The CI log of this step is pending
the pull request. `wheel-smoke` ends with `allium check tests/fixtures/smoke/ok.allium`,
exit 0 (its JSON's last lines `"spec_file": "tests/fixtures/smoke/ok.allium"` and `}`).

### The green parity run (step 7)

At `5bbc289` (macOS arm64), `just parity` exit 0:

```text
positive control: check <corpus>/alliumpy/xmod/app/orders.allium exits 1 under the reference
202 compared, 0 differ
negative control: candidate plus one byte, check <corpus>/alliumpy/xmod/app/orders.allium: fired (stdout differs)
negative control: candidate forced to exit 0, check <corpus>/alliumpy/xmod/app/orders.allium: fired (exit status: reference 1, candidate 0)
======================== 44 passed, 2 skipped in 6.87s =========================
```

202 = 5 × 29 + 53 + 4 × 1, the count `tests/parity/README.md` states. No row reported a
stderr difference. At `d0a6841`, again exit 0, the same four harness lines, then:

```text
parse diagnostics over 30 files: 1
SKIPPED [2] crates/alliumpy/tests/test_cli.py:147: /dev/full exists only on Linux; S01 measured on macOS, so the parity CI job on Linux is where this runs
======================== 48 passed, 2 skipped in 6.57s =========================
```

On Linux, in a `python:3.13-bookworm` container with the wheel built from this worktree's
content at `d0a6841` (`alliumpy-3.6.1-cp311-abi3-manylinux_2_34_aarch64.whl`, toolchain
1.99.1) and the reference built there: the harness exit 0 with the same four lines, and
`test_cli.py` `50 passed` with no skip, against the candidate and against the reference
(`ai_tmp/linux-parity.sh`). The `parity` CI job is the record; its run is pending.

### CI (step 8)

`parity` job after `python`: the setup action (`cache-key: parity`), `actions/cache` on
`.tools/parity` keyed on the runner's OS and architecture and `hashFiles('Cargo.toml')`
with no restore keys, then `install-parity-reference`, `parity`, `version-check`,
`check-clean`; `parity` added to `check`'s `needs` (the header comment now says seven
gate jobs); `venv/bin/allium check tests/fixtures/smoke/ok.allium` in
`wheel-smoke-py311`. `actions/cache` is pinned to the SHA the setup action already uses;
re-read with `gh api repos/actions/cache/git/ref/tags/v6.1.0`, `commit
55cc8345863c7cc4c66a329aec7e433d2d1c52a9`. actionlint passed in `just lint`.

### The record and the pages (step 9)

`0014-cli-strategy.md` is S01's draft, byte for byte (S01:1667-1734), with frontmatter
equal to the manifest; 0014's row already existed, so `decisions/README.md` changes only
line 41 (T11's leftover); 0007 gains one sentence pointing to `exclude_files`; own-lines
edits to `architecture`, `install-and-run`, `commands` (a Parity table and the changed
`wheel-smoke`/`version-check` rows), `testing` (a Command parity section),
`quality-gates`, `quality-philosophy` and `security-model`; the `CHANGELOG.md` line.
`just check-docs` exit 0.

### Verification

At `d0a6841`, `git status --short` printing only this file as modified,
under `bash` (`ai_tmp/verify.sh`); outputs above, plus:

```text
allium 3.6.1 (language versions: 1, 2, 3)
exit 0
wheel-smoke exit 0
allium 3.6.1 (language versions: 1, 2, 3)
exit 0
parity exit 0
parity: empty corpus: no .allium file under .../ai_tmp/empty-corpus
exit 2
50 skipped in 0.01s
exit 0
<the PATH, one line, ending in .../Contents/MacOS>exit 0
exit 1
exit 1
alliumpy
crates
docs
extensions
README.md
      29
       0
```

`just --evaluate PATH` prints no newline, so its `exit 0` joins the line. The PATH grep
for `parity` and the `from T13` grep each exit 1. `gh pr checks` waits for step 11. `just check` after this file's commit is
quoted in the pull request, since a file cannot quote the run on its own commit.

### What an upstream bump costs under route (a), for T17

Fetch the three files at the new tag and the new tag's `.allium` files (one `gh api` read
each, hash-checked); run `vendor_cli.py` (in `ai_tmp/`, unedited across `v3.6.0` and
`v3.6.1`; a stop means upstream changed a rewritten line, so update the transform by hand
and review it); review upstream's own diff to the three files; update `cli.rs`'s header
line naming the tag, the corpus and its README, the `test_plan.rs` fixture path if it
moved, `ALLIUM_VERSION`, `ALLIUM_VERSION_STRING`, the pin, the crate and wheel versions
(invariant 9), and `LICENSE-allium-tools`; re-measure the `TERMINAL_*` constants in
`test_cli.py` from the new reference (they change with `v3-lifecycle.allium` or upstream's
JSON); `just install-parity-reference` (the CI cache key moves with `Cargo.toml`), `just
check`, `just parity`. Watch coverage: 92.27% now, and an upstream bump that adds
untested lines to `main.rs` moves it. A `serde`/`serde_json` bump in this repository's
lock also changes the vendored command's dependencies and is a reason to run `just
parity`. U16 (where `vendor_cli.py` lives) stays with T17: it remains scratch here.

### Review records (§14)

**Checkpoint 1** (step 7), at `5bbc289`. Reviewers: Codex `gpt-6-astra`, read-only, one
per lens (`ai_tmp/review/T13-1/`); triage and fixes: one fresh-context Claude Opus 5.5
subagent. Both lenses answered Q2, Q3, Q5 and Q6 with no finding: the candidate is the
smoke venv's launcher on the wheel's bytes; paths in the JSON match as given, with no
normalisation; the red run's 15 matches and 187 differences check against the
reference; an off-by-one `line` or `col` fails the API case. Q4: `help check extra`,
`parse <corpus>`, `plan F -h` are absent from the matrix and matched by hand.

| Finding | Severity | Verdict | Applied |
| --- | --- | --- | --- |
| A: parser-error exit status of `parse`/`plan`/`model` compared nowhere (both lenses F1) | medium | valid: every corpus file parses cleanly | `test_cli.py` asserts the reference's 1, 1, 1, 0 on `broken.allium` and `allium parse`'s status in the API case; a mutated candidate fails 4 cases |
| B: `version-check` ignores the reference's return code (both F2) | medium | valid | a reference that does not run or exits nonzero fails |
| C: `review-change/SKILL.md` outside Files touched (conformance F3) | low | valid, required by Verification | recorded under Deviations, not reverted |
| D: the pty read cannot time out (breakage F3) | medium | valid | `select` with a deadline; on expiry kill and `pytest.fail` |

No high finding, so no second round. Re-run at `a3f32f0`'s content: `just parity` exit 0,
`202 compared, 0 differ`, both controls fired, `48 passed, 2 skipped`; Linux `50 passed`
for both binaries; `just check` exit 0.

**Checkpoint 2** (step 10), at `f358914`, over `git diff main...HEAD`, the same harness
and model (`ai_tmp/review/T13-2/`). Q1: no route step executed differently from S01's
draft. Q3: no (`parity` sets the variable on its own line). Q4: no (the key hashes
`Cargo.toml`, there are no restore keys, and `install-parity-reference` always runs).

| Finding | Severity | Verdict | Applied |
| --- | --- | --- | --- |
| E: a reference exiting 0 with empty or malformed output passes as stale (both F1, answering Q2) | medium | valid | only a well-formed `allium x.y.z` line can be stale; 8 probes as expected |
| F: the `review-change` edit (conformance F2, breakage F3) | low | valid, as C | recorded under Deviations |
| G: `ai_tmp/linux-parity.sh` does not propagate failures (breakage F2) | low | valid, scratch only | fixed in the scratch script; the quoted logs show each status |

No high finding, so no second round.

**Code review** (the `code-review` skill, medium effort, over the lane's diff after
checkpoint 2), unverified candidates triaged by the executing agent:

| Candidate | Verdict | Applied |
| --- | --- | --- |
| reference `--version` has no timeout | valid, low | 60 s timeout, a failed read |
| `import pty` breaks collection on Windows | valid, low | `pytest.importorskip("pty")` |
| SIGINT test's fixed 2 s sleep may race Python's startup on a slow runner | plausible; the 2 s are the ticket's and S01's | handed back (Open points) |
| `.tools/parity` could enter the setup action's `.tools` cache if `python`'s save loses a race | plausible, low; the fix is in `.github/actions/setup/action.yml`, outside Files touched | handed back (Open points) |
| upstream's `std::env::args().skip(1)` also decodes `argv[0]`; `run_os` gets `sys.argv[1:]` | valid, low: an install path that is not UTF-8 would print a version where upstream exits 101 | handed back (Open points): S01's drafted `cli.rs` and binding |
| `_run_cli` uses the global `Stdout` buffer across calls | low; private API, S01's binding | not applied |
| `_cli.py` flushes Python's streams after the call | invalid as a defect: nothing writes before it; S01's text | not applied |
| the total-count case reparses every file | low, cost only | not applied |
| `run.py`'s zero-comparison guard cannot fire | invalid: S01 kept it deliberately (S01:1218-1219); verbatim | not applied |

After these fixes, at `d0a6841`: `just check` exit 0, `All checks passed and the
worktree is unchanged.`; the Verification block above; Linux `202 compared, 0 differ`
and `50 passed` for both binaries.

### Deviations

- `.agents/skills/review-change/SKILL.md:31` lost its "(from T13)", although Files
  touched names only `AGENTS.md` and the python-change skill: the Verification line
  `rg -n 'from T13' AGENTS.md .agents` must exit 1 and cannot otherwise. One line, no
  entry added.
- The route steps' verbatim copy sits as `### Route-specific steps (from S01, route
  (a))` at the end of `## Steps` rather than inside step 4: inside the numbered list it
  broke markdownlint's MD029 for steps 5 to 11.
- The pair's comment line names this repository and T13 instead of "S01 spike"; the
  rest is S01's text.
- `wheel-smoke`'s comment gains half a line naming the new `check`.
- `test_cli.py` goes beyond the ticket's list in three places, each from a review: the
  parser-error statuses, the bounded pty read, the module-level `importorskip`.
- Phase 3 for the code-review candidates was applied by the executing agent, not a
  triage subagent (two small edits, one writer).
- The Linux runs (`/dev/full`, then the harness and `test_cli.py`) were in Docker on
  this Mac (OrbStack, aarch64), as the maintainer authorised; the CI job on
  `ubuntu-latest` (x86_64) is the first run there.

### U items

- **U16** (where `vendor_cli.py` lives): handed back to T17; scratch here.
- **U17** (`/dev/full` on Linux): closed, measured above and asserted.
- **U19**: rustqual annotations are moot under `exclude_files`; the corpus is still thin
  on multi-entity `when` (in `tests/fixtures/parity/README.md`); the upstream pull
  request's harness line is unmeasured because route (c) was not taken. Handed back.
- **U25** ("from T13" qualifiers): closed.

### Handed back outside Files touched

Stale future tense after this lane, owned elsewhere: `docs/project/purpose-and-scope.md:20`
(now false: "answers `-V` and `--version` only") and `:29`;
`docs/project/terminology.md:24, 29`; `docs/operations/maintenance.md:45` and
`docs/how-to/maintain-dependencies.md:154` (T17's runbook); `docs/decisions/0011:26`,
`0012:28, 37`; `docs/explanation/packaging.md:72`.

### Rebase onto T15 (`eb141cb`)

Before the pull request the lane was rebased onto `main` at `eb141cb` (T15 merged).
Conflicts, each resolved by keeping both lanes' lines: `AGENTS.md` (T15's fuzz sentence,
T13's dropped qualifier), `Cargo.toml` and `crates/alliumpy-core/Cargo.toml` (`divan`
beside `serde` and `serde_json`), `CHANGELOG.md` (both lines), `docs/decisions/README.md`
line 41, and `docs/reference/testing.md` (T15's sections kept under T13's Command
parity, its "T13 adds POSIX parity" paragraph and the emptied Future evidence heading
dropped). `Cargo.lock` was taken from `main` and `cargo update -p serde -p serde_json
--offline` re-added only `"serde",` and `"serde_json",` under `alliumpy-core`; T15's
separate `fuzz/Cargo.lock` path-depends on the core, so `cargo update -p alliumpy-core
--offline` in `fuzz/` added the same two lines (`Locking 0 packages`), a regenerated
lockfile outside Files touched. Then `just initialize` exit 0 (T15 changed `pixi.lock`
and `tools.txt`), and at `d9fa570` `just check` exit 0 (`All checks passed and the
worktree is unchanged.`), coverage `TOTAL ... 92.27%` lines, and `just parity` exit 0:

```text
positive control: check <corpus>/alliumpy/xmod/app/orders.allium exits 1 under the reference
202 compared, 0 differ
negative control: candidate plus one byte, check <corpus>/alliumpy/xmod/app/orders.allium: fired (stdout differs)
negative control: candidate forced to exit 0, check <corpus>/alliumpy/xmod/app/orders.allium: fired (exit status: reference 1, candidate 0)
parse diagnostics over 30 files: 1
======================== 48 passed, 2 skipped in 6.51s =========================
```

### Not done here

Step 11: push and pull request, with the `parity` job's first run, summary line and URL,
and the acceptance criterion "the `parity` CI job is green on the pull request". They
wait for the maintainer's authorisation.

## Open points

- Whether stderr joins the byte comparison, as S01 recommended or declined; the harness
  README states the answer.
- Whether `parity` should also run against an `allium` installed with `uv tool install`
  from `dist/`, so that the launcher `uv` writes is the one proved; T14's proof run
  covers `uvx`, and this is cheap to add here if the venv launcher and uv's differ.
- If the chosen route is (b), where the Windows binary comes from in T14's matrix, and
  whether `_bin/allium.exe` keeps parity on CRLF (`CONVENTIONS.md` §12 claim 18); T14
  owns the proof, this ticket owns the shim's branch.
- From T13's code review, handed back: the SIGINT case's fixed 2 s may race Python's
  startup on a slow runner (the 2 s are S01's); `.tools/parity` can enter the setup
  action's `.tools` cache if `python`'s post-job save loses a race to another job, which
  only an exclusion in `.github/actions/setup/action.yml` closes; and `run_os` never sees
  `argv[0]`, which upstream's `std::env::args()` also decodes, so an install path that is
  not UTF-8 would print a version where upstream exits 101. Each needs a change beyond
  S01's drafted text or this ticket's files.
- The Python-API case compares one diagnostic (`broken.allium`'s): every upstream file at
  `v3.6.1` parses with none. A corpus file with parser errors would widen it.
- T15's `just mutants` (weekly `mutants.yml`) runs over all of `alliumpy-core`, which
  now holds the three vendored CLI files: the run grows by their mutants, many of them
  missed by upstream's own tests. Excluding `src/cli/{main,test_plan,domain_model}.rs`
  (for example in `.cargo/mutants.toml`) is T15's or the maintainer's call; it is
  outside the gate and outside this ticket's files.
