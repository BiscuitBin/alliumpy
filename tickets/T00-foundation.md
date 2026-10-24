---
id: T00
title: "Foundation: a shape-complete skeleton that passes `just check` and builds a wheel on its first commit"
status: open
depends_on: []
parallel_with: []
branch: ticket/t00-foundation
estimated_size: XL
---

# T00: Foundation: a shape-complete skeleton that passes `just check` and builds a wheel on its first commit

## Context

This repository (`BiscuitBin/alliumpy`, private, one `first commit` holding a stub
`README.md`, plus `tickets/`) becomes the two-crate workspace and the one wheel
`CONVENTIONS.md` §0 describes. Read `CONVENTIONS.md` in full first, then `README.md` in
this directory. §9 is the part with no original to copy; read it twice.

This is the tracer bullet: one commit that passes through every layer the foundation
has, in a valid shape, so that six lanes can then replace stubs in parallel. It has to be
one ticket because B's `bg-validate-docs` and `bg-validate-agents` walk every registered
page and every skill, `bg-project-check` snapshots the worktree between recipes, and the
wave-1 lanes may not touch the frozen files: `just check` is green only if every path
exists and every frozen file is final from the first commit.

Almost everything is a copy of P at `bf51e0d` with a stated delta. P's own foundation
ticket, P `tickets/T00-foundation.md`, is the procedure this one follows; read its Steps
and Hand-back notes for the order of work and the traps it met (the `typos` hook that
rewrote files, `codex exec` hanging on stdin, a pixi `cargo` ahead of rustup's). L's
spike, L `tickets/S04-bindings-and-cli.md` lines 299-448 and 995-1153, is the design of
the Python side and the evidence it rests on; read both ranges before step 6.

Preconditions, stated and not performed (`CONVENTIONS.md` §2): rustup with
`~/.cargo/bin/cargo` first on `PATH`, pixi 0.81.0 or newer, any just, gh. If one is
missing, stop and report it.

## Goal

A first commit on `ticket/t00-foundation` after which, in a fresh clone, `just initialize`
then `just check` are green (all twenty-two gates of `CONVENTIONS.md` §4 and
`check-clean`), and `just lint` and `just wheel-smoke` pass there under `CONVENTIONS.md`
§11's network denial, with every T00 path in `CONVENTIONS.md` §3 present: final content
for the frozen files, the dotfiles, the first-run script, the licences, the manifest, the
map, the adapters and the bridges; and a stub for every page, record, skill, root document
and working configuration a lane will replace.

The wheel tracer: `just wheel-smoke`, from an emptied `dist/`, builds exactly one wheel
named `alliumpy-3.6.1-cp311-abi3-<platform>.whl`, installs it into a fresh virtual
environment on pixi's interpreter with no network, imports `alliumpy`,
`alliumpy.parse(...)` returns an empty list for `tests/fixtures/smoke/ok.allium` and a
non-empty one for `broken.allium`, and `allium --version` prints
`allium 3.6.1 (language versions: 1, 2, 3)` with exit 0. `cargo nextest run --workspace
--exclude alliumpy` runs at least four tests, `cargo test --doc --workspace --exclude
alliumpy` runs at least one doctest, `just coverage` is at or above 90%, and
`just py-test` runs the four pytest cases of step 6.

## Non-goals

- No CLI command beyond `-V`/`--version` (S01 decides the route, T13 builds it). `_cli.py`
  answers everything else with one stderr line and exit 2 (`CONVENTIONS.md` §9).
- No Python API beyond `parse`, `Diagnostic`, `AlliumError`, `ALLIUM_VERSION` and
  `__version__` (`CONVENTIONS.md` §9, "The T00 API").
- No dependency beyond `allium-parser` and `pyo3` (`CONVENTIONS.md` §2).
- No final prose. Pages, records, skills, `AGENTS.md`, `README.md`, `CHANGELOG.md`,
  `SECURITY.md` and both crate READMEs are stubs of 40 or more real words whose first
  sentence is `This is a T00 stub; <lane> replaces it.`, then say what the file will
  contain. The word `stub` is what T11 step 6 sweeps for.
- No final Rust tool configuration beyond what the gate needs (T02), no final `ruff.toml`
  or `mypy.ini` beyond what makes the gates fire (T03), no CI beyond the one-job stub
  (T01), no repository settings (T01).
- No wave-2 recipe, file or pin (`CONVENTIONS.md` §11, "Wave 2 shares files by
  rebasing").
- No `.claude/settings.json` (`CONVENTIONS.md` §1 fact 1), no `docs/specs/`, no Allium
  skill, no `allium-skill-reference/` (`CONVENTIONS.md` §1 decision 5).
- No sdist decision (S01) and no release workflow (T14).

## Files touched

| Path | Class | Content |
| --- | --- | --- |
| `Cargo.toml` | skeleton -> T02 | `CONVENTIONS.md` §3 "The two crates": P `Cargo.toml` plus `[workspace.dependencies]` |
| `Cargo.lock` | generated | `cargo generate-lockfile` |
| `rust-toolchain.toml` | final | P `rust-toolchain.toml`, the day's stable (`CONVENTIONS.md` §2) |
| `rustfmt.toml` | working -> T02 | P `rustfmt.toml` |
| `clippy.toml` | working -> T02 | P `clippy.toml` |
| `taplo.toml` | working -> T02 | P `taplo.toml`, `CONVENTIONS.md` §5 |
| `deny.toml` | working -> T02 | P `deny.toml`; `[graph] targets` is the seven triples of decision 6 (`x86_64-unknown-linux-gnu`, `aarch64-unknown-linux-gnu`, `x86_64-unknown-linux-musl`, `aarch64-unknown-linux-musl`, `aarch64-apple-darwin`, `x86_64-apple-darwin`, `x86_64-pc-windows-msvc`); no wasm target |
| `.config/nextest.toml` | working -> T02 | P `.config/nextest.toml` |
| `rustqual.toml` | working -> T02 | P `rustqual.toml`, header naming both crates and decision 0007 (`CONVENTIONS.md` §5) |
| `tools.txt` | final in wave 1 | P `tools.txt`, `CONVENTIONS.md` §2 |
| `tools-source.txt` | final in wave 1 | P `tools-source.txt`, `CONVENTIONS.md` §2 |
| `crates/alliumpy-core/Cargo.toml` | skeleton -> T02 | `CONVENTIONS.md` §3 |
| `crates/alliumpy-core/src/lib.rs` | skeleton -> T02 | `CONVENTIONS.md` §9 "The T00 API": the constants, `Severity`, `Diagnostic`, `parse`, doctest, unit tests |
| `crates/alliumpy-core/README.md` | stub -> T12 | 40 words |
| `crates/alliumpy/Cargo.toml` | skeleton -> T02 | `CONVENTIONS.md` §3: cdylib, its own `[lints]` |
| `crates/alliumpy/pyproject.toml` | final in wave 1 | `CONVENTIONS.md` §9 "The two manifests" verbatim, plus the `[tool.pixi]` comment §9 requires |
| `crates/alliumpy/src/lib.rs` | skeleton -> T02 | the `#[pymodule]` `_alliumpy` |
| `crates/alliumpy/python/alliumpy/__init__.py` | working -> T03 | re-exports, `__version__` |
| `crates/alliumpy/python/alliumpy/_alliumpy.pyi` | working -> T03 | the T00 API, typed |
| `crates/alliumpy/python/alliumpy/py.typed` | final | empty |
| `crates/alliumpy/python/alliumpy/_cli.py` | working -> T13 | `main()`: `-V` and `--version` only (`CONVENTIONS.md` §9) |
| `crates/alliumpy/tests/test_parse.py` | working -> T03 | four cases: one per smoke fixture, one for `eq`, `hash` and `repr`, one for the version constants (step 6) |
| `crates/alliumpy/tests/stubtest-allowlist.txt` | working -> T03 | a comment line only |
| `crates/alliumpy/README.md` | stub -> T12 | 40 words; the PyPI long description |
| `crates/alliumpy/LICENSE` | final | byte-identical to the root `LICENSE` |
| `crates/alliumpy/LICENSE-allium-tools` | final | U `LICENSE` at `v3.6.1` with a header paragraph (`CONVENTIONS.md` §9 "Licences") |
| `ruff.toml` | working -> T03 | step 7 |
| `mypy.ini` | working -> T03 | step 7 |
| `scripts/version_check.py` | final in wave 1 | `CONVENTIONS.md` §9 |
| `scripts/initialize.sh` | final | P `scripts/initialize.sh` minus `install-allium` (`CONVENTIONS.md` §5) |
| `tests/fixtures/smoke/ok.allium`, `broken.allium`, `smoke.py` | working -> T03 | `CONVENTIONS.md` §9 |
| `tests/fixtures/py-lint-violation/ruff.py`, `mypy.py` | working -> T03 | `F401` and `E501`; one type error |
| `LICENSE` | final | the Apache-2.0 text, as P `LICENSE` |
| `README.md` | stub -> T12 | replaces the one-line stub |
| `CHANGELOG.md` | stub -> T12 | P `CHANGELOG.md`'s shape, one `[Unreleased]` section |
| `SECURITY.md` | stub -> T12 | 40 words |
| `AGENTS.md` | stub -> T05 | the six phrases, 300 words |
| `CLAUDE.md` | final | byte-identical to P `CLAUDE.md` |
| `.github/copilot-instructions.md` | final | byte-identical to P `.github/copilot-instructions.md` |
| `.agents/skills/<7>/SKILL.md` | stub -> T05 | final frontmatter (`CONVENTIONS.md` §7), stub body |
| `.claude/skills/<7>/SKILL.md` | final | B's `BRIDGE_BODY` (B `src/biscuit_games_tooling/validate_agents.py` line 23) with `{name}` the skill's directory name; frontmatter per `CONVENTIONS.md` §7 |
| `.codex/skills/<7>/SKILL.md` | final | B's `BRIDGE_BODY` (B `src/biscuit_games_tooling/validate_agents.py` line 23) with `{name}` the skill's directory name; frontmatter per `CONVENTIONS.md` §7 |
| `Justfile` | final in wave 1 | `CONVENTIONS.md` §4 |
| `.pre-commit-config.yaml` | final | P's, `CONVENTIONS.md` §5 |
| `.pre-commit-fix.yaml` | final | P's, plus the two ruff hooks (`CONVENTIONS.md` §5) |
| `.editorconfig` | final | P's plus the Python section (`CONVENTIONS.md` §5) |
| `.gitattributes` | final | P's minus the vendored-reference line |
| `.gitignore` | final | P's plus every generated Python path (`CONVENTIONS.md` §5) |
| `.markdownlint-cli2.jsonc` | final | P's |
| `lychee.toml` | final | P's minus the vendored-reference exclusion |
| `_typos.toml` | final | P's, `CONVENTIONS.md` §5 |
| `pyproject.toml` | final | `CONVENTIONS.md` §2 |
| `pixi.lock` | generated | `pixi lock` |
| `.github/actions/setup/action.yml` | stub -> T01 | P's, minus the allium sentence in the description and the allium clause of the `.tools` cache step's comment (`CONVENTIONS.md` §10) |
| `.github/workflows/ci.yml` | stub -> T01 | one job named `check` running `just check` |
| `docs/manifest.yml` | final in wave 1 | `CONVENTIONS.md` §6, §8 |
| `docs/README.md` | final in wave 1 | `CONVENTIONS.md` §6 |
| `docs/project/*.md`, `docs/tutorials/*.md`, `docs/how-to/*.md`, `docs/explanation/*.md`, `docs/reference/*.md`, `docs/operations/*.md` | stub -> T07 | one per manifest entry |
| `docs/decisions/README.md`, `docs/decisions/0001-*.md` to `0014-*.md` | stub -> T07 (0014 -> T13) | `CONVENTIONS.md` §8 file names and titles |
| `tickets/T00-foundation.md` | ticket | `status:` and hand-back notes |

## Steps

1. Create the worktree (`README.md`, "How to pick up a ticket") and verify the
   preconditions as L `tickets/T00-foundation.md` step 1 does (P's step 1 points there):
   `command -v rustup && command -v cargo && command -v pixi && command -v just && command -v gh`,
   `pixi --version` (0.81.0 or newer) and `rustup toolchain list`; `cargo` must resolve
   under `~/.cargo/bin`, else prefix every command with `PATH="$HOME/.cargo/bin:$PATH"`
   (`CONVENTIONS.md` §2). Stop if one is missing.

2. **The toolchain.** Read the newest stable from
   `https://static.rust-lang.org/dist/channel-rust-stable.toml` and write
   `rust-toolchain.toml` as P's, with that channel. Run `rustup toolchain install` from
   the worktree (network; authorised as one of this ticket's named installs) and confirm
   `rustup show active-toolchain` prints the pin.

3. **The workspace.** Write both crates as `CONVENTIONS.md` §3 "The two crates" and §9
   "The T00 API" describe. The conversion in `alliumpy-core::parse`: call
   `allium_parser::parse(source)`, build one `allium_parser::lexer::SourceMap` over the
   source, and for each diagnostic map `span.start` through `line_col` to one-based
   `line` and `col`, `severity` by match in a private helper function (the upstream
   `Severity` enum lives in `allium_parser::diagnostic`), `message` by clone and `code`
   by `map(str::to_owned)`; read U `crates/allium/src/main.rs` at `v3.6.1`
   (`set -o pipefail; mkdir -p ai_tmp/upstream && gh api 'repos/juxt/allium-tools/contents/crates/allium/src/main.rs?ref=v3.6.1' --jq .content | base64 -d > ai_tmp/upstream/main.rs && test -s ai_tmp/upstream/main.rs`,
   the form S01 uses: endpoint quoted, because `?` globs under zsh; `pipefail` and
   `test -s`, because a failed read otherwise exits 0 and leaves an empty file; any
   non-zero exit is a stop, `CONVENTIONS.md` §11 "Checks fail closed"; every `gh api`
   read in this ticket takes the same guards) to copy exactly how its
   `diagnostic_to_json` computes line and column, so that the numbers match the CLI's.
   Unit tests: an empty source yields no diagnostics (or whatever upstream yields for it,
   asserted, not assumed); a source with one syntax error yields a diagnostic whose
   `line` and `col` are asserted against the values upstream's CLI prints for the same
   text (read from the same `main.rs` logic, and recorded in the test's comment);
   `ALLIUM_VERSION_STRING` starts with the word
   `allium`, a space and `ALLIUM_VERSION`; one test per upstream `Severity` variant
   through the private helper (`Error`, `Warning` and `Info` each map to the matching
   `alliumpy_core::Severity`), which is what `CONVENTIONS.md` §3 means by every branch of
   the conversion and what takes `cargo nextest run` past the floor of four (nextest does
   not run doctests); a doctest on `parse`. Then `cargo generate-lockfile` (network,
   authorised: the registry index for `allium-parser` and `pyo3`) and
   `cargo fetch --locked` (network, authorised; the first line of P's `sync`), so that
   every later cargo command runs offline. Do not run clippy or any other cargo build
   here: the bindings crate compiles against whatever `python3` is on `PATH` until the
   `Justfile` exports `PYO3_PYTHON` (`CONVENTIONS.md` §1 fact 3, §4), so the first lint
   run is `just clippy` in step 5.

4. **Tool configuration.** Copy the root configuration files the table names from P,
   applying only the stated deltas. Write `tools.txt`, `tools-source.txt` and
   `pyproject.toml` (`CONVENTIONS.md` §2), then `pixi lock` and `pixi install --frozen`
   (network, authorised; `CONVENTIONS.md` §12 claim 15). The dotfiles,
   `scripts/initialize.sh` and the `pyproject.toml` comments are final here, because they
   freeze when this ticket merges:
   - Apply `CONVENTIONS.md` §5's list to each dotfile. `rg -n -i
     'pachinko|pawdoku|sudoku|allium-skill|install-allium|effects|specs|wasm'` over these
     files lists the candidates; `allium` on its own is this repository's subject and
     stays.
   - `.gitignore`: every path `CONVENTIONS.md` §5 lists, each under a comment in P's
     register; the `.claude/*` block without the `!.claude/settings.json` line; the
     `.tools/` comment reworded to name only the two tool lists. Prove the block as P's
     T00 did: `mkdir -p .claude && touch .claude/scheduled_tasks.lock`, run
     `just check-agents` later in step 10 and quote it green, then remove the file.
   - `scripts/initialize.sh`: drop the `just install-allium` line and its comment block;
     in the first comment, drop `install-allium` from the list of recipes that need the
     environment; and correct the `install-tools` comment that counts the network
     downloads (one remains).
   - Renumber every decision citation in a copied comment to `CONVENTIONS.md` §8's
     numbers (`rustqual.toml`, the `Justfile`'s `install-tools` comment,
     `tools-source.txt`), and list each in the hand-back notes.

5. **The Justfile and hooks.** Write the `Justfile` as `CONVENTIONS.md` §4 states it: P's
   text with the listed changes and no others; the Python recipes exactly as §4 prints
   them. Then `just install-tools` (network; rustqual may compile from source). Run
   `just clippy` now, before any other recipe: the Justfile's `PYO3_PYTHON` export and
   the pixi interpreter both exist from here, and the recipe carries P's `--locked`. A
   lint the stable added, or one pyo3's macro output trips, shows here. A lint the core
   trips is fixed in code or set in the workspace table with a comment for T02; a lint
   only the bindings crate trips is set in that crate's own `[lints]` table with a
   comment naming the macro (`CONVENTIONS.md` §3, §12 claims 3 and 8). `#[expect]` with
   a reason is the only allowed suppression in code. Copy both prek configurations with
   §5's deltas. Do not run `just install-hooks`: its `prek
   install` writes the hook shim into the Git directory every worktree shares, which
   P `scripts/initialize.sh` refuses to do from a secondary worktree. Run the recipe's
   other lines instead (network, authorised):

   ```sh
   .pixi/envs/default/bin/prek prepare-hooks
   .pixi/envs/default/bin/prek prepare-hooks --config .pre-commit-fix.yaml
   RUSTUP_AUTO_INSTALL=0 .pixi/envs/default/bin/prek run lychee --files README.md || true
   ```

   The last line ends in `|| true` as the recipe's `-` prefix does. The primary checkout
   installs the shim after this ticket merges (`README.md`, "How to pick up a ticket").

6. **The Python package.** Write `crates/alliumpy/pyproject.toml` as the
   `CONVENTIONS.md` §9 block verbatim, plus one comment above `[tool.maturin]` saying the
   file carries no `[tool.pixi]` table because pixi reads only the root `pyproject.toml`
   (§1 fact 2, §9); `crates/alliumpy/src/lib.rs` with the `Diagnostic` pyclass
   `#[pyclass(frozen, eq, hash)]` (the core type derives `PartialEq`, `Eq` and `Hash`,
   `CONVENTIONS.md` §9) and a `__repr__` in §9's exact form, its three `repr`s produced
   through pyo3 (`PyString::new(py, s).repr()` for the strings, the literal `None` for an
   absent `code`) so that quoting and escaping are CPython's, never a hand-written `'{}'`,
   plus `AlliumError`, a `ValueError` subclass through `create_exception!` added to the
   module (§9: no fallible path yet; the class exists so that the stub and the shape are
   in place);
   `__init__.py` (re-export `parse`, `Diagnostic`, `AlliumError`,
   `ALLIUM_VERSION` from `._alliumpy`; `__version__ =
   importlib.metadata.version("alliumpy")`; `__all__`; `ALLIUM_VERSION_STRING` stays an
   attribute of `_alliumpy` only, imported by `_cli.py` and not in `__all__`, per
   `CONVENTIONS.md` §9); `_alliumpy.pyi` describing
   exactly what the module exposes, with docstrings; `py.typed` empty; `_cli.py` as §9
   says, reading `ALLIUM_VERSION_STRING` from `._alliumpy` and never from `__version__`;
   `tests/test_parse.py` with four cases: ok fixture empty; broken fixture non-empty
   with `severity == "error"` and `line >= 1`; two `parse` calls over the broken fixture
   give equal first diagnostics with equal `hash`, and `repr` of one equals
   `f"Diagnostic(line={d.line}, col={d.col}, severity={d.severity!r}, message={d.message!r}, code={d.code!r})"`;
   `ALLIUM_VERSION == "3.6.1"` and `__version__.startswith(ALLIUM_VERSION)`;
   `tests/stubtest-allowlist.txt` holding one
   comment line that says every entry needs a reason beside it. The two licence files:
   `crates/alliumpy/LICENSE` a byte copy of the root `LICENSE`;
   `crates/alliumpy/LICENSE-allium-tools` holding a header paragraph (what it is, which
   upstream version, the URL as plain text, that the code under it arrives with the route
   S01 chooses) and then U `LICENSE` at `v3.6.1` verbatim, read with
   `set -o pipefail; gh api 'repos/juxt/allium-tools/contents/LICENSE?ref=v3.6.1' --jq .content | base64 -d > ai_tmp/upstream/LICENSE && test -s ai_tmp/upstream/LICENSE`;
   then `rg -c 'Permission is hereby granted' crates/alliumpy/LICENSE-allium-tools` must
   print `1` (an empty read would ship an empty licence in the wheel).
   Write `tests/fixtures/smoke/ok.allium` and `broken.allium` as `CONVENTIONS.md` §9
   "`wheel-smoke`, `version-check` and the fixtures" says: list U's modules with
   `gh api 'repos/juxt/allium-tools/git/trees/v3.6.1?recursive=1' --jq '.tree[] | select(.path | endswith(".allium")) | .path'`
   (network, authorised; S01 runs the same listing), read one small module with
   `set -o pipefail; gh api 'repos/juxt/allium-tools/contents/<path>?ref=v3.6.1' --jq .content | base64 -d > ai_tmp/upstream/<name>.allium && test -s ai_tmp/upstream/<name>.allium`,
   or write the smallest module U `README.md` at `v3.6.1` shows, with its header line;
   `ok.allium` must yield no diagnostic and `broken.allium` at least one `error` through
   `alliumpy_core::parse`, which is upstream's parser and the only oracle at T00; each
   with an attribution comment naming origin, version and licence (§11, "Untrusted
   material"), placed below the `-- allium: 3` header, which must stay the first non-empty
   line (U `parser.rs` `detect_version` reads only that line; a comment above it gives a
   `missing version marker` warning, T03 step 2). Both files are this repository's own
   text and every hook reads them: write them in `.editorconfig`'s layout (`[*.allium]`:
   four-space indents, LF, final newline, no trailing whitespace) and spell-clean, and add
   nothing to `_typos.toml`'s excludes, which §5 reserves for `tests/fixtures/parity/`.
   Then `just py-develop` from a shell with no pixi activation and no `VIRTUAL_ENV` or
   `CONDA_PREFIX` set (`CONVENTIONS.md` §12 claim 9), `just py-test`, `just py-stubtest`
   (claim 21).

7. **The Python gates' configuration.** `ruff.toml`: `target-version = "py311"`,
   `line-length = 100`, `extend-exclude = ["tests/fixtures/py-lint-violation"]` (and the
   generated paths), `[lint] select = ["ALL"]` with the ignores T03 will defend, each
   with a comment, and `[format]` defaults; the point at T00 is that it runs over
   `crates/alliumpy/python/`, `crates/alliumpy/tests/`, `tests/` and `scripts/` and is
   green. `mypy.ini`: `strict = True`,
   `files = crates/alliumpy/python, crates/alliumpy/tests,
   tests/fixtures/smoke, scripts`, `exclude = tests/fixtures/py-lint-violation`,
   `python_version = 3.11`, `mypy_path = crates/alliumpy/python`. The two fixtures:
   `tests/fixtures/py-lint-violation/ruff.py` carries one unused import (`F401`) and one
   line over 100 characters (`E501`), the two codes the `py-lint` control greps for
   (`CONVENTIONS.md` §4: under `select = ["ALL"]` the file also trips `INP001`, `D100`
   and the copyright-notice rule, so the exit status alone proves nothing), `mypy.py` one
   type error (`x: int = "a"`), each with a comment saying it is a positive control and
   must keep failing. `just py-lint`, `just py-typecheck` (`CONVENTIONS.md` §12 claim 20),
   then each with a violation removed as a scratch edit (for `ruff.py`, `F401` and `E501`
   in turn), which must fail the recipe with its positive-control message. A scratch edit,
   here and wherever this ticket says "scratch copy": copy the file to `ai_tmp/scratch/`,
   edit it in place in the worktree, run the recipe, quote the exit status, copy the saved
   file back and confirm with `cmp`. Never copy the tree (`.pixi/` and `.tools/` are not
   relocatable) and never `git stash` (nothing is committed until step 13).

   **Adversarial review** (`CONVENTIONS.md` §14): the files that freeze when this ticket
   merges: `rust-toolchain.toml`, the `Justfile`, both prek configurations, `tools.txt`,
   `tools-source.txt`, `pyproject.toml`, `crates/alliumpy/pyproject.toml`, both licence
   copies, `py.typed`, `scripts/version_check.py` (step 8, write it first), the dotfiles
   of step 4 and `scripts/initialize.sh`. Ask: which delta from P goes beyond
   `CONVENTIONS.md` §2, §4, §5 and §9; which recipe a lane will need changed after the
   freeze; whether `wheel-smoke` can pass on a stale wheel, two wheels, or a cached
   download; whether `py-lint` or `py-typecheck` can pass with nothing to lint; whether
   `version-check` can pass while two of its five copies disagree.

8. **The wheel tracer.** Write `scripts/version_check.py` as `CONVENTIONS.md` §9
   states it (five equal values or a message naming the two that differ, exit 1; a
   missing venv names `just wheel-smoke`), and `tests/fixtures/smoke/smoke.py` as §9.
   Run `just wheel-smoke` and quote the wheel's filename (`CONVENTIONS.md` §12 claim 1),
   then `.pixi/envs/default/bin/python -I -m zipfile -l dist/*.whl` and quote the two
   `licenses/` entries (claim 19), then `just version-check`. Then claim 1's second half
   as a scratch edit (step 7): set `version = "3.6.1.post1"` in the crate
   `pyproject.toml`, `just wheel-smoke`, confirm the filename carries `3.6.1.post1` and
   `just version-check` still passes with the crates at `3.6.1`; restore the file and
   run `just wheel-smoke` again so that `dist/` and the venv hold the `3.6.1` wheel.
   Then `just wheel-smoke` under `CONVENTIONS.md` §11's network denial with both
   negative controls (claim 14).

   **Adversarial review** (`CONVENTIONS.md` §14): the wheel tracer, before the rest of
   the tree is built on it. Ask: whether `smoke.py` could pass against the worktree's
   `python/alliumpy/` instead of the installed wheel (the `-I` and the venv's `cwd`);
   whether `allium --version`'s exit status is checked; whether a wheel built from a
   stale `.so` or a stale `target/` could pass; whether the offline run's denial was
   proved by its negative controls or passed on a warm `uv` cache.

9. **The handbook.** Write `docs/manifest.yml` from P `docs/manifest.yml`: drop the
   entries `CONVENTIONS.md` §3 lists as not carried; add `how-to/install-and-run.md` and
   `explanation/packaging.md` with the slugs §6 gives; renumber and retitle the decision
   entries as §8's table, with its slugs; keep every other entry's slug. Write
   `docs/README.md` from P `docs/README.md` (`CONVENTIONS.md` §6). Then one stub per
   manifest entry, as `CONVENTIONS.md` §6 and L `tickets/T00-foundation.md` step 10
   describe (P's step 8 points there): frontmatter equal to its manifest entry, an H1
   equal to the title, 40 or more words of real prose naming what the page will say,
   which P page it is rewritten from (or that it is new) and the owning lane, with no
   `TODO`, `TBD`, `FIXME` or lorem ipsum (B
   `src/biscuit_games_tooling/validate_docs.py` lines 33-40 rejects the markers) and no
   link, except the two index pages, because B's `_unreachable` (lines 257-267) walks
   links from `docs/README.md` and reports every page it cannot reach:
   `docs/README.md` links every other registered page and none the manifest drops (the
   "Start here" list gains `how-to/install-and-run.md`, the "Understand" list gains
   `explanation/packaging.md`, and the two specifications entries go with their
   paragraph), and the `docs/decisions/README.md` stub is P's index reshaped: the same
   opening paragraphs and a table of fourteen rows linking records 0001 to 0014 with
   §8's files and titles, 0015 to 0017 absent until their tickets. Record 0014's stub as
   §8 says.

10. **The agent contract.** `AGENTS.md` stub: the headings `CONVENTIONS.md` §7 names
    (`Project map`, `Invariants`, `Provenance`), the six phrases of §1 fact 1 each in a
    true sentence outside any `<important if>` block (the `docs/specs/` sentence as §7
    words it), the runes sentence in Provenance, 300 or more words. Seven skill stubs with
    the final frontmatter of §7 (P's for the carried five, the new descriptions for
    `rust-change` and `python-change`; each description states a trigger) and a body that
    cites `AGENTS.md` and one `just` recipe. Fourteen bridges whose body is B's
    `BRIDGE_BODY` formatted with each skill's name
    (B `src/biscuit_games_tooling/validate_agents.py` line 23) and the same frontmatter. The two adapter files copied byte-for-byte. Then
    `just check-agents`, with and without the `.claude/scheduled_tasks.lock` probe of
    step 4.

11. **The root documents and CI stub.** `README.md`, `CHANGELOG.md`, `SECURITY.md`, both
    crate READMEs as stubs; `LICENSE`. `.github/workflows/ci.yml`: P's `on:` block
    (`pull_request`, `push` to `main`, `workflow_dispatch`), `permissions: contents: read`
    and `concurrency` kept, then one job, `name: check`, using P's setup action
    (`cache-key: check`), then `just check`, so that the check name branch protection
    would require exists from the first push (`CONVENTIONS.md` §10). No `install-allium`
    step anywhere.

12. **The gate.** `git add -A` first: prek's `--all-files` walks `git ls-files`, so a
    file still untracked is never linted and gates 3 and 20 would pass over nothing (the
    runner's snapshot tolerates a staged index; it only requires that no recipe changes
    it). Then `just check`. Then the claims T00 owns first: `CONVENTIONS.md` §12 claims
    6, 13, 16 and 17. For claim 13, with `.pixi/envs/default/bin` on `PATH` as the
    Verification block sets it, run `cargo llvm-cov report --show-missing-lines` and
    confirm no `crates/alliumpy/` line is listed and the core is at or above the floor.
    For claim 6, remove the core's tests as a scratch edit (step 7) and confirm
    `cargo nextest run --workspace --exclude alliumpy --locked` fails rather than passing
    on zero tests; if it passes, record the outcome and change §4 so its nextest lines
    carry `--no-tests=fail`, through a `main` pull request before the freeze, as Open
    point 3 does for the `uv` flags; never leave `test` passing on zero tests. Run
    `just lint` under §11's denial.

    **Adversarial review** (`CONVENTIONS.md` §14): the whole tree, before step 13 commits
    it. Ask: which acceptance criterion is asserted but not shown; whether the evidence
    for `CONVENTIONS.md` §12 claims 1, 3, 6, 8, 9, 13 to 17 and 19 to 21 proves each
    claim; whether the adapters and the bridges are byte-identical to P's except the two
    descriptions §7 changes; which stub has fewer than 40 real words; what the acceptance
    criteria's grep prints; which line step 4 removed from the dotfiles that something in
    this repository, a later lane or a wave-2 ticket still needs; whether `_cli.py` or
    `version_check.py` derives one version from another.

13. **A fresh clone, offline.** Commit, clone the worktree into `ai_tmp/fresh`, and run
    `just initialize`, then `just lint`, `just py-test` and `just wheel-smoke` under
    `CONVENTIONS.md` §11's network denial, with its negative control, then `just check`
    there, so that nothing green depends on a file outside Git. Then the secondary
    worktree, with the fresh clone as its primary:
    `git -C ai_tmp/fresh worktree add ../fresh-2`, then
    `just initialize` in `ai_tmp/fresh-2`, which skips `install-hooks` there, and
    `just lint` works without a second `install-hooks`. Delete `ai_tmp/fresh` and
    `ai_tmp/fresh-2` afterwards.

## Acceptance criteria

- `just check` prints all twenty-two gates of `CONVENTIONS.md` §4 and `check-clean`,
  green, in the worktree and in the fresh clone.
- `just lint`, `just py-test` and `just wheel-smoke` pass in the fresh clone after
  `just initialize`, under `CONVENTIONS.md` §11's network denial with both
  negative-control probes failing, and `just lint` passes in the secondary worktree
  without a second `install-hooks`.
- `dist/` holds exactly one wheel after `just wheel`, named
  `alliumpy-3.6.1-cp311-abi3-<platform>.whl`, and `python -m zipfile -l` lists
  `alliumpy-3.6.1.dist-info/licenses/LICENSE` and
  `alliumpy-3.6.1.dist-info/licenses/LICENSE-allium-tools`;
  `rg -c 'Permission is hereby granted' crates/alliumpy/LICENSE-allium-tools` prints `1`.
- In the smoke venv: `python -I -c 'import alliumpy; print(alliumpy.__version__,
  alliumpy.ALLIUM_VERSION)'` prints `3.6.1 3.6.1`; `allium --version` prints
  `allium 3.6.1 (language versions: 1, 2, 3)` and exits 0; `allium check x` exits 2 with
  one stderr line naming T13.
- `just version-check` passes, and fails with a message naming the two values when
  `ALLIUM_VERSION` is changed to `3.6.2` as a scratch edit (step 7).
- `scripts/initialize.sh` does not contain `allium`, and `just check-agents` stays green
  with an untracked `.claude/scheduled_tasks.lock` present.
- `rustup show active-toolchain` prints the pin; `rust-version` matches its minor.
- `cargo nextest run --workspace --exclude alliumpy --locked` runs four or more tests;
  `cargo test --doc --workspace --exclude alliumpy --locked` runs one or more doctests;
  `just coverage` reports 90% or more and lists no `crates/alliumpy/` line.
- `just py-test` runs the four cases of step 6; `just py-stubtest` passes; `just py-lint`
  and `just py-typecheck` pass, and each fails with its positive-control message when its
  fixture's violation is removed as a scratch edit (step 7; for `py-lint`, removing
  `F401` alone and `E501` alone each fails it).
- `just check-agents` prints `Validated AGENTS.md, 2 adapters, and 7 skills.`
- `grep -rn -i 'pachinko\|pawdoku\|sudoku\|wasm\|docs/specs\|install-allium' --exclude-dir=.git --exclude-dir=tickets --exclude-dir=.pixi --exclude-dir=target --exclude-dir=.tools --exclude-dir=dist --exclude-dir=ai_tmp .`
  prints nothing (the fresh clone of step 13, which has no `ai_tmp/`, is the
  authoritative run), or only lines the hand-back notes justify (a carried record's
  "Carried from pachinko" opening and `AGENTS.md`'s `docs/specs/` sentence are two).
- Step 4's `rg` prints nothing over the dotfiles, `scripts/initialize.sh` and
  `pyproject.toml`, or only lines the hand-back notes justify.
- Every path in the Files-touched table exists; no path outside it was created.
- The adversarial reviews in Steps ran (`CONVENTIONS.md` §14), and every valid finding is
  fixed or handed back.

## Verification

Commands below that do not start with `just` run with the pixi tools first on `PATH`, as
the `Justfile` does: the block's `export` line puts them there (no cargo lives there, so
rustup's stays the compiler).

```sh
rustup show active-toolchain
export PATH="$PWD/.pixi/envs/default/bin:$PATH"   # as the Justfile's PATH export: cargo-nextest, cargo-llvm-cov and python live there
just check
cargo nextest run --workspace --exclude alliumpy --locked
cargo test --doc --workspace --exclude alliumpy --locked
cargo llvm-cov report --show-missing-lines
just py-test
just py-stubtest
just wheel-smoke; ls dist/
.pixi/envs/default/bin/python -I -m zipfile -l dist/*.whl; echo "exit $?"   # two licenses/ entries, exit 0
target/wheel-smoke/venv/bin/python -I -c 'import alliumpy; print(alliumpy.__version__, alliumpy.ALLIUM_VERSION)'
target/wheel-smoke/venv/bin/allium --version; echo "exit $?"
target/wheel-smoke/venv/bin/allium -V; echo "exit $?"
target/wheel-smoke/venv/bin/allium check x; echo "exit $?"   # must be 2
just version-check
just check-agents
touch .claude/scheduled_tasks.lock && just check-agents; echo "exit $?"; rm .claude/scheduled_tasks.lock
# macOS; on Linux, unshare -rn in place of sandbox-exec (CONVENTIONS.md §11)
deny='(version 1)(allow default)(deny network*)'
sandbox-exec -p "$deny" curl -fsS --max-time 10 https://static.rust-lang.org; echo "exit $?"
sandbox-exec -p "$deny" curl --noproxy '*' -fsS --max-time 10 https://1.1.1.1; echo "exit $?"
sandbox-exec -p "$deny" just lint; echo "exit $?"
sandbox-exec -p "$deny" just py-test; echo "exit $?"   # py-develop's maturin/uv install must not reach the network (§11)
sandbox-exec -p "$deny" just wheel-smoke; echo "exit $?"
rg -n -w 'allium' scripts/initialize.sh; echo "exit $?"   # must be 1
rg -n -i 'pachinko|pawdoku|sudoku|allium-skill|install-allium|effects|specs|wasm' .editorconfig .gitattributes .gitignore .markdownlint-cli2.jsonc lychee.toml _typos.toml scripts/initialize.sh pyproject.toml
git status --short
```

Quote each command's output in the hand-back notes, and the fresh clone's offline
`just lint`, `just wheel-smoke` and `just check`, and the secondary worktree's
`just lint`.

## Hand-back notes

Implemented the two-crate tracer, Python package, wheel/console path, twenty-two-gate
runner, tool/environment locks, CI stub, handbook and agent stubs. Evidence below was
collected on base `708d170fbec4744b7f93ab94737ab90f99cca1e1` with the uncommitted T00
implementation, before the first implementation commit. Fresh-clone evidence is recorded
separately after that commit; the ticket remains open until that proof completes.

### Pins, source facts and deviations

The newest stable channel metadata selected Rust `1.99.1`; `rust-version = "1.99"`.
The binding uses pyo3 `0.30.1`, `abi3-py311`, without `extension-module`. Both crates retain
P's lint table without relaxations. Const getters satisfy the current clippy suggestions;
`create_exception!` receives its docstring in the fourth argument; the non-exhaustive
upstream severity match needs a fallback. No macro lint allowance or fallback pin was
needed. The solved local interpreter is Python `3.14.9`; maturin is `1.15.0`, uv `0.13.5`.

Read the registry's `SourceMap::line_col` and upstream v3.6.1 `main.rs`:
coordinates are zero-based and the CLI adds one to both. The core's syntax-error test
asserts line 2, column 1 for `-- allium: 1` followed by `?`. The upstream parser produces
a missing-version warning for an empty string, so the clean test uses a versioned empty
module. Smoke fixtures retain upstream's version-header syntax and MIT attribution.

Beyond the prescribed P deltas, Python lint configuration scopes its exceptions to the
specified API order, stub documentation/representation, fixed console subprocess and
formatter conventions. Copyright headers satisfy Ruff's full rule set. The stub includes
the native module's generated `__all__` so stubtest checks the actual pyo3 surface. No
frozen recipe or manifest was weakened. All seven carried decisions retain both P and L
origin numbers; citations in Cargo comments, skills and `tools-source.txt` use this
repository's renumbered decisions.

The exact P dotfile removals were: `.gitattributes`' vendored-reference rule;
`.gitignore`'s `!.claude/settings.json` exception and obsolete pinned-binary comment;
only the vendored-reference entry from markdownlint's `ignores`, lychee's `exclude_path`
and typos' `extend-exclude`. Other exclusions remain. Python indentation, wheel/native
artifacts and caches were added; the parity-fixture typos exclusion is retained for T13.
No other dotfile line was removed. The prescribed configuration grep prints nothing.

### Owned claim outcomes

| §12 claim | Observed result |
| --- | --- |
| 1 | maturin builds `alliumpy-3.6.1-cp311-abi3-macosx_11_0_arm64.whl`; scratch `.post1` builds `alliumpy-3.6.1.post1-cp311-abi3-macosx_11_0_arm64.whl`, while Cargo stays 3.6.1. Both version checks exit 0; restored 3.6.1 wheel rebuilt. |
| 3 | `just clippy` exits 0 on both crates with P's unchanged lint table. |
| 6 | nextest runs 6 core tests, exit 0; removing the test module makes it report `no tests to run`, exit 4. Restored bytes before subsequent checks. |
| 8 | frozen/eq/hash pyo3 class builds under `forbid(unsafe_code)` and the lint table; clippy and editable build exit 0. |
| 9 | `env -u VIRTUAL_ENV -u CONDA_PREFIX just py-develop` exits 0: `Found CPython 3.14`, `Installed alliumpy-3.6.1`; recipe supplies the pixi CONDA_PREFIX. |
| 13 | coverage reports 56/56 core lines, 100.00%, exit 0, with no bindings-crate line. |
| 14 | hostname curl fails 6 and direct-IP/no-proxy curl fails 7 under the same OS network-denial policy; lint, py-test (including editable install) and wheel-smoke each exit 0 under denial. Exact prescribed offline uv flags work. |
| 15 | `pixi lock` exits 0 and locks the specified Python 3.14 tool pins for linux-64 and osx-arm64; local locked installation succeeds. |
| 16 | snapshots-check exits 0 with no snapshots or insta dependency; a staged scratch orphan `.snap` makes it fail with `unreferenced snapshot`, exit 1. Removed and unstaged the scratch file. This uses step 12's staged-tree approach rather than making an intermediate scratch commit. |
| 17 | `just metrics` exits 0, including rustqual 1.8.3 on both crates; no pyo3 finding or table exception. |
| 19 | wheel listing contains both `alliumpy-3.6.1.dist-info/licenses/LICENSE` and `alliumpy-3.6.1.dist-info/licenses/LICENSE-allium-tools`; exit 0. |
| 20 | ordinary Ruff/mypy gates exit 0; removing F401 alone, E501 alone, or mypy's deliberate type error each makes its gate exit 1 with its positive-control message. Saved bytes restored and compared. |
| 21 | stubtest imports the editable native module and passes, exit 0; deliberate `wrong_line` stub property fails, exit 1; restored stub passes. |

### Review record and handoffs

All three checkpoints used independent conformance and breakage reviewers with separate
triage, at the base revision plus the staged implementation. Reports and verdicts are in
ignored `ai_tmp/review/T00-{1,2,3}/`; they are local evidence, not shipped artifacts.

1. Freeze checkpoint: two valid medium findings restored the retained markdownlint and
   lychee exclusions. Independent triage compared repaired files to pinned P after only
   the authorized removal; equality checks exit 0. Breakage review found no defect.
2. Wheel checkpoint: no actionable implementation defect. Triage verified raw offline
   and post-release evidence and exact manifest equality with §9. Incidental Python
   bytecode in the wheel is a nonblocking packaging observation handed to T03/future
   packaging design; excluding it would require changing the frozen manifest contract.
3. Whole-tree/code review: no breakage defect; one valid low finding restored P's
   decision-index opening explanation, adapted for T07/T13. The carried P/L decision origin numbers
   were also checked against §8. Final reviewer `just check` exits 0 with
   `All checks passed and the worktree is unchanged.` No high finding required a second
   round, and no valid in-scope finding remains outstanding.

The remaining implementation belongs to the lanes already named by each stub: T02 core
and bindings, T03 Python surface, T05 agent text, T07 handbook/decisions, T13 command
parity and decision 0014, and later release/matrix verification in T14. Linux lock solve
is demonstrated; Linux/Windows runtime and release publishing remain their assigned work.

### Verification transcript excerpts

Each row quotes the material stdout/stderr from the named command and its actual exit
status. Full pre-commit control output is retained locally in
`ai_tmp/evidence/controls.txt`; full gate output in `check-worktree.txt`. Initial sandbox
cache-permission failures were rerun with approved access, without changing recipes.

| Command | Output excerpt | Exit |
| --- | --- | --- |
| `rustup show active-toolchain` | `1.99.1-aarch64-apple-darwin (overridden by .../rust-toolchain.toml)` | 0 |
| `just check` | 22 gates passed; `All checks passed and the worktree is unchanged.` | 0 |
| `cargo nextest run --workspace --exclude alliumpy --locked` | `6 tests run: 6 passed, 0 skipped` | 0 |
| `cargo test --doc --workspace --exclude alliumpy --locked` | `1 passed; 0 failed` | 0 |
| `cargo llvm-cov report --show-missing-lines` | core: `56`, missed `0`, `100.00%`; total `100.00%` | 0 |
| `just py-test` | `4 passed` | 0 |
| `just py-stubtest` | `Success: no issues found in 1 module` | 0 |
| `just py-lint` | `All checks passed!`; both expected fixture codes detected | 0 |
| `just py-typecheck` | `Success: no issues found in 6 source files`; fixture type error detected | 0 |
| `just wheel-smoke` and wheel inventory | one `alliumpy-3.6.1-cp311-abi3-macosx_11_0_arm64.whl`; smoke passes | 0 |
| `python -I -m zipfile -l dist/*.whl` | both `licenses/LICENSE` and `licenses/LICENSE-allium-tools` | 0 |
| isolated smoke-venv import | `3.6.1 3.6.1` | 0 |
| smoke-venv `allium --version` and `allium -V` | each: `allium 3.6.1 (language versions: 1, 2, 3)` | 0 each |
| smoke-venv `allium check x` | stderr: `allium: commands arrive with T13; only --version and -V are available` | 2 |
| `just version-check` | `version-check: all five versions agree: 3.6.1` | 0 |
| scratch Rust version 3.6.2, version-check | names mismatched `3.6.1` and `3.6.2` | 1 |
| `just check-agents`, ordinary and with untracked scheduled lock | each: `Validated AGENTS.md, 2 adapters, and 7 skills.` | 0 each |
| denied hostname curl | `Could not resolve host: static.rust-lang.org` | 6 |
| denied direct-IP curl | `Failed to connect to 1.1.1.1 port 443` | 7 |
| denied `just lint` | all lint hooks passed | 0 |
| denied `just py-test` | editable install succeeds; `4 passed` | 0 |
| denied `just wheel-smoke` | local release wheel built and installed; smoke passes | 0 |
| MIT `rg -c` | `1` | 0 |
| initializer `rg -n -w allium` | no output | 1 |
| prescribed dotfile/configuration `rg` | no output | 1 |
| `git status --short` before commit | only the scoped staged foundation paths and this ticket | 0 |

The acceptance grep permits the seven decision provenance sentences, this index's
explicit source attribution, and AGENTS.md's required `docs/specs/` invariant. These
explain the only retained source-project mentions outside excluded ticket/scratch paths.
The final fresh-clone acceptance grep is recorded below.

### Committed-tree proof

Pending the implementation commit and the prescribed fresh clone/secondary worktree
verification. This is an explicit remaining step, not a passing acceptance claim.

## Open points

- If pyo3 0.30.1's macro output trips lints that the bindings crate's own table cannot
  reasonably allow, say so: the maintainer may prefer pyo3 0.29.2, which L verified.
- If the newest stable's lint set forces more than a handful of table changes, say so:
  the maintainer may prefer to pin the stable P uses and bump it as a follow-up.
- If `uv venv` or `uv pip install` cannot be made to run offline with the flags §4
  gives, record the flags that do, and change §4 through a `main` pull request before
  the freeze; never leave `wheel-smoke` reaching the network.
- Whether `line_col` in `allium_parser::lexer::SourceMap` is zero-based (read its
  definition in `allium-parser`'s source in the registry cache that step 3's
  `cargo fetch --locked` filled, as `CONVENTIONS.md` §12 claim 12 does) and whether the
  CLI adds one to both: read, do not assume, and record it beside the
  unit test that asserts the numbers.
