---
id: T03
title: "Python quality gate: ruff, mypy, the stub, pytest, the smoke fixtures"
status: done
depends_on: [T00]
parallel_with: [T01, T02, T05, T07, S01]
branch: ticket/t03-python-gate
estimated_size: M
---

# T03: Python quality gate: ruff, mypy, the stub, pytest, the smoke fixtures

## Context

T00 landed the Python package, its stub, one pytest file, working copies of `ruff.toml`
and `mypy.ini`, two positive-control fixtures and the smoke fixtures, and registered six
Python gates in `just check` (`CONVENTIONS.md` §4, gates 14 to 19), green on the day. The
recipes and every pin are frozen in wave 1 (`CONVENTIONS.md` §11). This lane makes the
configuration those recipes read final and shows that each gate bites: a linter that
finds nothing to lint, a type checker that silently skips the stub, and a stubtest whose
allowlist hides everything all pass while the claim is false.

There is no P original for this lane; P has no Python source. The design is L's spike:
L `tickets/S04-bindings-and-cli.md` lines 299-440 (what was verified about pyo3,
maturin and the `abi3-py311` wheel) and lines 1005-1130 (the crate, the recipes, the
pins). Read both ranges before step 2. `CONVENTIONS.md` §9 "The T00 API" is the API this
lane tests and describes; nothing is added to it here. `CONVENTIONS.md` §12 claims 20 and
21 are this lane's to settle finally; T00 checked them first.

Tool facts this lane rests on, read from the tools' documentation on 2026-10-22 and
confirmed by the executing agent on the pinned versions (`ruff 0.17.2`, `mypy 2.4.0`,
`CONVENTIONS.md` §2): ruff lints a path passed explicitly even when `exclude` or
`extend-exclude` matches it, unless `force-exclude = true`, so `ruff.toml` must never set
`force-exclude`; mypy's `exclude` filters recursive discovery only, and `files` applies
only when no path is given on the command line, so the positive-control fixture is
checked when named; stubtest imports and executes the module it checks, its allowlist is
one entry or regular expression per line with `#` comments, and an unused allowlist
entry is an error by default. Two stubtest limits bound what the stub proves: it cannot
infer the value type behind a pyo3 attribute (a getset or member descriptor, which
typeshed's `builtins` does not model), so a stub declaring `line: str` passes; and it
reports a stub attribute absent at runtime only for module-level names, not class
attributes. It does report a runtime attribute missing from the stub, a stub-only method
and a wrong method signature. The attribute types in `_alliumpy.pyi` are therefore
pinned by the pytest cases of step 6, not by `py-stubtest`.

## Goal

`py-lint`, `py-typecheck`, `py-test` and `py-stubtest` are each green on real code and
each is shown to fail when its subject is broken; `_alliumpy.pyi` describes the built
module exactly, with docstrings, under an allowlist whose every entry has a reason beside
it; the pytest suite covers every public name `_alliumpy.pyi` and `__init__.py` declare
(`_cli.main` is T13's and is exercised by `wheel-smoke`'s `allium --version`); the smoke
fixtures are this repository's own and keep `smoke.py`'s contract; every non-default
setting in `ruff.toml` and `mypy.ini` has a comment saying why.

## Non-goals

- No new Python API: no `check`, no AST, no `analyse` (S01 and T13 decide what the CLI
  route needs; a later ticket exposes the rest). The stub describes T00's API and nothing
  more.
- No change to `_cli.py` (T13) or to `crates/alliumpy/src/lib.rs` and the core (T02). A
  discrepancy stubtest finds between the stub and the module is fixed in the stub if the
  stub is wrong, and handed to T02 if the module is: the binding's shape is
  `CONVENTIONS.md` §9's, and a change to it is a design change.
- No edit to the `Justfile`, `pyproject.toml`, `crates/alliumpy/pyproject.toml`,
  `.gitignore` or `scripts/version_check.py` (`CONVENTIONS.md` §11). A flag found wrong
  in a recipe, or a generated path found unignored, is handed back as a T00 follow-up.
- No Python dependency. pytest, ruff and mypy are pixi's; the tests import `alliumpy` and
  the standard library only.
- No `pyproject.toml` `[tool.ruff]` or `[tool.mypy]` table anywhere: both manifests are
  frozen, and the root one is pixi's (`CONVENTIONS.md` §1 fact 2). Configuration lives in
  `ruff.toml` and `mypy.ini`.
- No `--ignore-missing-stub` and no `--ignore-unused-allowlist` on stubtest: the recipe
  is frozen and passes neither, by design.

## Files touched

| Path | Class | Content |
| --- | --- | --- |
| `ruff.toml` | final | step 3 |
| `mypy.ini` | final | step 4 |
| `crates/alliumpy/python/alliumpy/__init__.py` | final | re-exports, `__all__` (the four re-exported names), `__version__`, module docstring |
| `crates/alliumpy/python/alliumpy/_alliumpy.pyi` | final | the T00 API with docstrings (`CONVENTIONS.md` §9) |
| `crates/alliumpy/tests/test_parse.py` | final | step 6 |
| `crates/alliumpy/tests/stubtest-allowlist.txt` | final | step 5 |
| `tests/fixtures/smoke/ok.allium` | final | step 2 |
| `tests/fixtures/smoke/broken.allium` | final | step 2 |
| `tests/fixtures/smoke/smoke.py` | final | T00's contract kept (`CONVENTIONS.md` §9); typed and ruff-clean |
| `tests/fixtures/py-lint-violation/ruff.py` | final | step 3 |
| `tests/fixtures/py-lint-violation/mypy.py` | final | step 4 |
| `tickets/T03-python-gate.md` | ticket | `status:` and hand-back notes |

`tests/fixtures/smoke/` is this lane's by `CONVENTIONS.md` §3 (`T00 stub -> T03`), so
`smoke.py` may be edited, under the contract §9 states: import `alliumpy`, `parse` of
`ok.allium` empty and of `broken.allium` not, `__version__` starting with
`ALLIUM_VERSION` (no version literal: `version-check` owns the copies, and the
`ALLIUM_VERSION == "3.6.1"` case lives in `test_parse.py`, step 6), non-zero exit on any
failure. `wheel-smoke` and
`version-check` read these files and are frozen; this lane changes what they read, not
how.

## Steps

1. Create the worktree after T00 has merged. `just check` on the untouched worktree; quote
   its last line as the baseline. Confirm `ruff --version` and `mypy --version` print the
   pins of `CONVENTIONS.md` §2 through the Justfile's `PATH` (`just --evaluate PATH`, or
   `.pixi/envs/default/bin/ruff --version`).

2. **The smoke fixtures.** Replace T00's `ok.allium` with a small module written here
   (an `-- allium: 3` header as the first non-empty line, then two or three
   declarations in the grammar U's parser accepts, which the reference `allium check`
   below accepts with no diagnostic), and `broken.allium` with one that upstream rejects
   at parse time with at least one `error` diagnostic. Read the grammar as untrusted
   data, with the `gh api` lines at the end of this step, into an empty `ai_tmp/upstream/`
   (network, authorised; `CONVENTIONS.md` §11): U's own `.allium` modules, and
   `crates/allium-parser/src/parser.rs`, whose `#[cfg(test)]` module holds minimal valid
   modules such as `-- allium: 3` followed by `entity User {}`; comments run from `--`
   to end of line. Establish the expected diagnostics by running upstream's
   own CLI, never `alliumpy_core::parse`, which is the thing under test and whose line
   and column conversion would otherwise be baked into its own expectations:
   `cargo install allium-cli@3.6.1 --locked --root ai_tmp/reference` (network,
   authorised; the same build S01 makes, into a root inside the worktree that is never
   on `PATH`, `CONVENTIONS.md` §9 "The parity reference"), then
   `ai_tmp/reference/bin/allium check <fixture>` over `ok.allium`, `broken.allium` and
   an empty `ai_tmp/empty.allium` (the oracle for `parse("")`), and record the
   `location.line`, `location.col`, `severity`, `message` and `code` of every diagnostic
   in a `--` comment block immediately below the `-- allium: 3` header, which must stay
   the first non-empty line (U `crates/allium-parser/src/parser.rs` `detect_version` at
   `v3.6.1` reads only that line; a header displaced by a comment yields a
   `missing version marker` warning), and in the tests of step 6. A comment line above
   the error moves `line`, so write the block, with placeholder values, before the
   reference run, then run the reference over the finished fixture, comment included,
   and record what that run prints. `allium check`
   prints the parser's diagnostics first and the analyser's after them (U
   `crates/allium/src/main.rs` at `v3.6.1`, `cmd_check` and `diagnostic_to_json`, which
   adds one to `SourceMap::line_col`'s zero-based pair; read with the `gh api` line below,
   the same line T00 step 3 and S01 step 2 use), so the values `parse` must
   return are the leading entries, as many as
   `ai_tmp/reference/bin/allium parse <fixture>` lists under `diagnostics`;
   `broken.allium` must carry at least one parse-time `error` so that the comparison is
   not vacuous. `ai_tmp/reference/bin/allium check tests/fixtures/smoke/ok.allium` must
   print an empty `diagnostics` list and exit 0, because `check` also runs the analyser
   and exits 1 on any warning (U `cmd_check`) and T13 appends this very command to
   `wheel-smoke`; `ai_tmp/reference/bin/allium check tests/fixtures/smoke/broken.allium`
   must exit 1. Quote the reference's `--version` line and both exit statuses in the
   hand-back notes. Neither
   fixture carries U text, so neither needs attribution; say so in the comment. Keep
   `smoke.py`'s contract; make the file pass `py-lint` and `py-typecheck` (mypy's
   `files` includes it, step 4), with `-I`-safe imports only.

   ```sh
   mkdir -p ai_tmp/upstream
   set -o pipefail   # bash and zsh: a failed gh api must not be hidden by base64 or the redirect
   gh api 'repos/juxt/allium-tools/git/trees/v3.6.1?recursive=1' --jq '.tree[] | select(.path | endswith(".allium")) | .path' > ai_tmp/upstream/allium-files.txt
   gh api 'repos/juxt/allium-tools/contents/<path>?ref=v3.6.1' --jq .content | base64 -d > ai_tmp/upstream/<basename>   # one per module read
   gh api 'repos/juxt/allium-tools/contents/crates/allium-parser/src/parser.rs?ref=v3.6.1' --jq .content | base64 -d > ai_tmp/upstream/parser.rs
   gh api 'repos/juxt/allium-tools/contents/crates/allium/src/main.rs?ref=v3.6.1' --jq .content | base64 -d > ai_tmp/upstream/main.rs
   for f in allium-files.txt parser.rs main.rs; do test -s "ai_tmp/upstream/$f" || { printf '%s\n' "fetch failed: $f" >&2; exit 1; }; done   # and each <basename> read
   ```

3. **`ruff.toml`.** Final, with a comment on every non-default setting:
   `target-version = "py311"` (the wheel's floor, not pixi's 3.14); `line-length = 100`
   (rustfmt's); `extend-exclude = ["tests/fixtures/py-lint-violation"]` plus any generated
   path ruff would otherwise walk (`respect-gitignore` is on by default, so `dist/`, the
   `.so` and the caches are already skipped; confirm with
   `.pixi/envs/default/bin/ruff check --show-files`);
   `force-exclude` absent, with a comment saying the positive control depends on the
   default (Context). `[lint] select = ["ALL"]`, then `ignore` entries each with a
   one-line reason; the only acceptable reasons are a rule that conflicts with the
   formatter (ruff's documented list), a rule that contradicts a house convention named
   in `CONVENTIONS.md`, and `D`-rules for the pydocstyle convention chosen
   (`[lint.pydocstyle] convention = "google"` or `"numpy"`, one, stated). A rule tripped
   only by one file, or by a file this lane may not edit (`scripts/version_check.py`,
   frozen, §11; `crates/alliumpy/python/alliumpy/_cli.py`, T13's), is never a global
   `ignore`: it goes in `[lint.per-file-ignores]` under that path, which holds: for
   `crates/alliumpy/tests/**`, `S101` (asserts are tests), `INP001` (no `__init__.py` in
   the test directory, if ruff reports it) and `PLR2004` (if the recorded positions are
   compared as integer literals); for `crates/alliumpy/python/alliumpy/_alliumpy.pyi`,
   `PYI021` (the Goal requires a docstring on every public name there, and §9 makes the
   stub the canonical description of the API); for `tests/fixtures/smoke/**`, `INP001`
   and `S101` (`smoke.py` asserts by §9's contract); for `scripts/**`, `INP001`, `T201`
   (the script prints its verdict) and `S603` or `S607` (its `allium --version`
   subprocess), each only if ruff reports it; for `_cli.py`, `T201` (the console script
   prints), if reported. Each entry has its one-line reason, and nothing else is ignored.
   In a file this lane owns, a rule right in general and wrong on one line takes
   `# noqa: RULE` with a reason on that line (T05 `fix-quality`), never an `ignore`
   entry. The hand-back notes list every `noqa` and per-file ignore; neither is handed
   back.
   `[format]` left at defaults, stated. `tests/fixtures/py-lint-violation/ruff.py`: one
   unused import (`F401`) and one line over 100 characters (`E501`), with a comment on
   each saying it is a positive control for `just py-lint` and must keep failing. Prove
   both directions: `just py-lint` green; then, in a scratch copy (`CONVENTIONS.md` §11
   "Scratch": the edit made in the worktree itself, the file saved to `ai_tmp/scratch/`
   first and copied back after, confirmed with `cmp`; never a copy of the tree, whose
   `.pixi/` and `.tools/` are not relocatable; every later "scratch copy" means this),
   remove `F401` alone, then `E501` alone, and confirm each time that the recipe fails
   with its positive-control message (the §4 control greps for both codes, because
   `select = ["ALL"]` also trips `INP001`, `D100` and the copyright-notice rule on the
   fixture, and the exit status alone would fire without them); then put one real
   violation into `crates/alliumpy/python/alliumpy/__init__.py` and confirm `just
   py-lint` fails naming the file (`CONVENTIONS.md` §12 claim 20, first half). Also
   confirm `.pixi/envs/default/bin/ruff check --show-files` lists every `.py` and `.pyi`
   under
   `crates/alliumpy/python/`, `crates/alliumpy/tests/`, `tests/fixtures/smoke/` and
   `scripts/`, and not the violation fixture: a `select` or `exclude` that drops a
   directory passes silently.

4. **`mypy.ini`.** Final: `[mypy]` with `strict = True`, `python_version = 3.11`,
   `files = crates/alliumpy/python, crates/alliumpy/tests, tests/fixtures/smoke, scripts`,
   `exclude = tests/fixtures/py-lint-violation`, `mypy_path = crates/alliumpy/python`
   (so that `import alliumpy` resolves to this worktree's `python/alliumpy/` and its
   `.pyi` first, ahead of the pixi environment's site-packages, where `py-develop`
   installed the same package; mypy reads `.py` and `.pyi` only and never the `.so`),
   `warn_unused_ignores = True`,
   `warn_unused_configs = True`, `follow_imports = normal` stated explicitly with a
   comment that `silent` or `skip` would let the stub go unchecked; no per-module
   section unless one is needed, each with a reason.
   `tests/fixtures/py-lint-violation/mypy.py`: one type error (`x: int = "a"`) and one
   call with a wrong argument type, each with the
   positive-control comment. Prove both directions as step 3 did: `just py-typecheck`
   green; the fixture with its errors removed fails the recipe; a `str` assigned to an
   `int` in `test_parse.py` fails `just py-typecheck` naming the file (`CONVENTIONS.md`
   §12 claim 20, second half). Confirm with
   `.pixi/envs/default/bin/mypy -v 2>&1 | rg alliumpy/_alliumpy.pyi`
   that the stub is what mypy read for `alliumpy._alliumpy`.

5. **The stub and stubtest.** Write `_alliumpy.pyi` final for `CONVENTIONS.md` §9's T00
   API: `parse(source: str) -> list[Diagnostic]` (as §9 writes it: pyo3's default
   `#[pyfunction]` accepts `source` by keyword, and stubtest reports a `/` the module
   does not have; `inspect.signature(alliumpy._alliumpy.parse)` in the pixi interpreter
   shows the kind), `class Diagnostic` with `@final`,
   read-only attributes `line: int`, `col: int`, `severity: str`, `message: str`,
   `code: str | None`, and the three methods whose behaviour `CONVENTIONS.md` §9 defines,
   written `def __repr__(self) -> str: ...`, `def __eq__(self, other: object, /) -> bool:
   ...` (positional-only: pyo3's comparison slot has signature `(self, value, /)`, and
   stubtest reports a stub parameter that is not) and `def __hash__(self) -> int: ...`;
   `class AlliumError(ValueError)`; `ALLIUM_VERSION: str`; `ALLIUM_VERSION_STRING: str`.
   One docstring per public name, in the convention step 3 chose. Then `just py-stubtest`
   with the allowlist holding its comment line only. For every error stubtest reports,
   decide: the stub is wrong (fix it), or the module is wrong against §9 (hand to T02,
   and record the entry in the allowlist with the T02 hand-back as its reason, to be
   removed
   when T02 lands), or the discrepancy is inherent to pyo3's generated attributes (one
   entry, one reason, naming the attribute). The allowlist stays under five entries; each
   entry is a plain name or an anchored regular expression, never one that matches the
   empty string, and each has a `#` comment on the line above giving the reason and the
   ticket that removes it. Prove it fires: in a scratch copy, delete the `col: int` line
   from the stub and confirm `just py-stubtest` fails with
   `alliumpy._alliumpy.Diagnostic.col is not present in stub`; add an entry
   `alliumpy._alliumpy.Diagnostic.col` and confirm the recipe passes, then restore the
   line and confirm the recipe fails on the now-unused entry (`CONVENTIONS.md` §12
   claim 21). Discard the copy. Do not use a wrong attribute type (`col: str`) or a
   stub-only attribute (`column: int`) as the deliberate error: neither fails, for the
   reason the Context gives.

   **Adversarial review** (`CONVENTIONS.md` §14): the smoke and stubtest design, before
   the allowlist and the fixtures are built on. Ask: whether `smoke.py` could pass against
   the worktree's `python/alliumpy/` or a stale `.so` rather than the installed wheel;
   what `wheel-smoke` does when `dist/` is empty or holds two wheels, and whether this
   lane's fixtures could mask that; whether any allowlist entry, or a regular expression
   in it, hides more than the one discrepancy its reason names; whether the ruff `select`
   or `extend-exclude` leaves a directory unlinted while the positive control still
   fires; whether mypy's `follow_imports`, `mypy_path` or an `ignore_missing_imports`
   anywhere lets `alliumpy._alliumpy` resolve to nothing and pass.

6. **The tests.** One file, `crates/alliumpy/tests/test_parse.py`, replacing T00's (the
   only test path `CONVENTIONS.md` §3 gives this lane), pytest-discoverable, typed,
   ruff-clean,
   importing `alliumpy` and the standard library only, in three sections each headed by a
   comment:
   - **Parsing**: parametrised over the two smoke fixtures, read from
     `tests/fixtures/smoke/` relative to the repository root (`pathlib.Path(__file__)`
     walked up, never the working directory); `parse` of `ok.allium` is `[]`; `parse` of
     `broken.allium` has at least one diagnostic with `severity == "error"`, and its
     diagnostics, as `(line, col, severity, message, code)` tuples, equal the values
     step 2 recorded from the reference `allium check`, in order; `parse("")` returns
     whatever step 2 recorded for the empty string, asserted; `parse` of a non-`str`
     raises `TypeError` (pyo3's conversion).
   - **`Diagnostic` and `AlliumError`**: a `Diagnostic` from `broken.allium` is frozen
     (setting `line` raises `AttributeError`), has a `repr` equal to `CONVENTIONS.md`
     §9's form built from the values step 2 recorded
     (`Diagnostic(line=..., col=..., severity='error', message=..., code=...)`, asserted
     as one string), has `line` and `col` of type `int`, `severity` and `message` of
     type `str`, and `code` a `str` or `None` (asserted with `isinstance`, since stubtest
     cannot check these), compares equal to and hashes alike with the same diagnostic
     from a second `parse` of the same source, and compares unequal to one from a
     different source (§9: `eq`, `hash`); `AlliumError` is a subclass of `ValueError`
     and can be raised and caught from Python with its message intact.
   - **Versions and `__all__`**: `ALLIUM_VERSION == "3.6.1"`;
     `alliumpy._alliumpy.ALLIUM_VERSION_STRING` (not re-exported, §9; importing the
     submodule counts as importing `alliumpy`) starts with `"allium " + ALLIUM_VERSION`;
     `__version__` starts with `ALLIUM_VERSION`
     and equals `importlib.metadata.version("alliumpy")`; `set(alliumpy.__all__) ==
     {"ALLIUM_VERSION", "AlliumError", "Diagnostic", "parse"}` (the four names T00
     step 6 re-exports; `__version__` is a dunder and not listed, and
     `ALLIUM_VERSION_STRING` is not re-exported, §9), and every name in it resolves with
     `getattr`.
   `__init__.py` final: module docstring, the re-exports, `__all__`, `__version__`.
   `just py-test` green with at least ten cases; then, in a scratch copy, swap the two
   fixture file names in `test_parse.py` and confirm it fails, so the suite is shown to
   read the fixtures.

7. **The whole gate.** `just py-lint`, `just py-typecheck`, `just py-test`,
   `just py-stubtest`, `just wheel-smoke`, `just version-check` in order, then
   `just check`.
   `wheel-smoke` now smokes this lane's fixtures through T00's `smoke.py` contract; if
   it fails on a fixture, the fixture is wrong, not the recipe.

8. `just check`, the final adversarial review, `just check` again if fixes landed, then
   commit.

   **Adversarial review** (`CONVENTIONS.md` §14): the lane's diff. Ask: which test could
   pass against a module that returns the wrong line or column (a test that asserts only
   `>= 1`, or one whose expected values were produced by the module itself rather than by
   the reference `allium check`); which `ruff.toml` ignore has no defensible reason;
   whether every allowlist
   entry's reason still holds; whether any file under `crates/alliumpy/python/`,
   `crates/alliumpy/tests/`, `tests/fixtures/smoke/` or `scripts/` escapes ruff or mypy;
   whether the evidence for `CONVENTIONS.md` §12 claims 20 and 21 proves each claim, and
   whether every attribute type the stub declares has an `isinstance` case in step 6,
   stubtest not checking them.

## Acceptance criteria

- `just py-lint`, `just py-typecheck`, `just py-test` and `just py-stubtest` are green;
  `just py-test` runs ten or more cases.
- Each of the four fails in the scratch-copy experiments of steps 3 to 6, with the output
  quoted: the positive controls with their violations removed (for `ruff.py`, `F401`
  alone and `E501` alone, each giving the positive-control message), a real violation
  in the package, a stub error, an unused allowlist entry, swapped fixtures. A failure
  counts only when the quoted output names the subject (the positive-control message,
  the violating file, `is not present in stub`, the unused-entry error, the pytest
  assertion on the fixture); `command not found`, a missing environment or any other
  wrong-reason failure is not evidence.
- `ruff check --show-files` lists every `.py` and `.pyi` under the four source roots and
  not `tests/fixtures/py-lint-violation/`; `mypy -v` shows `_alliumpy.pyi` read.
- `crates/alliumpy/tests/stubtest-allowlist.txt` has fewer than five entries, each with a
  reason and a removing ticket on the line above; none matches the empty string
  (stubtest never reports such an entry as unused, so it would hide every discrepancy
  silently).
- Every non-default setting in `ruff.toml` and `mypy.ini` has a comment saying why;
  `force-exclude` is not set in `ruff.toml` and `ignore_missing_imports` is not set in
  `mypy.ini`; a comment may name either.
- `_alliumpy.pyi` has a docstring on every public name and describes exactly
  `CONVENTIONS.md` §9's T00 API.
- `just wheel-smoke` and `just version-check` are green on the new fixtures; the
  reference's `allium check` exits 0 with no diagnostic on `ok.allium` and 1 on
  `broken.allium`.
- `just check` is green.
- The adversarial reviews in Steps ran (`CONVENTIONS.md` §14), and every valid finding is
  fixed or handed back.

## Verification

```sh
.pixi/envs/default/bin/ruff --version
.pixi/envs/default/bin/mypy --version
ai_tmp/reference/bin/allium --version; echo "exit $?"
ai_tmp/reference/bin/allium check tests/fixtures/smoke/ok.allium; echo "exit $?"       # must be 0, diagnostics []
ai_tmp/reference/bin/allium check tests/fixtures/smoke/broken.allium; echo "exit $?"   # must be 1
just py-lint
.pixi/envs/default/bin/ruff check --show-files | sort
just py-typecheck
.pixi/envs/default/bin/mypy -v 2>&1 | rg '_alliumpy\.pyi'; echo "exit $?"   # must be 0
just py-test
just py-stubtest
rg -v '^\s*(#|$)' crates/alliumpy/tests/stubtest-allowlist.txt   # every entry, none empty-matching
rg -cv '^\s*(#|$)' crates/alliumpy/tests/stubtest-allowlist.txt || echo 0   # entries, must be < 5
.pixi/envs/default/bin/python -I -c 'import re,sys; es=[l.strip() for l in open(sys.argv[1]) if l.strip() and not l.lstrip().startswith("#")]; sys.exit(1 if [e for e in es if re.fullmatch(e, "")] else 0)' crates/alliumpy/tests/stubtest-allowlist.txt; echo "exit $?"   # must be 0: no entry matches the empty string
rg -n '^\s*force-exclude\s*=' ruff.toml; echo "exit $?"            # must be 1
rg -n '^\s*ignore_missing_imports\s*[=:]' mypy.ini; echo "exit $?"  # must be 1
just wheel-smoke
just version-check
just check
```

Quote each command's output in the hand-back notes, plus each scratch-copy experiment's
failing output (steps 3 to 6), headed by the commit it ran at.

## Hand-back notes

### Evidence at `5b76af6` with uncommitted T03 changes

Implemented on `ticket/T03-python-gate`. All output below belongs to this base
commit plus the T03 diff, not to a claimed later commit. The untouched baseline at
`5b76af6` exited 0, ending:

```text
All checks passed and the worktree is unchanged.
```

The initial shell selected pixi's cargo proxy; putting rustup's bin first on PATH
resolved that environment issue. The sandbox denied the existing prek cache, so
baseline and full-gate runs used approved cache access. Python experiments used
`UV_CACHE_DIR=ai_tmp/uv-cache` (absolute) to keep installer writes in the worktree.
No frozen file, dependency, Rust API or other lane's file changed.

### Configuration and API decisions

Google pydocstyle convention; formatter settings retain defaults. The only global
ignores are COM812 (formatter trailing commas) and ISC001 (formatter string layout).
Per-file ignores, all with inline reasons in `ruff.toml`:

- `crates/alliumpy/tests/**`: S101 (test assertions), INP001 (discovered test files),
  PLR2004 (independent reference positions).
- `_alliumpy.pyi`: PYI021 (canonical API docstrings required by §9).
- `tests/fixtures/smoke/**`: INP001 (standalone script), S101 (smoke assertions).
- `scripts/**`: INP001 (standalone scripts), T201 (verdict output), S603 (fixed
  console-script subprocess, without a shell).
- `scripts/version_check.py`: PLR2004 (frozen script checks two output words).
  Step 3's general requirement to scope rules in frozen files applies to this
  existing T00 exception; moving it into global ignore would hide real violations.
- `_cli.py`: T201 (console output).

Every `noqa` in the four checked roots:

- `__init__.py`: RUF022, the exact `__all__` order is fixed by §9.
- `_alliumpy.pyi`: PYI029, §9 explicitly specifies `Diagnostic.__repr__`.
- `test_parse.py`: three PT027 exceptions, one on each standard-library
  `assertRaises`; the ticket forbids importing pytest in tests.
- `smoke.py`: S301, only a locally generated exception is unpickled (retained
  from T00).

Two precise mypy ignores deliberately cross the boundary: non-string `parse`
argument (`arg-type`) and read-only `line` assignment (`misc`); unused ignores
remain errors. No `force-exclude` or `ignore_missing_imports` setting exists.

The stub retains read-only properties and exact signatures. Added version-constant
docstrings. `inspect.signature` reports `parse(source)` and comparison
`(self, value, /)`, matching the stub's keyword acceptance and positional-only
comparison. Initial stubtest found no discrepancy. The final allowlist has zero
entries, so nothing can hide a mismatch or match an empty string. No T02 hand-back.
The 17 pytest cases use only alliumpy and standard-library imports; smoke cases
are parameterized with `unittest.TestCase.subTest`. Five separate runtime type
assertions cover descriptor types stubtest cannot infer.

### Independent reference

Read pinned L S04 lines 299–440 and 1005–1130; fetched U's module list,
`v3-lifecycle.allium`, `parser.rs` and CLI `main.rs` at `v3.6.1` into `ai_tmp/upstream/`.
Built with `cargo install allium-cli@3.6.1 --locked --root ai_tmp/reference` (exit 0).
The reference root was never on PATH. Both committed modules are original text;
comments state that they contain no upstream text and need no attribution.

```text
$ ai_tmp/reference/bin/allium --version
allium 3.6.1 (language versions: 1, 2, 3)
exit 0
$ ai_tmp/reference/bin/allium check tests/fixtures/smoke/ok.allium
diagnostics: []
exit 0
$ ai_tmp/reference/bin/allium check tests/fixtures/smoke/broken.allium
location.line: 5; location.col: 9; severity: error; code: null
message: expected declaration (entity, rule, enum, value, config, surface, actor, given, default, variant, deferred, use, open question, contract, invariant), found '?'
exit 1
$ ai_tmp/reference/bin/allium parse tests/fixtures/smoke/broken.allium
one parse diagnostic, severity Error, same message; span 360..361
exit 1
$ ai_tmp/reference/bin/allium check ai_tmp/empty.allium
location.line: 1; location.col: 1; severity: warning; code: null
message: missing version marker; expected '-- allium: 1' as the first line
exit 1
$ ai_tmp/reference/bin/allium parse ai_tmp/empty.allium
one parse diagnostic, severity Warning, same message; span 0..0
exit 0
```

The reference ran over finished fixtures including comments; parser diagnostic
counts establish which leading check entries are parser results. Expected tuples
and repr are independent reference values, never obtained from the bindings.
The initial new fixture test failed against T00's fixture at `(3, 1)` instead of
`(5, 5)`; replacing the fixture made it pass.

### Gate outputs and discovery

Outputs quoted below are the decisive lines; complete local transcripts are under
`ai_tmp/verify-*.log`. Producer exit statuses were captured before filtering.

```text
$ .pixi/envs/default/bin/ruff --version
ruff 0.17.2
exit 0
$ .pixi/envs/default/bin/mypy --version
mypy 2.4.0 (compiled: yes)
exit 0
$ just py-lint
All checks passed!
89 files already formatted
exit 0
$ just py-typecheck
Success: no issues found in 6 source files
mypy.py:2: error: Incompatible types in assignment (expression has type "str", variable has type "int") [assignment]
mypy.py:10: error: Argument 1 to "needs_integer" has incompatible type "str"; expected "int" [arg-type]
exit 0 (these two findings are the required positive control)
$ just py-test
17 passed
exit 0
$ just py-stubtest
Success: no issues found in 1 module
exit 0
$ just wheel-smoke
+ alliumpy==3.6.1
allium 3.6.1 (language versions: 1, 2, 3)
exit 0
$ just version-check
version-check: all five versions agree: 3.6.1
exit 0
$ .pixi/envs/default/bin/ruff check --show-files
crates/alliumpy/python/alliumpy/__init__.py
crates/alliumpy/python/alliumpy/_alliumpy.pyi
crates/alliumpy/python/alliumpy/_cli.py
crates/alliumpy/tests/test_parse.py
scripts/version_check.py
tests/fixtures/smoke/smoke.py
exit 0 (repository prefix omitted; also lists TOML configuration files)
$ .pixi/envs/default/bin/mypy -v
LOG:  Found source:           BuildSource(path='crates/alliumpy/python/alliumpy/_alliumpy.pyi', module='alliumpy._alliumpy', has_text=False, base_dir='/Users/scutting/.supacode/repos/alliumpy/ticket/T03-python-gate/crates/alliumpy/python', followed=False)
LOG:  Metadata fresh for alliumpy._alliumpy: file crates/alliumpy/python/alliumpy/_alliumpy.pyi
exit 0
allowlist non-comment entries: 0; empty-string regex matches: 0; validation exit 0
force-exclude assignment: absent; ignore_missing_imports assignment: absent
```

Programmatic discovery compared every `.py`/`.pyi` under all four roots against
ruff's output and rejected any positive-control path. Mypy checked all six source
files; the worktree stub was explicitly present in verbose output. No source escapes.

### Scratch-copy failures (claims 20 and 21)

Each experiment saved the original in `ai_tmp/scratch/`, edited the real worktree
file, and restored it in a `finally` block. `cmp` exited 0 for every restored file.
Complete output is in `ai_tmp/experiments.log`; decisive output follows.

```text
remove F401 alone; just py-lint:
py-lint: the positive control did not fire (exit 1 naming F401 and E501)
exit 1
remove E501 alone; just py-lint:
py-lint: the positive control did not fire (exit 1 naming F401 and E501)
exit 1
real unused import in __init__.py; just py-lint:
F401 `os` imported but unused
crates/alliumpy/python/alliumpy/__init__.py
exit 1
remove both mypy fixture errors; just py-typecheck:
py-typecheck: the positive control did not fire
exit 1
str assigned to int in test_parse.py; just py-typecheck:
crates/alliumpy/tests/test_parse.py: error: Incompatible types in assignment
exit 1
delete col property from stub; just py-stubtest:
error: alliumpy._alliumpy.Diagnostic.col is not present in stub
exit 1
add exact missing-col allowlist entry; just py-stubtest:
Success: no issues found in 1 module
exit 0
restore col with allowlist entry still present; just py-stubtest:
note: unused allowlist entry alliumpy._alliumpy.Diagnostic.col
exit 1
swap both fixture names in test_parse.py; just py-test:
TestParsing.test_fixtures (fixture='broken.allium')
AssertionError: assert [(5, 9, 'error', ...)] == []
TestParsing.test_fixtures (fixture='ok.allium')
AssertionError: assert [] == [(5, 9, 'error', ...)]
exit 1
```

Claim 20 is proved in both directions for both gates; claim 21 is proved by the
missing-property, exact-entry and unused-entry sequence. None failed because of a
missing tool or environment.

### Review checkpoints

Checkpoint 1: fresh-context Codex subagents on `gpt-6-astra`, separate conformance
and breakage lenses; separate triage subagent checked both findings. C1 valid:
filtered evidence could hide a producer failure; status-first subprocess capture
fixed it, mypy and ruff exited 0 independently. BR-1 valid: global S101/T201/INP001
could hide package violations; scoped exceptions fixed it and triage reproduced
package S101 and T201 errors. No high-severity findings; no second round required.

The recipe rebuilds into emptied dist, requires exactly one existing wheel, installs
into a fresh venv offline, and executes smoke with `-I`. Empty dist or two wheels fail
its cardinality check. Fixtures never modify import search paths; isolated imports
resolve the installed wheel. No frozen recipe fix or unignored generated path found.

Checkpoint 2: fresh-context Codex reviewers on `gpt-6-astra`, separate lenses;
separate triage. B2-01 and C2-1 valid duplicates: symmetric `(5, 5)` and `(1, 1)`
locations let swapped line/column fields pass. Triage changed only the broken
fixture's indentation and coordinate comment and the expected tuple/repr; the
independent reference on the finished fixture now gives `(5, 9)`, error, same
message, code null, exit 1; parse reports exactly one error, span 360..361, exit 1.
This distinguishes swapped fields and duplicated coordinates. All scratch
experiments and six Python/wheel gates were rerun successfully after this fix;
original files restored with `cmp`. No high-severity finding, no extra round or
hand-back needed. The conformance review's initial whole-ticket read inadvertently
included the hand-back section; it disclosed that exposure and based its finding
on source and raw evidence. The independent breakage review found the same defect.

`review-change` is this repository's review skill; applied after implementation
alongside the ticket's adversarial procedure. No frozen-file change was required.
The first full run found only unformatted `ruff.toml`; taplo fixed that file.
After triage, EditorConfig rejected six-space fixture indentation; eight spaces
now satisfy its four-space rule and the independent reference confirms `(5, 9)`.
A subsequent full run exited 0, ending with the line below. After the coordinate
fix, the complete gate is rerun before commit; any failure blocks completion.

```text
$ just check
All checks passed and the worktree is unchanged.
exit 0
```

An additional `target/wheel-smoke/venv/bin/python -I` assertion checked both
`alliumpy.__file__` and the native module's `__file__` are beneath the fresh venv:

```text
target/wheel-smoke/venv/lib/python3.14/site-packages/alliumpy/__init__.py
target/wheel-smoke/venv/lib/python3.14/site-packages/alliumpy/_alliumpy.abi3.so
exit 0 (absolute worktree prefix omitted)
```

No outstanding findings or hand-backs. Raw review, triage, reference and verification
logs remain untracked in `ai_tmp/`. The committed tree receives a final `just check`
and clean-status check; the final response identifies that tested commit.

## Open points

- Whether `Diagnostic` should expose a `to_dict()` or `__iter__` for JSON output. Not in
  §9's T00 API; if the tests want it, record the want for T13, which decides the CLI's
  JSON path, and do not add it here.
- Whether pyo3 generates attributes on `Diagnostic` (`__match_args__`, `__getstate__`)
  that stubtest expects in the stub. Each is either declared in the stub, if the module
  really has it, or allowlisted with the attribute named; never a wildcard.
- The pydocstyle convention. Recommend `google`; say so if the stub reads better under
  `numpy`.
