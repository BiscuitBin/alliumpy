---
id: T13
title: "The `allium` command in the wheel: S01's decision built, with parity proved"
status: open
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

To be written by the executing agent: the route built and the letter S01 gave it; each
route-specific step as executed, with any deviation from S01's draft and why; the step 3
run before the command existed; the first green parity run with both controls; the
behaviours of step 5 with the reference's observed values beside each; the `version-check`
tightening and the claim 12 outcome as applied; what an upstream bump costs under this
route, for T17's runbook; the review record for each checkpoint (`CONVENTIONS.md` §14);
the pull request and the `parity` job's run URL.

## Open points

- Whether stderr joins the byte comparison, as S01 recommended or declined; the harness
  README states the answer.
- Whether `parity` should also run against an `allium` installed with `uv tool install`
  from `dist/`, so that the launcher `uv` writes is the one proved; T14's proof run
  covers `uvx`, and this is cheap to add here if the venv launcher and uv's differ.
- If the chosen route is (b), where the Windows binary comes from in T14's matrix, and
  whether `_bin/allium.exe` keeps parity on CRLF (`CONVENTIONS.md` §12 claim 18); T14
  owns the proof, this ticket owns the shim's branch.
