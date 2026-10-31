# Conventions for bootstrapping `alliumpy`

This document is the design every ticket under `tickets/` obeys. A ticket cites it by
section (`CONVENTIONS.md §4`) instead of restating it, and embeds exact content only where
the agent executing the ticket would otherwise have to guess. Where a ticket and this
document disagree, this document wins and the ticket is corrected. Changes to this
document go through a pull request on `main`, never through a lane branch, because every
lane reads it.

The foundation is a copy of pachinko's, adapted, and pachinko's is a copy of
libpawdoku's. Almost every file a ticket writes already exists, finished and green, in P
at the pinned commit; a ticket names that file and the delta, and the agent reads the
original. Restating P here would only give the two copies room to disagree. What is new
here, and has no original to cite, is the Python side: §9 states it in full.

## 0. What is being built, and where the sources are

`BiscuitBin/alliumpy` (**private**, on the free organisation plan; today one `first
commit` holding a stub `README.md`, plus this `tickets/` directory on `bootstrap-tickets`)
becomes one PyPI package, `alliumpy`, built from a Cargo workspace of two crates:

- **`crates/alliumpy-core`**, crate name `alliumpy-core`, an rlib with no pyo3. It
  depends on upstream's `allium-parser` at an exact pin and holds the conversion layer
  over it (byte spans to line and column, upstream diagnostics to this crate's own
  types), the version constants, and later the CLI entry (S01 decides how). It carries
  the Rust unit tests and doctests, and the coverage floor is measured here (§9).
- **`crates/alliumpy`**, crate name `alliumpy`, a pyo3 cdylib, deliberately thin: the
  `#[pymodule]`, the classes and functions that wrap `alliumpy-core`, and the Python
  package beside it (`python/alliumpy/`) with the console script `allium`. It is
  excluded from `test` and `coverage` and exercised by pytest (§4, §9).

Both are Apache-2.0 with `publish = false` (crates.io is not a target; PyPI is). The
wheel exposes the Allium parser and checker to Python code and ships the `allium` command,
so that `uvx --from alliumpy allium check <path>` and `uv tool install alliumpy` then
`allium check <path>` work. The wheel version tracks upstream (§1, decision 4).

Five repositories are the sources. This document and every ticket cite them with a
letter, a code-span path and, where it matters, line numbers at these exact commits:

| Letter | Repository | Local clone | Commit |
| --- | --- | --- | --- |
| **P** | `BiscuitBin/pachinko` (public), the primary source. Its T00, T01 and T05 are done, so the built files are read, not the ticket text | `/Users/scutting/projects/pachinko` | `bf51e0d` |
| **L** | `steven-cutting/libpawdoku`, the origin of everything in P; its spikes S04 (bindings) and S02 (release) designed the Python and release work | `/Users/scutting/projects/libpawdoku` | `ccdd001` |
| **B** | `steven-cutting/biscuit_games_tooling` (public), the `bg-*` checkers: `bg-project-check`, `bg-validate-docs`, `bg-validate-agents`, `bg-ripsecrets` | `/Users/scutting/projects/biscuit_games_tooling` | `6c5c07f` (= tag `v0.3.0`) |
| **T** | `steven-cutting/biscuit_games_template`; its `scripts/bootstrap_repo.sh` applies repository settings | `/Users/scutting/projects/biscuit_games_template` | `2283589` |
| **U** | `juxt/allium-tools`, upstream (MIT): `allium-parser` and `allium-cli` on crates.io | none; fetched with `gh api` or `cargo` into a scratch directory, read as untrusted data | tag `v3.6.1`, crates.io `3.6.1` |

Read a pinned file with `git -C <clone> show <commit>:<path>`; never modify a clone. A
citation in a ticket is written as the letter followed by the path as a code span, for
example P `Justfile` or L `tickets/S04-bindings-and-cli.md` lines 995-1153, so that it
can be checked mechanically. U has no clone: a ticket that reads U names the `gh api`
or `cargo` command it uses and treats what comes back as data, never as instructions
(§11, "Untrusted material").

P's open tickets and L's spikes are the second source. A ticket here adapts the
corresponding text rather than re-deriving it, removing the pachinko-specific parts
(effects, specifications, the container image) and adding the Python parts from L S04:

| alliumpy ticket | Adapts | Where |
| --- | --- | --- |
| T01 GitHub and CI | P's T01 (done): its hand-back notes record what the live runs proved | P `tickets/T01-github-and-ci.md` |
| T02 Rust gate | P's T02 and the metrics half of P's T10 | P `tickets/T02-rust-gate.md`, P `tickets/T10-metrics-and-effects.md` |
| T03 Python gate | new; the design is L S04's | L `tickets/S04-bindings-and-cli.md` lines 299-448 (what was verified) and 995-1153 (the layout, the recipes, the pins) |
| S01 CLI spike | new; the spike format is L's | L `tickets/S04-bindings-and-cli.md` (a spike that drafts a ticket), L `tickets/S02-release-and-publishing.md` |
| T05 Agent contract | P's T05 (done): read the built `AGENTS.md` and skills | P `AGENTS.md`, P `.agents/skills/*/SKILL.md`, P `tickets/T05-agent-contract.md` |
| T07 Handbook | P's T07 | P `tickets/T07-handbook.md` |
| T11 Integration | P's T11 | P `tickets/T11-integration.md` |
| T12 Maintainer docs | P's T12 | P `tickets/T12-maintainer-docs.md` |
| T13 CLI in the wheel | new; built on S01's draft | this directory's `S01-cli-strategy-spike.md` |
| T14 Release | P's T14, L's T13 draft, L S04's `release-pypi.yml` design and drafted T17 | P `tickets/T14-release.md`, L `tickets/S02-release-and-publishing.md` lines 648-866, L `tickets/S04-bindings-and-cli.md` lines 1563-1680 |
| T15 Mutants, bench, fuzz | P's T15 and T16, L's drafts | P `tickets/T15-mutation-testing.md`, P `tickets/T16-bench-and-fuzz.md`, L `tickets/S03-bench-fuzz-mutants.md` lines 553-911 |
| T17 Renovate | P's T17, L's T18 draft | P `tickets/T17-renovate.md`, L `tickets/S01-dependency-updates.md` lines 666-905 |

Each L spike's "What was verified, and how" section holds the evidence its draft rests
on. A ticket that adapts a draft reads that section, not just the draft.

## 1. Decisions taken with the maintainer, and the facts everything rests on

Decisions, taken on 2026-10-22:

1. **Ticket format is pachinko's.** This directory, `CONVENTIONS.md`, `README.md` with
   the index and the dependency graph, one file per ticket in P's format
   (P `tickets/README.md`, "Ticket format"), adversarial review checkpoints citing §14.
2. **One wheel.** The PyPI package `alliumpy` is a pyo3 extension module exposing the
   parser and checker, plus a console script `allium`. Users run
   `uvx --from alliumpy allium check <path>` or `uv tool install alliumpy` then
   `allium check <path>`. The PyPI names `allium` and `allium-cli` are taken by
   unrelated projects (§1 fact 10). A PEP 541 claim on `allium` is a possible later
   ticket, not in this round.
3. **The CLI strategy is decided by a spike with a parity harness** (S01): vendor
   upstream's CLI modules into `alliumpy-core`, or bundle the upstream binary built from
   crates.io as package data behind an exec shim, or an upstream pull request exposing
   `run(args)`. S01 records a decision record; T13 builds the result.
4. **The version tracks upstream.** The wheel is `3.6.1` while it wraps allium-tools
   3.6.1; packaging-only fixes are `3.6.1.postN`. `allium --version` prints upstream's
   string. Cargo cannot express `.postN`, so the version in `crates/alliumpy/pyproject.toml`
   is static, not `dynamic = ["version"]`; `just version-check` holds the copies equal
   (§9). T14 owns the release mechanics.
5. **Everything from pachinko and libpawdoku is carried except what is inapplicable.**
   Carried: pixi, prek and B's checkers behind one `just check`; the agent contract and
   house skills; the Diátaxis handbook and decision records; the full Rust gate and CI;
   the wave-2 extras (release, Renovate, mutation testing, benchmarks and fuzzing).
   **Not carried:** the container image; the Allium specification gate
   (`install-allium`, `check-specs`, `analyse-specs`, `plan-spec`, `docs/specs/`, the
   `bg-install-allium` and `bg-run-allium` scripts); the seven vendored Allium skills
   (`allium`, `distill`, `elicit`, `propagate`, `tend`, `weed`, `witness`), P's house skill
   `spec-change`, and `allium-skill-reference/`; the `effects` gate and the library/service
   split; wasm and `no_std`. This repository *builds* an `allium` binary, so a second
   pinned `allium` on `PATH` for a spec gate would shadow or be shadowed by it (§13).
6. **Wheel platforms:** Linux x86_64 and aarch64 (manylinux and musllinux), macOS arm64
   and x86_64, Windows x86_64. `abi3-py311` wheels, plus whatever free-threaded wheel
   maturin's generator emits on the day (§12 claim 4).
7. **The adversarial review procedure is P's §14,** carried into §14 below with two
   clauses changed (the sources a brief may carry, and the source deltas are measured
   against), stated there.

Facts, each verified on 2026-10-22, that shape the mechanism:

1. **B still requires the phrases `docs/specs/` and `runes` in `AGENTS.md`.** B
   `src/biscuit_games_tooling/validate_agents.py` lines 47-54 require six phrases:
   `untrusted`, `just check`, `explicit authorization`, `ai_tmp/`, `docs/specs/` and
   `runes`. This repository has no `docs/specs/` directory, so `AGENTS.md` carries a
   true sentence for each: that the Allium specifications `allium` checks live in the
   repositories that use it, not under a `docs/specs/` here; and P's honest sentence
   about runes (P `AGENTS.md`, Provenance). B's `TOLERATED` set (line 32) permits
   `.claude/settings.json` without requiring it, so it is not carried: P's only enabled
   the Allium plugin.
2. **pixi never reads a nested `pyproject.toml`.** Manifest discovery searches the
   current directory and its parents, never subdirectories, and a nested
   `pyproject.toml` without `[tool.pixi]` is an error only when a command runs from
   inside that directory (L `tickets/S04-bindings-and-cli.md`, question (b)). The root
   `pyproject.toml` stays the pixi manifest, as in P; `crates/alliumpy/pyproject.toml`
   is maturin's alone and carries no `[tool.pixi]` table, with a comment saying so.
3. **pyo3's design facts, from L S04 questions (a) and (f) and its Step 5 recipes.**
   `abi3-py311` yields one wheel per platform for every CPython from 3.11 up, plus a
   separate `cp314t` wheel for
   free-threaded 3.14; the `extension-module` feature is deprecated and maturin sets
   `PYO3_BUILD_EXTENSION_MODULE` itself; pyo3's macros compile under
   `#![forbid(unsafe_code)]`; a cdylib's own `cargo test` binary needs the loader to
   find `libpython`, so the bindings crate's tests are Python's; `panic = "unwind"` stays
   because pyo3 turns panics into exceptions; `PYO3_PYTHON` must name the pixi
   interpreter or cargo compiles against whatever `python3` is on `PATH`;
   `maturin develop` in a pixi environment needs `CONDA_PREFIX` set and finds `uv` on
   `PATH` to install with. L verified these on pyo3 0.29.2 and maturin 1.15.0; the pin
   here is newer (§2), so T00 re-checks them (§12 claim 8).
4. **A cdylib-only workspace leaves the inherited gates empty.** With the bindings crate
   excluded from `test`, `cargo nextest run` would run zero tests (nextest now fails
   on that by default, §12 claim 6), `cargo test --doc` would run nothing, and
   `cargo llvm-cov` would read 0%. Hence the two-crate shape of §0: `alliumpy-core`
   carries the tests and the floor.
5. **Upstream, from U at `v3.6.1` and crates.io** (`cargo info allium-parser@3.6.1` and
   `cargo info allium-cli@3.6.1`, both `version: 3.6.1`, `license: MIT`,
   `rust-version: unknown`). `allium-parser` is a real library: `parse(&str) ->
   ParseResult { module, diagnostics }`, `analyze`, `analyse`, the `_with_cross_module`
   and `_with_external_refs` variants, a serialisable AST, `Diagnostic { span, message,
   severity, code }` with byte-offset spans, and `lexer::SourceMap` for line and column.
   Its dependencies are `regex-lite`, `serde` and `serde_json`: no C code. `allium-cli`
   is a binary crate, `[[bin]] name = "allium"`, hand-rolled argument parsing, commands
   `check`, `analyse`, `parse`, `plan`, `model`, `help`, and `-V`/`--version` printing
   `allium 3.6.1 (language versions: 1, 2, 3)`. Multi-file cross-module context,
   file discovery, line/col JSON output, `plan` and `model` live only in that binary.
   `allium check` prints one pretty JSON object per file to stdout, exit 0 when clean, 1
   on any error or warning, 2 on no inputs. Upstream's own CI uses
   `dtolnay/rust-toolchain@stable`; there is no `rust-toolchain` file and no
   `rust-version`. The `_with_cross_module` signatures have grown between releases, and
   the README carries a pre-release notice, so the pin is exact: `allium-parser = "=3.6.1"`.
6. **The repository is public.** The maintainer made it public on 2026-10-24, during
   T01; it began private. GitHub Pages and branch protection are available to
   a private repository only on a paid plan; on the free organisation plan both are
   public-repository features. T01 reads the plan and the visibility first, hands the
   question to the maintainer as an authorisation stop, and makes `pages.yml`'s deploy
   conditional (§10, §12 claim 11). GitHub Actions minutes on a private repository are
   metered, and macOS and Windows runners cost more of them (§13). On this public
   repository, T01's first full CI run of seven Ubuntu jobs reported `total_ms: 0`
   billable.
7. **PEP 639 `license-files` globs cannot leave the project root,** which for maturin
   is `crates/alliumpy/`. T00 places this repository's Apache-2.0 text and upstream's
   MIT text with attribution under that directory so that both ship in the wheel's
   `.dist-info/licenses/` (§9). T14 asserts the wheel's contents.
8. **The toolchain pin is P's.** pyo3 `0.30.1` is the newest on crates.io (`rust-version
   1.85`), maturin `1.15.0` the newest on PyPI, crates.io and conda-forge; upstream has
   no MSRV. `rust-toolchain.toml` pins `1.99.1` as P does (§2).
9. **The Justfile is POSIX-only and the pixi platforms are `linux-64` and
   `osx-arm64`** (P `pyproject.toml`). Windows and macOS x86_64 wheels are built only by
   the release matrix (T14), never by `just check`; parity is proved on POSIX only
   (T13), and T14's rehearsal is the one Windows proof (§9).
10. **PyPI names on 2026-10-22:** `allium` is taken (an unrelated astronomy package,
    0.0.1), `allium-cli` is taken and active (an unrelated company's CLI); `alliumpy`
    returns 404 and is free. A pending trusted publisher does not reserve a name
    (L `tickets/S04-bindings-and-cli.md`, question (a), "PyPI trusted publishing"), so
    T14 checks the name again on the day (§12 claim 7).
11. **`uvx` needs `--from`** when the command name differs from the package name:
    `uvx alliumpy` would look for a command named `alliumpy`; the documented form is
    `uvx --from alliumpy allium ...`. T14 proves it (§12 claim 2).
12. **The conda-forge pins for the Python tools solve against Python 3.14** on both
    platforms, read with `pixi search` and the anaconda.org file list on 2026-10-22:
    `maturin 1.15.0` (a `noarch`-style `py311` build whose run dependency is `python`),
    `uv 0.13.5`, `pytest 9.1.1`, `ruff 0.17.2`, `mypy 2.4.0` (it has `py314` builds for
    `linux-64` and `osx-arm64`). None depends on `rust`, so the environment never gains
    a second cargo (P `docs/decisions/0011-tool-manager.md`).

## 2. Toolchain and pins

### `rust-toolchain.toml` (T00 creates it; frozen)

P `rust-toolchain.toml` at `bf51e0d`, verbatim: `channel = "1.99.1"`,
`profile = "minimal"`, `components = ["rustfmt", "clippy", "llvm-tools-preview"]`, with
P's comment. The channel is the newest stable release on the day T00 executes, read from
`https://static.rust-lang.org/dist/channel-rust-stable.toml`; on 2026-10-22 that was
still `1.99.1`. `rust-version` in `[workspace.package]` is the pin's `major.minor`.
Because P's lint table was tuned against 1.99.1, a newer pin means T00 runs `just clippy`
before freezing anything and T02 owns any lint the new stable added or renamed (§12
claim 3).

### `pyproject.toml` (the pixi manifest; T00 writes it with its final comments; frozen)

P `pyproject.toml` with these changes and no others:

- `[project] name = "alliumpy-tooling"`, and the description names alliumpy and says the
  wheel's own manifest is `crates/alliumpy/pyproject.toml`.
- `[tool.pixi.dependencies]` gains, each with a comment: `maturin = "==1.15.0"`,
  `uv = "==0.13.5"` (the installer `maturin develop` uses in a pixi environment, §1
  fact 3; also `uv venv` and `uv pip` in `wheel-smoke`), `pytest = "==9.1.1"`,
  `ruff = "==0.17.2"`, `mypy = "==2.4.0"` (`stubtest` ships inside mypy). Python stays
  `3.14.*`: it is the tooling interpreter and the `PYO3_PYTHON` the gates compile
  against; the wheel's floor is `abi3-py311` and is tested in CI on 3.11 (§10).
- The `recipes` list in `[tool.biscuit-games-tooling]` is §4's gate order.
- The comments describe this repository, not P.
- Every other pin stays as P has it (`just ==1.58.0`, `prek ==0.5.3`,
  `cargo-binstall ==1.23.0`, `cargo-nextest ==0.9.146`, `cargo-llvm-cov ==0.9.1`,
  `cargo-deny ==0.20.2`, `cargo-insta ==1.48.0`, `cargo-shear ==1.13.4`,
  `taplo ==0.10.0`, B at `v0.3.0`). Moving them is Renovate's job (T17).

`pixi.lock` is generated by `pixi lock`, committed, and never hand-edited. Pixi owns the
tools and the Python environment; rustup owns the compiler; the environment never gains
`rust`.

### `crates/alliumpy/pyproject.toml` (maturin's manifest; T00 writes it final; frozen in wave 1)

Stated in full in §9. Its `[project]` table is final at T00: `name`, `version`,
`requires-python`, `license`, `license-files`, `readme`, `classifiers`, `[project.scripts]`
and `[project.urls]`. Only wave-2 tickets edit it, as `shared, own lines` (§11): T13 if
S01's route needs a `[tool.maturin]` key, T14 for the version bump and the
`[tool.maturin.generate-ci.github]` table it reads.

### Cargo dependencies (T00 adds them; each with the decision-0004 note)

Each pin is declared once in the root `Cargo.toml` `[workspace.dependencies]` table and
consumed with `{ workspace = true }` by the member named here (§3, "The two crates").

- `crates/alliumpy-core`: `allium-parser = "=3.6.1"` (exact, §1 fact 5; the one
  exception to decision 0004's caret rule, recorded in decision 0011).
- `crates/alliumpy`: `pyo3 = { version = "0.30.1", features = ["abi3-py311"] }`
  (never `extension-module`, §1 fact 3) and the path dependency on `alliumpy-core`.
- No `serde` or `serde_json` until something needs them (cargo-shear flags an unused
  dependency); S01's prototype and T13 add `serde` (features `["derive"]`) and
  `serde_json` to `[workspace.dependencies]` at full `x.y.z` caret ranges (invariant 7),
  each with its decision-0004 note, when the vendored CLI
  (`domain_model.rs` derives `Serialize`; `main.rs` writes JSON) or `analyse` needs them.
- No dev-dependency: the bindings crate has no Rust tests (§1 fact 3), and
  `alliumpy-core`'s tests need none yet.

### `tools.txt` and `tools-source.txt` (T00 creates them; frozen in wave 1)

P `tools.txt` (`cargo-hack@0.6.45`) and P `tools-source.txt` (`rustqual@1.8.3`), each with
its comment block, verbatim except that a comment citing a decision number is renumbered
to §8's. Wave-2 tickets add their own lines (§11). The parity reference `allium` (T13) is
**not** a `tools-source.txt` line: it must never land on `PATH` (§9, "The parity
reference").

### Maintainer prerequisites (not ticket steps)

As P `tickets/CONVENTIONS.md` §2 "Maintainer prerequisites": rustup installed and its
`~/.cargo/bin/cargo` first on `PATH`; pixi 0.81.0 or newer; any just; gh authenticated
with access to `BiscuitBin`; ripgrep (`rg`) and `jq`, which the tickets' verification
commands use and no pin provides. If an agent's shell finds `~/.pixi/bin/cargo` first,
every command is prefixed `PATH="$HOME/.cargo/bin:$PATH"`. A PyPI account that can
register a pending trusted publisher is a prerequisite for T14 only.

## 3. Target repository tree (exact paths and owners)

Owner is the lane that writes the final content. T00 creates every path below that has
T00 in its row, as a stub or in final form, so that `just check` is green on the first
commit. A path that a lane creates is marked `new`; no other lane touches it. No path has
two wave-1 owners. `(frozen)` marks files no wave-1 lane touches after T00 (§11).

```text
Cargo.toml                            T00 skeleton -> T02 (lints, profiles)
Cargo.lock                            T00 (generated; two members, allium-parser and pyo3 trees)
rust-toolchain.toml                   T00 (frozen)
rustfmt.toml  clippy.toml             T00 working -> T02
taplo.toml  deny.toml                 T00 working -> T02
.config/nextest.toml                  T00 working -> T02
rustqual.toml                         T00 working (header renumbered to decision 0007) -> T02
tools.txt  tools-source.txt           T00 (frozen in wave 1)
crates/alliumpy-core/Cargo.toml       T00 -> T02
crates/alliumpy-core/src/lib.rs       T00 (the conversion layer, the constants, tests) -> T02
crates/alliumpy-core/README.md        T00 stub -> T12
crates/alliumpy/Cargo.toml            T00 (its own [lints] table) -> T02
crates/alliumpy/pyproject.toml        T00 (frozen in wave 1)
crates/alliumpy/src/lib.rs            T00 (the #[pymodule]) -> T02
crates/alliumpy/python/alliumpy/__init__.py    T00 -> T03
crates/alliumpy/python/alliumpy/_alliumpy.pyi  T00 working -> T03
crates/alliumpy/python/alliumpy/py.typed       T00 (empty; frozen)
crates/alliumpy/python/alliumpy/_cli.py        T00 working (--version only) -> T13
crates/alliumpy/tests/test_parse.py   T00 (four cases) -> T03
crates/alliumpy/tests/stubtest-allowlist.txt   T00 (empty but for its comment) -> T03
crates/alliumpy/README.md             T00 stub -> T12 (the PyPI long description)
crates/alliumpy/LICENSE               T00 (this repository's Apache-2.0 text; frozen)
crates/alliumpy/LICENSE-allium-tools  T00 (U's MIT text and attribution; frozen in wave 1; T13 edits the header, shared)
ruff.toml                             T00 working -> T03
mypy.ini                              T00 working -> T03
scripts/version_check.py              T00 (frozen in wave 1; T13 tightens it, shared)
scripts/initialize.sh                 T00 (frozen)
tests/fixtures/smoke/                 T00 stub (ok.allium, broken.allium, smoke.py) -> T03
tests/fixtures/py-lint-violation/     T00 (ruff.py, mypy.py: the positive controls) -> T03
tests/fixtures/parity/                T13 new (U's corpus, with attribution)
tests/parity/                         T13 new (the harness; never beside the corpus)
LICENSE                               T00 (Apache-2.0 text, final)
README.md  CHANGELOG.md  SECURITY.md  T00 stub -> T12
AGENTS.md                             T00 stub (six phrases, 300 words) -> T05
CLAUDE.md  .github/copilot-instructions.md   T00 (byte-identical to P; frozen)
.agents/skills/<7>/SKILL.md           T00 stub -> T05
.claude/skills/<7>/SKILL.md  .codex/skills/<7>/SKILL.md   T00 (fixed bridge body; frozen)
Justfile                              T00 (frozen in wave 1)
.pre-commit-config.yaml  .pre-commit-fix.yaml   T00 (frozen)
.editorconfig  .gitattributes  .gitignore   T00 (frozen)
.markdownlint-cli2.jsonc  lychee.toml  _typos.toml   T00 (frozen)
pyproject.toml                        T00 (frozen)
pixi.lock                             T00 (generated; frozen in wave 1)
.github/actions/setup/action.yml      T00 stub -> T01
.github/workflows/ci.yml              T00 one-job stub -> T01
.github/workflows/audit.yml  .github/workflows/pages.yml   T01 new
.github/workflows/release-pypi.yml    T14 new
.github/workflows/mutants.yml  .github/workflows/fuzz.yml   T15 new
fuzz/                                 T15 new
crates/alliumpy-core/benches/         T15 new
.cargo/mutants.toml                   T15 new (only if a mutant is equivalent)
renovate.json                         T17 new
docs/how-to/release.md                T14 new
docs/how-to/bump-upstream.md          T17 new
docs/decisions/0015..0017-*.md        T14, T15, T17 new (one each)
docs/manifest.yml  docs/README.md     T00 (frozen in wave 1)
docs/project/*.md                     T00 stub -> T07
docs/tutorials/first-change.md        T00 stub -> T07
docs/how-to/*.md                      T00 stub -> T07
docs/explanation/*.md                 T00 stub -> T07
docs/reference/*.md  docs/operations/*.md   T00 stub -> T07
docs/decisions/README.md  docs/decisions/0001..0014-*.md   T00 stub -> T07 (0014 -> T13)
tickets/                              this directory
ai_tmp/  .tools/  .pixi/  target/  dist/   gitignored; never committed
```

Not carried from P: `crates/libpachinko/**`, `crates/pachinko/**`,
`scripts/check-effects.sh` (and the `tests/fixtures/effects-violation/` P's T10 would
add), `docs/specs/`, `docs/how-to/work-with-the-specs.md`,
`docs/explanation/specifications.md`, the seven
Allium skills and `spec-change` with their sixteen bridges, `allium-skill-reference/`,
`.claude/settings.json`, P's decisions 0001, 0002, 0003, 0005, 0008, 0010 and 0014, and
every snapshot.

Wave 2 creates paths of its own; each wave-2 ticket lists them.

### The two crates (T00 writes them; T02 finishes them)

Root `Cargo.toml` is P `Cargo.toml` with: `version = "3.6.1"` added to
`[workspace.package]` (the key `scripts/version_check.py` reads, §9; both crates inherit
it); `repository` and `homepage` set to `https://github.com/BiscuitBin/alliumpy`;
`rust-version` per §2; a `[workspace.dependencies]` table holding
`allium-parser = "=3.6.1"` and `pyo3 = { version = "0.30.1", features = ["abi3-py311"] }`
so that each pin is written once; the `module_name_repetitions` comment reworded;
`[profile.release]` keeps `lto = "fat"` and `codegen-units = 1` and keeps `panic` at its
default, `unwind`, with L's comment that pyo3 needs it (L `Cargo.toml`). T00 lands the
full lint table at once, because `-D warnings` is decided by it and a skeleton with fewer
lints would only move the failures into T02.

`crates/alliumpy-core/Cargo.toml`: P `crates/libpachinko/Cargo.toml`'s package shape,
every inherited field `.workspace = true` including `version.workspace = true` in place
of P's literal `version`, `name = "alliumpy-core"`, `lib.name = "alliumpy_core"`, a
`description`, `keywords`, `categories` and `readme` (P's package shape, kept for rustdoc
and the manifest's readers; clippy's `cargo_common_metadata` skips a `publish = false`
crate, so no lint requires them), `[lints] workspace = true`, one dependency:
`allium-parser = { workspace = true }`. `src/lib.rs` (T00's content, §9 "The T00 API"):
the crate docs; `pub const ALLIUM_VERSION: &str = "3.6.1"`, the upstream version this
crate wraps; `pub const ALLIUM_VERSION_STRING: &str`, what `allium --version` prints
(§9); `Severity`, `Diagnostic` and `parse(source: &str) -> Vec<Diagnostic>`, each
documented, with a doctest and in-module unit tests covering every branch of the
conversion, so that every gate has something to format, lint, test, document and measure.

`crates/alliumpy/Cargo.toml`: the same package shape, `name = "alliumpy"`,
`[lib] crate-type = ["cdylib"]`, dependencies `alliumpy-core = { path =
"../alliumpy-core", version = "3.6.1" }` and `pyo3 = { workspace = true }`, and its own
`[lints]` table instead of `workspace = true`: a copy of the workspace table with
`unsafe_code = "forbid"` kept, and any lint pyo3's macro output trips set to `allow`
with a comment naming the macro and the reason, which T02 settles (§12 claim 8). L's
reasoning: a member cannot lower a workspace `forbid`, and a bindings crate whose macro
output trips a workspace lint declares its own table rather than weakening everyone's
(L `tickets/S04-bindings-and-cli.md`, Context). `src/lib.rs`: the `#[pymodule]`
`_alliumpy`, exposing `parse`, a `Diagnostic` class, the exception `AlliumError` (§9),
`ALLIUM_VERSION` and `ALLIUM_VERSION_STRING`, every class `#[pyclass(frozen, eq, hash)]`
and `Send + Sync` by construction, with a hand-written `__repr__` (§9), every error
mapped through `Display` (§9). No Rust test in this crate.

Package versions: both crates' `version` is `3.6.1`, equal to the wheel's version with
`.postN` stripped (decision 4; `just version-check`).

## 4. `Justfile` (T00 writes it; frozen in wave 1)

P `Justfile` at `bf51e0d`, with exactly these changes:

- The header comment no longer mentions the Allium checker; it says that `.tools/bin`
  holds what conda-forge lacks and nothing else.
- A new line after the `PATH` export:
  `export PYO3_PYTHON := justfile_directory() / ".pixi" / "envs" / "default" / "bin" / "python"`,
  with a comment: every cargo invocation compiles `crates/alliumpy` against the pixi
  interpreter, never a system Python older than the `abi3-py311` floor (§1 fact 3).
- The `coverage_floor` comment reads "over crates/alliumpy-core/src/**" (still `"90"`).
- `install-allium` is deleted, with its comment. `check-specs`, `analyse-specs` and
  `plan-spec` are deleted, with their comments. `effects` is deleted, with its comment.
- `test`, `test-doc`, `snapshots-check` and `snapshots-accept` gain
  `--exclude alliumpy` after `--workspace` on every cargo line (`cargo insta test`
  forwards it to nextest). The comment on `test` says why: the cdylib's own test binary
  would need `libpython` at load time, and its tests are Python's (§1 fact 3).
- `coverage`: the `llvm-cov nextest` line reads `-p alliumpy-core` in place of
  `--workspace`; the two `report` lines are unchanged. The comment says the floor
  measures the core, because the bindings crate's lines are exercised by pytest, which
  llvm-cov does not see (§9).
- `metrics` runs rustqual once per crate: `rustqual crates/alliumpy-core …` and
  `rustqual crates/alliumpy …`, each with `--config rustqual.toml --fail-on-warnings
  --format github`. The sentence about gate 8 goes.
- `site` writes a root `index.html` that links to both crates' pages
  (`alliumpy_core/index.html` and `alliumpy/index.html`), with the title
  "alliumpy: API reference".
- New recipes, in a new section `# ---- python ---` after `# ---- documents ---` and
  before `# ---- aggregate ---`, each with a comment in P's register:

  ```just
  # Builds the extension into the pixi environment in place (the .so beside
  # __init__.py, gitignored). maturin needs an environment to install into and
  # finds the pixi one through CONDA_PREFIX, set on this line alone; it installs
  # with the pinned uv on PATH. `locked = true` in crates/alliumpy/pyproject.toml
  # makes it honour Cargo.lock. Not a gate: py-test and py-stubtest depend on it.
  py-develop:
      CONDA_PREFIX="{{ justfile_directory() }}/.pixi/envs/default" maturin develop --manifest-path crates/alliumpy/Cargo.toml

  # Gate: ruff over every Python file ruff.toml names; --show-files must list
  # the package, or an exclude has emptied the gate (ruff exits 0 on no files);
  # then the positive control: the fixture must fail with exit status 1
  # (violations found) and the output must name F401 and E501, the fixture's
  # own violations: under select = ALL the file also trips INP001, D100 and
  # the copyright-notice rule, so the exit status alone would fire with F and
  # E dropped. Exit 2
  # is a tool or usage error, not a fired control; a missing fixture is E902
  # with exit 1, so it is tested first.
  py-lint:
      ruff check .
      ruff format --check .
      ruff check --show-files . | grep -q 'crates/alliumpy/python/alliumpy/__init__\.py$' || { printf '%s\n' 'py-lint: ruff did not see the package' >&2; exit 1; }
      test -f tests/fixtures/py-lint-violation/ruff.py || { printf '%s\n' 'py-lint: the positive control fixture is missing' >&2; exit 1; }
      status=0; out=$(ruff check --quiet --output-format concise tests/fixtures/py-lint-violation/ruff.py) || status=$?; [ "$status" -eq 1 ] && printf '%s\n' "$out" | grep -q ': F401 ' && printf '%s\n' "$out" | grep -q ': E501 ' || { printf '%s\n' "$out" 'py-lint: the positive control did not fire (exit 1 naming F401 and E501)' >&2; exit 1; }

  # Gate: mypy over the files mypy.ini names (the stub, the package, the tests,
  # scripts/), then the positive control: the fixture must fail with exit status
  # 1 (type errors). Exit 2 is a usage or I/O error, not a fired control, and the
  # one error line stays visible for the hand-back (CONVENTIONS.md §11). stubtest,
  # which imports the built module, is py-stubtest.
  py-typecheck:
      mypy
      status=0; mypy --no-error-summary tests/fixtures/py-lint-violation/mypy.py || status=$?; [ "$status" -eq 1 ] || { printf '%s\n' 'py-typecheck: the positive control did not fire' >&2; exit 1; }

  # Gate: the binding's behaviour tests, against the extension py-develop built.
  py-test: py-develop
      python -m pytest crates/alliumpy/tests

  # Gate: the stub file describes the built module exactly. The allowlist is
  # reviewed in T03 and must stay short; an entry hides a discrepancy.
  py-stubtest: py-develop
      python -m mypy.stubtest alliumpy._alliumpy --allowlist crates/alliumpy/tests/stubtest-allowlist.txt

  # The release wheel for this platform into dist/, which is emptied first so a
  # stale wheel can never be smoked. A release build on every `just check` is
  # the price of smoking the artefact the release ships (CONVENTIONS.md §9).
  wheel:
      rm -rf dist
      maturin build --release --manifest-path crates/alliumpy/Cargo.toml --out dist

  # Gate: the wheel installs and works in a fresh virtual environment, offline.
  # Exactly one wheel, which must exist (an unmatched glob is one literal argument);
  # a venv on the pixi interpreter with no download; install
  # from dist/ alone; then import, parse the smoke fixtures, and run the console
  # script. Python runs with -I so nothing in the worktree shadows the package.
  wheel-smoke: wheel
      #!/bin/sh
      set -eu
      set -- dist/*.whl
      [ "$#" -eq 1 ] && [ -f "$1" ] || { printf 'wheel-smoke: expected one wheel in dist/, found: %s\n' "$*" >&2; exit 1; }
      rm -rf target/wheel-smoke
      uv venv --python .pixi/envs/default/bin/python --no-python-downloads --offline target/wheel-smoke/venv
      uv pip install --python target/wheel-smoke/venv --offline --no-index --no-deps "$1"
      target/wheel-smoke/venv/bin/python -I tests/fixtures/smoke/smoke.py
      target/wheel-smoke/venv/bin/allium --version

  # Gate: one version, in every place it is written (CONVENTIONS.md §9). Reads
  # the Cargo manifests, the wheel manifest and the console script's own output
  # from the venv wheel-smoke left; fails if that venv is missing.
  version-check:
      python -I scripts/version_check.py
  ```

- The `install-tools` comment's `decision 0012` becomes `decision 0007` (§5, §8).
- The `snapshots-check` comment's `Gate 19` becomes `Gate 22`, its place in the gate order
  below (`metrics`'s `Gate 7` already matches).
- No other recipe changes. `snapshots-review`, `install-tools`'s two passes, `audit`,
  `check-links-online` and `check-clean` are otherwise P's text.

**Gate order** (the `recipes` list in `pyproject.toml`), then `check-clean`:

1. `check-toolchain`
2. `lock-check`
3. `lint`
4. `fmt-check`
5. `toml-check`
6. `clippy`
7. `metrics`
8. `features`
9. `test-doc`
10. `coverage`
11. `doc`
12. `deny`
13. `deps-unused`
14. `py-lint`
15. `py-typecheck`
16. `py-test`
17. `py-stubtest`
18. `wheel-smoke`
19. `version-check`
20. `check-docs`
21. `check-agents`
22. `snapshots-check`

`test`, `build`, `audit`, `site`, `py-develop`, `wheel` and `check-links-online` are
outside `check` (`wheel` runs inside `wheel-smoke`). Wave 2 adds recipes outside `check`
only (§11): `parity` and `install-parity-reference` (T13), `mutants`, `bench`, `fuzz`
and `fuzz-build` (T15); T15 also adds the fuzz crate's `--manifest-path fuzz/Cargo.toml`
line to `lock-check`, `fmt-check` and `clippy` (§11).

Cost, stated so that no agent optimises it away: gates 16 to 19 build the extension
twice per `just check` (a debug build into the pixi environment, a release build into
`dist/`). The release build carries `lto = "fat"`; if it dominates `just check`'s time,
T02's open point on the release profile is where that is weighed, and the `wheel`
recipe's `--release` is never dropped from `check`, because the wheel the gate smokes
must be the wheel the release ships.

## 5. Hooks and dotfiles

`.pre-commit-config.yaml` and `.pre-commit-fix.yaml` are P's at `bf51e0d` with these
deltas, and both are frozen at T00:

- The `exclude:` block drops `allium-skill-reference/` and gains `dist/`,
  `target/wheel-smoke/` (the latter is under `target/`, already excluded; listed for the
  reader) and `tests/fixtures/parity/.*\.allium$`: T13 commits upstream's corpus byte for
  byte, so editorconfig-checker, the whitespace fixers and the builtin checks must neither
  report nor repair it, while the corpus `README.md` stays checked. `.editorconfig` needs
  no entry: the hook never sees those files.
- The `check-specs` and `analyse-specs` local hooks are deleted with their comment
  block. The `validate-agents` hook's `files:` pattern drops `skills-lock\.json$`.
- Two new local hooks after `deps-unused`, through `just` for the reason the Rust hooks
  give: `py-lint` (`entry: just py-lint`, `files: ^(.*\.pyi?|ruff\.toml)$`) and
  `py-typecheck` (`entry: just py-typecheck`, `files: ^(.*\.pyi?|mypy\.ini)$`). `py-test`,
  `py-stubtest` and `wheel-smoke` are deliberately not hooks, as clippy is not: a build
  blocks every commit.
- In `.pre-commit-fix.yaml`, a `ruff format` hook and a `ruff check --fix` hook, through
  `.pixi/envs/default/bin/ruff`, beside `cargo fmt` and `taplo fmt`. That file's
  `exclude:` block alone also gains `tests/fixtures/py-lint-violation/`: prek passes
  filenames, and ruff repairs a named file whatever `ruff.toml` excludes (T03 keeps
  `force-exclude` unset), so without it `just fix` would strip the positive controls
  and the next `just py-lint` would fail.

`.editorconfig`, `.gitattributes`, `.gitignore`, `.markdownlint-cli2.jsonc`,
`lychee.toml`, `_typos.toml` and `taplo.toml` are P's at `bf51e0d`. T00 copies them, then
adjusts (T00 step 4):

- `.editorconfig` gains `[*.{py,pyi}]` with `indent_size = 4` (L `.editorconfig` has the
  Python section P dropped) and `[*.allium]` stays for the fixtures.
- `.gitattributes` drops the `allium-skill-reference/**` line.
- `.gitignore` ignores, up front, every generated path a later lane would otherwise
  need to add to a frozen file (§11): `dist/`, `crates/alliumpy/python/alliumpy/*.so`,
  `crates/alliumpy/python/alliumpy/*.pyd`, `__pycache__/`, `*.py[cod]`,
  `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `.venv/`, and keeps P's lines
  (`ai_tmp/`, `.pixi/`, `.tools/`, `target/`, the `.claude/*` block without the
  `!.claude/settings.json` exception, `mutants.out*/` with the comment naming T15, the
  snapshot files, `*.profraw`, `lcov.info`); the `.tools/` comment drops its sentence
  about the allium binary and `just install-allium`. The fuzz artefacts are T15's own
  lines.
- `.markdownlint-cli2.jsonc` keeps P's `MD033` `allowed_elements` of
  `["br", "important"]` for the `<important if>` blocks (§7) and drops
  `allium-skill-reference` from `ignores`.
- `_typos.toml` drops the `allium-skill-reference` exclusion, keeps `mis` and `als`
  under P's comments, and adds `tests/fixtures/parity/` to the excludes so that
  upstream's corpus is never spell-checked.
- T00 renumbers every decision citation inside a copied comment (`rustqual.toml`'s
  header, the `install-tools` comment in the `Justfile`, `tools-source.txt`) to §8's
  numbers; P's T00 hand-back records the same kind of edit.
- `lychee.toml` drops the vendored-reference exclusion.
- `taplo.toml` adds `crates/alliumpy/pyproject.toml` and the root `pyproject.toml` to
  what it formats, if P's glob does not already cover them (it formats `**/*.toml`;
  T00 confirms), and `tests/fixtures/**` to its excludes. `taplo.toml` is T02's; the
  other six are final at T00.

`just initialize` never formats (P `scripts/initialize.sh`). T00 drops its
`just install-allium` line and the comment above it, drops `install-allium` from the
first comment's list of recipes, and corrects the sentence in the `install-tools` comment
that counts the network downloads (one, not two).

## 6. Handbook

The Diátaxis handbook under `docs/`, under the documentation contract L ships
(L `docs/reference/documentation-contract.md` at `ccdd001`; P's page at `bf51e0d` is a
stub that defers to it). P's handbook pages and decision records at `bf51e0d` are all
stubs, so where this table and T07 say "P's", the original to read is L's finished page
of the same path at `ccdd001`, which P carried. `docs/manifest.yml` and `docs/README.md`
are final at T00 and frozen in wave 1. T00 writes the manifest as P `docs/manifest.yml`
minus the entries for the dropped pages and records, plus the new pages below, with the
decision records renumbered and retitled as §8 lists, in this order: P's grouping, then
decisions last. Each registered page has a stub at T00 with valid frontmatter equal to
its manifest entry, a matching H1 and at least 40 words of real prose naming what the
page will say and which lane writes it. Carried pages keep P's `canonical_for` slugs.
B's validator accepts the kinds `project`, `tutorial`, `how-to`, `explanation`,
`reference`, `operations` and `decision` and the audiences `user`, `contributor`,
`maintainer`, `operator` and `agent` only (B `src/biscuit_games_tooling/validate_docs.py`
lines 20-29).

| Path | Owner | From P | Adaptation |
| --- | --- | --- | --- |
| `docs/README.md` | T00 | same | A map for a two-crate workspace that ships one wheel; the "Start here" list gains the install how-to and "Understand" gains `explanation/packaging.md`; the two specifications list entries go with their paragraph; no specifications paragraph; every registered page stays reachable from it (B walks links from this page), the decision records through `decisions/README.md`, which T00 writes as P's index with fourteen rows |
| `docs/project/purpose-and-scope.md` | T07 | same | What the wheel is for (the CLI for `uv` users, the bindings for Python code), what it is not (not upstream, not a fork: the parser is upstream's, the CLI's behaviour is upstream's), who consumes it |
| `docs/project/repository-map.md` | T07 | same | The tree of §3 |
| `docs/project/terminology.md` | T07 | same | The glossary seed: repository, core crate, bindings crate, wheel, sdist, abi3, console script, parity, upstream, gate; the Allium terms (module, diagnostic, finding) with one sentence each pointing at upstream's documentation |
| `docs/tutorials/first-change.md` | T07 | same | An exercise that can be followed again, test-first: a core unit test for a new `Diagnostic` field fails to compile, then the field; a pytest case fails on the missing attribute, then the pyclass attribute; stubtest fails on the stub, then the stub; `just check` |
| `docs/how-to/install-and-run.md` | T07 | new | `uvx --from alliumpy allium ...`, `uv tool install alliumpy`, `pip install alliumpy`, the Python API in five lines; what `allium check`'s exit codes mean, as upstream defines them; slug `install_and_run`. Until T13 lands, it says the CLI answers `--version` only and names T13 |
| `docs/how-to/develop-locally.md` | T07 | same | Two crates and the Python package; `py-develop`; the `PYO3_PYTHON` rule; otherwise P's |
| `docs/how-to/test-and-debug.md` | T07 | same | nextest for the core, pytest and stubtest for the binding, `wheel-smoke`, coverage HTML |
| `docs/how-to/maintain-dependencies.md` | T07 | same | P's; the `allium-parser` pin is a release, not an update (§9); "nothing updates them" until T17 |
| `docs/how-to/deploy-to-github-pages.md` | T07 | same | Both crates' rustdoc; the visibility condition (§1 fact 6) |
| `docs/explanation/architecture.md` | T07 | same | Upstream's parser under an exact pin, the core's conversion layer, the thin pyo3 crate, the Python package and console script; what S01 decides and what wave 2 adds (T13, T14), which each ticket updates when it lands |
| `docs/explanation/layering.md` | T07 | same | The direction Cargo enforces: `alliumpy` -> `alliumpy-core` -> `allium-parser`; pyo3 only in `alliumpy`; Python only in `python/`, `tests/` and `scripts/` |
| `docs/explanation/packaging.md` | T07 | new | One wheel, abi3-py311 plus `cp314t`, the five targets, the static version and `.postN`, the two licence texts, pixi versus maturin manifests, the sdist ruling (S01); slug `python_packaging` |
| `docs/explanation/quality-philosophy.md` | T07 | same | P's argument; examples from this gate, including why the wheel is smoked offline and why parity is byte-for-byte |
| `docs/explanation/security-model.md` | T07 | same | A wheel built from an upstream crate: supply chain (the exact pin, `--locked`, cargo-deny, trusted publishing with no token), `forbid(unsafe_code)`, untrusted inputs to the parser, the parity reference built from crates.io and never downloaded |
| `docs/reference/commands.md` | T07 | same | The recipe table of §4 |
| `docs/reference/configuration.md` | T07 | same | Both Cargo manifests, the lint tables (workspace and the bindings crate's own), `deny.toml`, the floor, both `pyproject.toml` files and what each owns, `ruff.toml`, `mypy.ini`, both tool lists, `scripts/version_check.py` |
| `docs/reference/testing.md` | T07 | same | nextest and doctests for the core; pytest, stubtest and the smoke for the binding; coverage scope; the insta rule waiting for its first snapshot; parity (T13) |
| `docs/reference/quality-gates.md` | T07 | same | The twenty-two gates of §4 |
| `docs/reference/documentation-contract.md` | T07 | same | L's rules verbatim; "Links that leave the repository" rewritten to name only the outward pages that exist here: `api.md`, `deploy-to-github-pages.md`, `install-and-run.md` |
| `docs/reference/agent-contract.md` | T07 | same | Seven skills |
| `docs/reference/api.md` | T07 | same | The Python API (every name `__init__.py` re-exports, as `_alliumpy.pyi`, which is canonical, describes it; `ALLIUM_VERSION_STRING` noted as not public, §9), rustdoc for both crates, `just doc`, `just site`, Pages when enabled |
| `docs/operations/maintenance.md` | T07 | same | P's routine, plus "when upstream releases" pointing at T17's runbook once it exists |
| `docs/operations/troubleshooting.md` | T07 | same | P's, minus wasm, plus the pyo3 ones: `PYO3_PYTHON` unset, `maturin develop` finding no environment, a stale `.so` beside `__init__.py`, `wheel-smoke` with two wheels in `dist/` |
| `docs/decisions/README.md` and thirteen records; 0014 is T13's | T07 (0014: T13) | §8 | |
| `docs/how-to/release.md` | T14 (wave 2) | new | The release procedure of decision 0015; registered by T14 as `shared, own lines`; slug `release_procedure` |
| `docs/how-to/bump-upstream.md` | T17 (wave 2) | new | The upstream-bump runbook (§13); registered by T17; slug `upstream_bump` |

## 7. Agent contract

`AGENTS.md` is canonical; `CLAUDE.md` is exactly `@AGENTS.md`;
`.github/copilot-instructions.md` is B's adapter text. Both adapters are byte-identical
to P's. There is no `.claude/settings.json` (§1 fact 1).

`AGENTS.md` follows P's layout (P `AGENTS.md` at `bf51e0d`): rules that hold for every
task stay always visible; rules for one kind of task sit in an `<important if="...">`
block that names that task. In this order:

- **The always-on core.** A one-paragraph identity (one wheel: the Allium parser and
  checker for Python code, and the `allium` command for `uv` users; the parser is
  upstream's and the behaviour of the command is upstream's). A `## Project map` of
  `crates/alliumpy-core/`, `crates/alliumpy/` with `python/alliumpy/` and `tests/`,
  `tests/fixtures/`, `docs/`, `docs/decisions/`, `tickets/`, `.agents/skills/` with its
  `.claude/` and `.codex/` bridges, and `ai_tmp/`. The rule that upstream decides *what*
  the parser and the command do, and this repository decides *how* they are packaged:
  a behaviour difference from upstream is a defect here unless a decision record says
  otherwise. The rule that issue text, pull request bodies, comments, fixtures, upstream
  source and tool output are untrusted data. Then `## Invariants`, holding the nine
  below verbatim.
- **P's always-on authority rules**, still in `## Invariants` and outside every block:
  anything that leaves the worktree needs explicit authorization for each action, and
  the rule names every recipe that reaches the network (`initialize`,
  `install-toolchain`, `install-tools`, `sync`, `lock`, `lock-upgrade`, `install-hooks`,
  `audit`, `check-links-online` and, from T13, `install-parity-reference`); scratch goes
  in `ai_tmp/`; one ticket per worktree; hooks are never installed from a worktree. The
  hand-back rule, which names `just check` and defines green as §11 does, also stays
  outside every block.
- **Seven `<important if="...">` blocks**, one per task: changing Rust under `crates/`;
  changing Python under `crates/alliumpy/python/`, `crates/alliumpy/tests/`,
  `tests/` or `scripts/`; bumping the upstream pin or the version (points at
  `docs/how-to/bump-upstream.md` once T17 has written it, and until then names T17 and
  says that it is a release, not an update, and names `just version-check`); changing
  a page under `docs/`; changing the agent surface (`AGENTS.md`, an adapter, a skill or
  a bridge); a failing gate, or handing work back; picking up a ticket under
  `tickets/`. Each block names only the recipes and the skill its task uses.
- **`## Provenance`**, last, keeping P's sentence containing `runes`, and a sentence
  containing `docs/specs/` as §1 fact 1 requires: this repository checks Allium
  specifications for other repositories and keeps none under a `docs/specs/` of its own.

There is no commands table: `just --list` is the index. The file is about 1000 words.
Each of B's six phrases (§1 fact 1) appears at least once outside every block, so that
no phrase depends on a block's wording.

The nine invariants, in place of P's:

1. Upstream decides behaviour. The `allium` command in the wheel has stdout and
   exit-code parity with `allium-cli` at the pinned version over the corpus; `just
   parity` proves it (from T13). The Python API's results are the parser's, converted,
   never reinterpreted.
2. `alliumpy` depends on `alliumpy-core`, which depends on `allium-parser`; never the
   reverse, and pyo3 appears only in `crates/alliumpy`.
3. Public types in `alliumpy-core` are `Send + Sync + 'static`, `Clone` and `Debug`;
   public enums and structs are `#[non_exhaustive]`; errors have stable `Display` text,
   because pyo3 builds the Python exception's message from it.
4. `#![forbid(unsafe_code)]` in every crate: through the workspace lint table in
   `alliumpy-core`, and through the crate's own `[lints]` table in `alliumpy`.
5. Clippy pedantic with the lint tables; `#[expect(lint, reason = "...")]` only.
6. Coverage does not fall below 90% of lines over `crates/alliumpy-core/src/**`; the
   bindings crate is covered by pytest, stubtest and the wheel smoke, which `just check`
   runs.
7. `Cargo.lock` is the pin; manifests write full `x.y.z` caret ranges, except
   `allium-parser`, which is exact (decision 0011); every cargo gate that builds or
   resolves dependencies passes `--locked`, except `deps-unused`, whose `cargo shear`
   takes no such flag, and `snapshots-check`, which runs after `lock-check` and offline
   because cargo-insta forwards the flag to nextest; and `locked = true` in the maturin
   manifest makes every wheel build do the same (decision 0004).
8. No dependency is added without the decision-0004 note.
9. One version: the wheel's version with `.postN` stripped equals both crates' version,
   the `allium-parser` pin and the version `allium --version` prints (decision 0010);
   `just version-check` proves it, and a bare pin bump fails it by design.

Skills, canonical under `.agents/skills/<name>/SKILL.md`, each with a bridge under
`.claude/skills/` and `.codex/skills/` whose body is B's `BRIDGE_BODY`. The bridges
repeat the canonical frontmatter, which B's `_check_skills` compares, and they freeze at
T00, so T00 writes the final frontmatter: P's for every carried skill except
`rust-change`, whose description becomes `Implement or review a change to the core or
the bindings crate with the layering, tests and documentation evidence the invariants
require.`, plus the new `python-change`, whose description is `Implement or review a
change to the Python package, its stub, its tests or the console script with the
stubtest, pytest and wheel-smoke evidence the invariants require.`

| Skill | From P | Change |
| --- | --- | --- |
| `rust-change` | same | Two crates with a fixed direction; the bindings crate's own lint table; no effects clause; a public type in the core is part of the Python API's shape |
| `python-change` | new | Read `_alliumpy.pyi` first, it is the API's canonical description; change the stub, the Rust binding and the test together; `just py-lint`, `just py-typecheck`, `just py-test`, `just py-stubtest`, `just wheel-smoke`, `just version-check`; the console script's behaviour is upstream's (invariant 1) |
| `plan-change`, `review-change`, `review-docs`, `project-check` | same | Gate names and numbers of §4; no wasm, no specs, no effects |
| `fix-quality` | same | A dispatch line for every gate of §4, the six Python gates included; no wasm, no specs, no effects |

Seven skills, fourteen bridges. `just check-agents` prints
`Validated AGENTS.md, 2 adapters, and 7 skills.`

## 8. Decision records

A fresh series. A carried record opens "Carried from pachinko's decision NNNN at
`bf51e0d`" (and, where P's was itself carried, "which carried libpawdoku's decision
NNNN at `ccdd001`") and keeps P's `canonical_for` slug. Format as L's (L
`docs/decisions/0007-dependency-policy.md` at `ccdd001`; P's records are stubs, §6):
frontmatter, `# Decision NNNN: title`, Context, Decision, Consequences, What would
reopen this, Related pages. T07 writes 0001 to 0013; T13 writes 0014 from S01's draft;
each wave-2 ticket writes its own.

| Number | File | Title | From P | Slug |
| --- | --- | --- | --- | --- |
| 0001 | `0001-one-wheel-two-crates.md` | One wheel from two crates: a thin pyo3 crate over a tested core | new | `decision_one_wheel` |
| 0002 | `0002-hook-runner-and-checkers.md` | Hook runner and checkers | 0004 (L 0004) | `decision_python_toolchain` |
| 0003 | `0003-apache-2-0-with-upstream-mit.md` | Apache-2.0 for this repository, upstream's MIT shipped beside it | 0006 (L 0006), extended: the wheel carries both texts (§1 fact 7) | `decision_license` |
| 0004 | `0004-dependency-policy.md` | Dependency policy: caret ranges and `Cargo.lock` | 0007 (L 0007) | `decision_dependency_policy` |
| 0005 | `0005-rust-quality-gate.md` | The Rust quality gate | 0009 (L 0009) | `decision_rust_gate` |
| 0006 | `0006-tool-manager.md` | Tool manager | 0011 (L 0011) | `decision_tool_manager` |
| 0007 | `0007-metrics-gate.md` | The metrics gate | 0012 (L 0013) | `decision_metrics_gate` |
| 0008 | `0008-api-reference-on-github-pages.md` | The API reference on GitHub Pages, when the repository's visibility allows it | 0013 (L 0016), conditioned on §1 fact 6 | `decision_api_reference_on_pages` |
| 0009 | `0009-pypi-name-alliumpy.md` | PyPI name `alliumpy`, console script `allium` | new | `decision_pypi_name` |
| 0010 | `0010-version-tracks-upstream.md` | The wheel version tracks upstream, with `.postN` for packaging fixes | new | `decision_version_policy` |
| 0011 | `0011-exact-pin-on-allium-parser.md` | An exact pin on `allium-parser` | new | `decision_upstream_pin` |
| 0012 | `0012-abi3-wheels-and-platforms.md` | `abi3-py311` wheels and the five platforms | new | `decision_wheel_platforms` |
| 0013 | `0013-no-spec-gate-no-allium-skills.md` | No specification gate and no Allium skills in this repository | new | `decision_no_spec_gate` |
| 0014 | `0014-cli-strategy.md` | How the `allium` command gets into the wheel | new; S01 drafts, T13 lands | `decision_cli_strategy` |
| 0015 | `0015-release-process.md` | The release process | T14 | `decision_release_process` |
| 0016 | `0016-mutation-bench-and-fuzz.md` | Mutation testing, benchmarks and fuzzing | T15 | `decision_mutation_bench_fuzz` |
| 0017 | `0017-renovate.md` | Dependency updates through Renovate, except the upstream pin | T17 | `decision_dependency_updates` |

0014's T00 stub says the decision is open, names S01 and T13, and lists the three
options of §1 decision 3; T07 leaves it as the stub (T13 owns it). 0007's thresholds are
P's; its module-boundary rules wait for modules. 0010 and 0011 divide the version
argument: 0010 is the policy users see, 0011 is why the dependency is pinned exactly and
why Renovate leaves it alone.

## 9. Python packaging

This section replaces P's §9 (the placeholder specification module and the effects
boundary). It is the one part of this repository with no finished original to cite, so
it is stated in full.

### The shape

Two crates (§0, §3). `alliumpy-core` is where Rust is tested and measured; `alliumpy` is
glue. The rule for what goes where: anything that can be unit-tested without an
interpreter lives in the core; the bindings crate holds only `#[pymodule]`,
`#[pyclass]`, `#[pyfunction]` and `From` impls into pyo3 types. S01's result, if it
vendors upstream's CLI, goes into `crates/alliumpy-core/src/cli/`, under the same rule.
That places it under the floor (§7 invariant 6), the lint tables (invariant 5) and
`rustqual.toml` (§4 gate 7); S01 rules on what route (a) does to each, and T13 executes
that ruling, never a gate change the ruling does not state.

### The two manifests

The root `pyproject.toml` is the pixi manifest and nothing else (§2); pixi never reads
the other (§1 fact 2). `crates/alliumpy/pyproject.toml` is maturin's, and T00 writes it
in this shape, final in `[project]`:

```toml
[build-system]
requires = ["maturin>=1.15,<2.0"]
build-backend = "maturin"

[project]
name = "alliumpy"
# Static, not dynamic: Cargo cannot write a PEP 440 post-release, and this
# repository's packaging fixes are 3.6.1.postN (decision 0010). just
# version-check holds this equal to the crates' version with .postN stripped.
version = "3.6.1"
description = "The Allium specification parser and checker for Python, and the allium command for uv users"
readme = "README.md"
requires-python = ">=3.11"
license = "Apache-2.0"
# Both texts ship in the wheel's .dist-info/licenses/ (decision 0003). Globs
# cannot leave this directory, hence the copies here.
license-files = ["LICENSE", "LICENSE-allium-tools"]
classifiers = [
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3 :: Only",
  "Programming Language :: Rust",
  "Operating System :: OS Independent",
  "Topic :: Software Development :: Compilers",
  "Typing :: Typed",
]

[project.scripts]
allium = "alliumpy._cli:main"

[project.urls]
Repository = "https://github.com/BiscuitBin/alliumpy"
Upstream = "https://github.com/juxt/allium-tools"

[tool.maturin]
python-source = "python"
module-name = "alliumpy._alliumpy"
# Every maturin build honours the workspace Cargo.lock, as every gate does.
locked = true

[tool.maturin.generate-ci.github]
trusted-publishing = true
publishing-environment = "release"
```

No `[tool.pixi]` table, with a comment saying why. `dynamic = ["version"]` is never
set. maturin's documentation says a static `[project] version` takes precedence over
Cargo's; T00 proves it by reading the built wheel's name (§12 claim 1).

### The T00 API, and what it grows into

T00 ships the smallest API that exercises every layer:

- `alliumpy_core::ALLIUM_VERSION: &str = "3.6.1"`.
- `alliumpy_core::ALLIUM_VERSION_STRING: &str`, the exact text `allium --version`
  prints upstream, read by T00 from U `crates/allium/src/main.rs` at `v3.6.1` and
  written as a literal with a comment naming that file; on 2026-10-22 it was
  `allium 3.6.1 (language versions: 1, 2, 3)`. A unit test asserts it starts with
  the word `allium`, a space and `ALLIUM_VERSION`. S01 establishes whether `allium-parser`
  exposes the language-version list so that the suffix can be derived rather than
  copied (§12 claim 12); until then the literal is the copy and `version-check` checks
  the prefix. If S01 makes the suffix derivable, T13 replaces
  `scripts/version_check.py`'s regex-over-literal clause as `shared, own lines`. In
  either case T13 adds a `--print-pin` flag to the script so that
  `install-parity-reference` reads the pin from `Cargo.toml` rather than a literal
  ("The parity reference" below).
- `alliumpy_core::Severity` (`Error`, `Warning`, `Info`; `#[non_exhaustive]`, `Clone`,
  `Copy`, `Debug`, `PartialEq`, `Eq`, `Hash`) and
  `alliumpy_core::Diagnostic { line: u32, col: u32, severity, message: String,
  code: Option<String> }` (`#[non_exhaustive]`, `Clone`, `Debug`, `PartialEq`, `Eq`,
  `Hash`), one-based line and column as upstream's CLI prints them, converted from the byte
  span through `allium_parser::lexer::SourceMap`.
- `alliumpy_core::parse(source: &str) -> Vec<Diagnostic>`: upstream's `parse`, its
  diagnostics converted. (The checker, `check`, and the AST follow in T13 or a later
  ticket, never in T03, which changes no Rust (§3); S01 rules on what the CLI route
  needs.)
- Python: `alliumpy.parse(source: str) -> list[Diagnostic]`, `alliumpy.Diagnostic`
  (frozen, attributes as above, `severity` a plain `str` of `"error"`, `"warning"` or
  `"info"`; there is no Python enum; `__eq__` and `__hash__` from the Rust `PartialEq`
  and `Hash` through pyo3's `eq` and `hash` options, so two diagnostics with equal
  fields compare equal and hash alike; a `__repr__` of exactly the form
  `Diagnostic(line=1, col=2, severity='error', message='...', code=None)`, every field
  in that order, `severity`, `message` and `code` written as Python `repr`s),
  `alliumpy.AlliumError` (below) and `alliumpy.ALLIUM_VERSION`, all re-exported from
  `alliumpy._alliumpy` by `__init__.py`, listed in `__all__` and described in
  `_alliumpy.pyi`, which is the canonical description of the API.
  `alliumpy.__version__` is defined in `__init__.py` as
  `importlib.metadata.version("alliumpy")` (the PEP 440 version, `.postN` included);
  it is not an attribute of `_alliumpy` and does not appear in `_alliumpy.pyi`, so
  stubtest never sees it.
  `ALLIUM_VERSION_STRING` is exposed as an attribute of `alliumpy._alliumpy` (so that
  stubtest sees it) and is imported by `_cli.py`, but is not re-exported by
  `__init__.py` nor in `__all__`. `__all__` is exactly
  `["parse", "Diagnostic", "AlliumError", "ALLIUM_VERSION"]`; `__version__` is a module
  attribute outside it, as dunders are.
- `alliumpy._cli.main() -> int`, the console script: T00's handles `-V` and `--version`
  by printing `ALLIUM_VERSION_STRING` and returning 0, and answers anything else with
  one line on stderr saying the command arrives with T13 and exit status 2. It never
  derives the upstream string from `__version__` or the reverse (decision 4). T13
  replaces it with S01's route.

Public pyo3 classes are `#[pyclass(frozen, eq, hash)]` and `Send + Sync` by
construction, each with a `__repr__` in the form above; a Rust error reaching Python
becomes a `ValueError` subclass `alliumpy.AlliumError` created
with `create_exception!`, its message the error's `Display` text (invariant 3). T00 has
no fallible path yet; the class exists so that the stub, the test and the shape are in
place.

### `wheel-smoke`, `version-check` and the fixtures

`tests/fixtures/smoke/` holds `ok.allium` (a module upstream's `allium check` accepts
with an empty `diagnostics` list and exit 0: parser and analyser both silent, so `parse`
of it is empty; T13 appends that command to `wheel-smoke` and T14's release smoke
repeats it), `broken.allium` (one that yields at least one `error` diagnostic) and
`smoke.py`, which imports `alliumpy`, asserts `parse` of the first is empty and of the
second is not, asserts that `alliumpy.__version__` starts with `alliumpy.ALLIUM_VERSION`
(no version literal: `version-check` owns the copies, invariant 9), and exits non-zero on
any failure. T00 writes the two modules from U's own fixture corpus or the language's
smallest valid module, with attribution in a comment; T03 replaces them with its own and
keeps `smoke.py`'s contract. The venv lives under `target/wheel-smoke/`, so `check-clean`
sees nothing.

`scripts/version_check.py` (T00, frozen in wave 1; T13 edits it as `shared, own lines`)
runs under the pixi interpreter with `-I`, uses `tomllib`, and asserts:
`[workspace.package] version` in `Cargo.toml` == `[project] version` in
`crates/alliumpy/pyproject.toml` with a trailing `.postN` stripped == the version in
`[workspace.dependencies] allium-parser` with its `=` stripped == `ALLIUM_VERSION` as
written in `crates/alliumpy-core/src/lib.rs` (a regex over the literal) == the second
word of what `target/wheel-smoke/venv/bin/allium --version` prints, whose first word
must be `allium`. A missing venv is a failure naming `just wheel-smoke`. T13 tightens
the last clause to the whole string once S01 has settled the suffix.

### The parity reference (S01 and T13)

The reference `allium` is built from crates.io, never downloaded:
`cargo install allium-cli@<version> --locked --root <root>` into a directory **off
`PATH`**, by the recipe `install-parity-reference` (T13; network, authorised), whose
root is under `.tools/parity/` (gitignored, never `.tools/bin/`), so that no second
`allium` ever shadows the wheel's or a developer's. The version is read from
`Cargo.toml`'s pin (through `scripts/version_check.py --print-pin`, T13), never written
as a literal in the recipe. The harness in `tests/parity/`
invokes the reference by absolute path and the candidate as `target/wheel-smoke/venv/bin/allium`,
runs upstream's fixture corpus from `tests/fixtures/parity/` (committed with
attribution, excluded from typos) through both, and compares stdout byte for byte and
exit codes for every file and for the directory form. It fails closed: an empty corpus
is a failure, and a positive control (one fixture whose reference exit status the
harness has just observed to be nonzero, named in the output) runs first. Harness Python
runs with `-I`. Parity is POSIX-only (§1 fact 9);
`parity` is a local recipe outside `check` and a CI job that the required `check` job
needs (§10).

### The sdist

S01 rules on the sdist. Under the bundled-binary route it is unbuildable (no binary in
it); under the others, `uv` on any platform the matrix does not cover silently falls
back to building it, which needs a Rust toolchain and the network (Python 3.10 does not:
`requires-python` is in the sdist's metadata too, so it is refused, not built). T14 keeps
or drops the sdist as S01 rules and asserts its contents
(`Cargo.lock`, because `locked = true`; the vendored sources if S01 chose vendoring; both
licence texts); T12 documents the consequence for users.

### The release matrix versus the gate

`just check` builds and smokes the wheel for the developer's own platform (linux-64 or
osx-arm64) on pixi's Python 3.14. CI adds a `wheel-smoke` on Python 3.11, the abi3 floor
(§10). The five targets of decision 6, musllinux and the `cp314t` wheel are built only by
`release-pypi.yml`, rehearsed by a non-publishing `workflow_dispatch` run before any tag
(T14). Windows is proved there alone: the `.exe` console-script launcher, exit-code
propagation and CRLF (§12 claim 18).

### Licences

This repository is Apache-2.0 (decision 0003), as P. Upstream's MIT text and its
copyright line ship in the wheel as `LICENSE-allium-tools`, with a header paragraph
saying which upstream version the wheel carries; T00 writes it with the sentence that the
code under it arrives with the route S01 chooses, and T13 replaces that sentence with the
route and the fixture corpus it lands, as `shared, own lines` (§11). `deny.toml`'s
allow-list already permits MIT (P `deny.toml`).

## 10. CI

P `.github/workflows/ci.yml`, `audit.yml`, `pages.yml` and
`.github/actions/setup/action.yml` at `bf51e0d`, with these changes:

- The setup action's description and its `.tools` cache step's comment no longer mention
  the allium binary; `ci.yml`'s header comment counts six gate jobs. No job runs
  `just install-allium`.
- The `rust` job's steps are: `check-toolchain`, `lock-check`, `fmt-check`,
  `toml-check`, `clippy`, `metrics`, `features`, `test`, `snapshots-check`, `doc`,
  `deps-unused`. The `effects` step is gone.
- A new `python` job, after `rust`: the setup action, then `just py-lint`,
  `just py-typecheck`, `just py-test`, `just py-stubtest`, `just wheel-smoke`,
  `just version-check`, then `actions/upload-artifact` of `dist/*.whl` as `wheel-linux`
  (seven days).
- A new `wheel-smoke-py311` job that `needs: [python]`: `actions/checkout`,
  `actions/setup-python` with `python-version: '3.11'`, `actions/download-artifact` of
  `wheel-linux` into `dist/`, then plain shell, not `just`: `python -m venv venv`,
  `venv/bin/python --version` (so the log carries `Python 3.11.x`),
  `venv/bin/pip install --no-index --no-deps dist/*.whl`,
  `venv/bin/python -I tests/fixtures/smoke/smoke.py`, `venv/bin/allium --version`.
  Network is allowed in CI, so `--no-index` and `--no-deps` are what keep the install
  to the one downloaded file. This is the only place the abi3 floor is exercised
  before a release.
- Every gate job that runs recipes ends with `just check-clean`, a delta from P (whose
  CI never ran it, as P's T01 hand-back notes record), so that a recipe that rewrites a
  tracked file fails in CI as it does locally.
- The `documents` job's steps are `just lint`, `just check-docs`, `just check-agents`.
  No `check-specs`, no `analyse-specs`.
- `check`'s `needs` is `[rust, python, wheel-smoke-py311, coverage, deny, documents]`.
- `pages.yml`: the `deploy` job's `if:` also requires the repository to be public
  (`github.event.repository.visibility == 'public'`, or the equivalent T01 verifies),
  with a comment citing §1 fact 6, so that a private repository's run builds and
  uploads the artefact and skips the deploy rather than failing. T01 hands the
  visibility question to the maintainer.
- Every remote `uses:` keeps a full SHA with a version comment, re-read on the day T01
  runs (`gh api repos/<owner>/<repo>/git/ref/tags/<tag>`, dereferencing annotated tags).
  The local `uses: ./.github/actions/setup` has no pin.

The required check is `check`, the aggregate job, from T01 onward and never anything
else. A new gate job joins `check`'s `needs` and nothing else moves. In wave 2, T13's
`parity` job joins `needs`, because a CLI that no longer matches upstream is a broken
wheel; it needs the network to `cargo install` the reference (cached by `actions/cache`
on the pin) and is the one gate job that does. T14's `release-pypi.yml` (tag-triggered
and `workflow_dispatch`), the scheduled `mutants.yml` and `fuzz.yml` never do. `audit`
is never in `needs`.

Branch protection on a private repository is a paid-plan feature (§1 fact 6). T01 reads
`gh api orgs/BiscuitBin --jq .plan.name`, which must print a plan name (GitHub returns
`plan` to an organisation owner's token only; `null` means the plan was not read: stop
and ask the maintainer for it, never infer `free`), and the repository's visibility, and
stops: the maintainer chooses between making the repository public, a paid plan, or no
protection until one of those happens (in which case `check` is still the one check every
pull request runs, and the protection step is recorded as deferred, not skipped
silently).

## 11. Rules for tickets and lanes

- **Worktrees and branches.** Each ticket runs on the branch its `branch:` field names
  (`ticket/<id>-<slug>`, lowercase) in its own worktree, created from `origin/main` after
  a fetch, once every ticket it depends on has merged. Before T00, `tickets/` itself reaches `main` by merging
  `bootstrap-tickets` through a pull request (`README.md`, "How to pick up a ticket"); no
  worktree created from `main` holds these files until then. From a Supacode terminal:
  `supacode repo worktree-new --fetch --branch <branch> --base origin/main --name <id>`;
  otherwise `git fetch origin && git worktree add --no-track ../<id> -b <branch> origin/main`
  (network, authorised). A stale local `main` must never seed a lane: a green baseline on a
  stale base proves nothing. The tools live in the worktree's own
  gitignored `.pixi/` and `.tools/`, so every new worktree runs `just initialize`
  (network, authorised); only the primary checkout's run installs the shared hook shim,
  once, after T00 merges (`README.md`, "How to pick up a ticket").
- **T00 ships a shape-complete skeleton.** `bg-validate-docs` and `bg-validate-agents`
  can only be green if every page, record and skill exists from the first commit, so T00
  ships a stub for each. Lanes **replace** stubs; they never add, rename or reclassify a
  registered page, record or skill. A lane may create only the paths §3 marks `new` for it.
- **Files no wave-1 lane touches:** `Justfile`, `.pre-commit-config.yaml`,
  `.pre-commit-fix.yaml`, `rust-toolchain.toml`, `tools.txt`, `tools-source.txt`,
  `pixi.lock`, `pyproject.toml`, `crates/alliumpy/pyproject.toml`,
  `crates/alliumpy/LICENSE`, `crates/alliumpy/LICENSE-allium-tools`,
  `crates/alliumpy/python/alliumpy/py.typed`, `scripts/version_check.py`,
  `.editorconfig`, `.gitattributes`, `.gitignore`, `.markdownlint-cli2.jsonc`,
  `lychee.toml`, `_typos.toml`, `scripts/initialize.sh`, `docs/manifest.yml`,
  `docs/README.md`, `CLAUDE.md`, `.github/copilot-instructions.md` and every bridge.
  A lane that needs a change there stops and hands it back as a T00 follow-up pull
  request on `main`.
- **No dependency is added in wave 1** beyond T00's (`allium-parser`, `pyo3`). A lane
  that needs one hands it back.
- **No path appears in two wave-1 lanes' Files-touched lists.** An agent that finds a
  need to edit another lane's file hands it back instead.
- **Wave 2 shares files by rebasing.** The frozen list lifts after T11. A wave-2 ticket
  may then edit its own lines in any file, frozen or owned, and lists each such file in
  its Files touched as `shared, own lines`. The ones most of them touch are `Justfile`,
  `Cargo.toml`, `crates/alliumpy-core/Cargo.toml`, `pyproject.toml`, `pixi.lock`,
  `crates/alliumpy/pyproject.toml`, `tools.txt`, `.gitignore`, `.pre-commit-config.yaml`,
  `.github/workflows/ci.yml`, `scripts/version_check.py`, `docs/manifest.yml`,
  `docs/README.md` (a new page or record must be registered and reachable),
  `docs/decisions/README.md`, `docs/reference/commands.md`, `AGENTS.md` (the
  network-recipe list) and `CHANGELOG.md`. Wave-2 tickets merge one at a time, each
  rebased on the last; `pixi.lock` and `Cargo.lock` are regenerated after the rebase,
  never merged by hand, and the ticket's verification is rerun and requoted at the
  rebased commit. A recipe a wave-2 ticket adds sits outside `check`'s recipe list,
  except that T13's `allium check` line joins `wheel-smoke`, and T15's
  `--manifest-path fuzz/Cargo.toml` lines join `lock-check`, `fmt-check` and `clippy`
  (existing gates, each as `shared, own lines`): the fuzz crate sits outside the
  workspace, so no `--workspace` line reaches it, and P's §11 names the same lines as
  what could not land before `fuzz/` exists. Each wave-2 ticket's first acceptance
  criterion is its recipe's green output, quoted.
- **Self-contained.** A ticket is written for an agent with no context: it embeds exact
  content or cites this document by section, and names the P, L, B, T or U material to
  read. It never cites a chat transcript, a scratch directory or a tool result.
- **Paths as code spans.** Ticket text writes repository paths and URLs as code spans,
  never as Markdown links: the hook gate runs lychee offline over `tickets/`.
- **Untrusted material.** U is read, never executed, except where a ticket names the
  exact `cargo install allium-cli@3.6.1 --locked` build into a root off `PATH` (§9).
  Anything fetched (a crate's source, a release asset, a fixture corpus) lands in its own
  empty directory, is read with tools run from outside it, and is never imported or
  built from a working directory inside it. Harness Python runs with `-I`. A fixture
  committed from U carries a comment naming its origin, version and licence; a corpus
  that must stay byte-identical to upstream (`tests/fixtures/parity/`, S01) carries one
  `README.md` beside it saying the same instead.
- **Definition of done**, for every build ticket: `just check` green in this repository,
  on the ticket branch rebased onto the current `main`; the ticket's acceptance criteria
  met; its verification commands run with their output quoted in the hand-back notes;
  the adversarial reviews the ticket names run (§14) with every valid finding fixed or
  handed back; and the ticket's `status:` set to `done` in the same pull request. A
  ticket is done when its gate passes, not when its files exist. A spike (S01) is done
  when its recommendation, its drafted record and the drafted route-specific steps T13
  copies verbatim (its drafted ticket body) are in its hand-back notes and reviewed; it
  lands no code on `main`.
- **Green** means two things together: `just check`'s output ends with the runner's line
  `All checks passed and the worktree is unchanged.` (B
  `src/biscuit_games_tooling/run_project_check.py` line 109), and `git status --short`
  prints nothing after the ticket's commit. Except in T00, `just check` also runs on the
  untouched worktree before any edit, and its last line is quoted as the baseline; a red
  baseline means `main` is broken, and the fix is a `main` pull request, not this lane's
  work. Before asking to push, the agent runs `git fetch origin` (network, authorised),
  rebases onto `origin/main`, reruns `just check`, and reruns and requotes the ticket's
  verification. Two lanes that are each green can merge into a red `main`, and only
  this rerun sees them together.
- **Quoted evidence names its commit.** Each quoted output is headed by the commit it ran
  at (`git rev-parse --short HEAD`, plus "with uncommitted changes" when that is true). A
  rebase, a merge of `main` or a §14 fix round after a quote makes it stale: rerun it and
  replace it. CI evidence names the run URL and the commit the run tested, which for a
  pull request is the merge commit, not the branch head.
- **Checks fail closed.** A failed read, a timeout or an empty pipe is never a pass.
  Quoted output shows each command's exit status. A check that passes by printing
  nothing is preceded by a positive control: the unfiltered command, run alone, exits 0
  and matches something; a linter is preceded by its fixture failing (§4). An API read
  counts as "absent" only on an HTTP 404 whose message names absence; GitHub also
  answers 404 to a token that may not read the resource, so that, and any other error,
  stops the step. A cache is not evidence: a `uvx` proof runs with `UV_CACHE_DIR` on an
  empty directory; a wheel smoke runs after `dist/` was emptied.
- **Separately authorised actions.** Commits on the ticket branch are the ticket's work.
  Pushing, opening a pull request, tagging, filing issues, changing repository or
  organisation settings, installing a GitHub App, publishing anywhere (PyPI included),
  registering a PyPI publisher, approving a deployment, installing anything outside the
  worktree, and editing another repository are each separately authorised: the ticket
  says where one occurs, and the agent stops and asks.
- **Network.** `pixi install`, `cargo fetch`, `rustup toolchain install` and the recipes
  §7's `AGENTS.md` rule names (`initialize`, `install-toolchain`, `install-tools` with
  its rustqual source build, `sync`, `lock`, `lock-upgrade`, `install-hooks`, `audit`,
  `check-links-online` and, from T13, `install-parity-reference`) need the network. Each
  is a named, authorised step in the ticket that runs it. `just check` must not need the
  network: `wheel-smoke`'s `uv venv` and `uv pip install` run `--offline` and
  `--no-index`, and `py-develop`'s `maturin develop` installs a wheel with no dependency
  to resolve; claim 14 shows both. A claim that something works with the network
  blocked is shown under an OS-level denial: on macOS,
  `sandbox-exec -p '(version 1)(allow default)(deny network*)' <command>`; on Linux,
  `unshare -rn <command>`, in a namespace holding only `lo`. Inside the same denial, the
  negative control `curl -fsS --max-time 10 https://static.rust-lang.org` and
  `curl --noproxy '*' -fsS --max-time 10 https://1.1.1.1` must both fail, and the
  hand-back quotes both exit codes. Proxy variables are not denial: DNS, git, rustup, uv
  and raw sockets ignore them. A sandbox that fails to launch is not evidence. If the
  agent's own sandbox blocks a gate recipe, request the permission and record it; never
  weaken the recipe.
- **Scratch.** Anything that is not a deliverable goes in `ai_tmp/` (gitignored from T00)
  or the session's scratch directory, never in a commit. A "scratch copy" experiment
  (§12) is made in the worktree itself: save the file to `ai_tmp/`
  (`cp <path> ai_tmp/scratch/`), make the edit, run and quote the recipe, then copy the
  saved file back; a copied directory has no `.pixi/` or `.tools/`, so its `just`
  recipes fail for want of tools, which is not the gate firing.
- **Credentials.** No file carries a token. CI uses the run's own `github.token`; PyPI
  is reached by trusted publishing only (T14), and no PyPI token exists anywhere.

## 12. Unverified claims, and the ticket that checks each

Each claim was reasoned from source or documentation but not executed here. The named
ticket runs the check and records the outcome in its hand-back notes; a claim that fails
is a design change that comes back through this document. T11 carries claims 1, 3, 6,
8, 9, 10, 11, 13 to 17 and 19 to 22 (and S01's part of claim 12) from the wave-0 and
wave-1 hand-back notes; T17, the last ticket, carries claims 2, 4, 5, 7, 12 and 18, and
T14's parts of claims 1 and 19, from the wave-2 ones. P's and L's own claims about pixi,
prek, binstall and the hooks were settled there; a ticket re-checks them only by running
the gate.

| # | Claim | Check | Owner | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | maturin 1.15.0 takes a static `[project] version` over Cargo's, so the wheel is named `alliumpy-3.6.1-…` from the pyproject and `alliumpy-3.6.1.post1-…` after a `.post1` edit, with the crates still at `3.6.1` | `just wheel` and the wheel's filename, then the same with `.post1` in a scratch copy | T00 first, T14 | partial | T00 "Owned claim outcomes"; T14's part open (T17) |
| 2 | `uvx --from alliumpy allium --version` runs the console script from the published wheel with `UV_CACHE_DIR` on an empty directory | The proof run | T14 | open (T17) | T14's, carried by T17 |
| 3 | P's lint table is green on the pin, on both crates, pyo3's macro output included | `just clippy` on T00's tree | T00, T02 | holds | T00 "Owned claim outcomes"; T02 "Lint policy: claims 3 and 8" |
| 4 | `maturin generate-ci github` emits the `cp314t` free-threaded step and runner labels that exist for the five targets (macOS x86_64 in particular) | The generator's output, then the `workflow_dispatch` rehearsal | T14 | open (T17) | T14's, carried by T17 |
| 5 | `actions/attest` works on a private, non-Enterprise repository; if not, the step is removed | The rehearsal run | T14 | open (T17) | T14's, carried by T17 |
| 6 | nextest fails on zero tests by default, so `--exclude alliumpy` on a workspace whose core has tests runs those and nothing else | `cargo nextest run --workspace --exclude alliumpy --locked`, and the same with the core's tests removed in a scratch copy | T00 | holds | T00 "Owned claim outcomes"; T02 "Core coverage: claim 13" (six core tests) |
| 7 | The PyPI name `alliumpy` is still free on the day, and a pending publisher creates the project on first publish | `curl -sS -o /dev/null -w '%{http_code}\n' https://pypi.org/pypi/alliumpy/json` prints `404` before (and without `-o`, a body whose `message` is `Not Found`) and `200` after; any other code stops the step (§11) | T14 | open (T17) | T14's, carried by T17 |
| 8 | pyo3 0.30.1 holds L S04's facts (macros compile under `forbid(unsafe_code)`; no `extension-module`; `PYO3_BUILD_EXTENSION_MODULE` set by maturin), and `#[pyclass(frozen, eq, hash)]` compiles under the lint table (this repository's assumption, untested in L, which needed `skip_from_py_object` on 0.29.2) | `just clippy`, `just py-develop` | T00, T02 | partial | T00 "Owned claim outcomes"; T02 "Lint policy: claims 3 and 8"; `PYO3_BUILD_EXTENSION_MODULE` not shown (T18) |
| 9 | `maturin develop` finds the pixi environment through `CONDA_PREFIX` and installs with the pinned `uv 0.13.5` | `just py-develop` from a shell with no pixi activation and no `VIRTUAL_ENV` | T00 | partial | T00 "Owned claim outcomes"; T11 "Fresh clone (step 3)" (`CONDA_PREFIX` from an unactivated shell); the installer's uv version not shown (T18) |
| 10 | B's git dependency installs in `BiscuitBin` CI with no credential (P proved it on a public repository) | T00's stub run on `main`, then T01's full run | T01 | partial | T01 "Step 1: `check` on `main`" (stub run); the full run hit the cache (T18) |
| 11 | Pages and branch protection are unavailable to this private repository on the free organisation plan; the conditional deploy skips cleanly | `gh api orgs/BiscuitBin --jq .plan.name` (a plan name, not `null`), `gh api repos/BiscuitBin/alliumpy --jq .visibility`, the first `pages.yml` run | T01 | partial | T01 "State before (step 2, 2026-10-24T05:39:47Z, private)" (protection 403); Pages half and the private deploy skip not shown, repository public since 2026-10-24 (T18) |
| 12 | `cargo install allium-cli@3.6.1 --locked` builds on the pin, and the binary's `--version` output equals `ALLIUM_VERSION_STRING`; `allium-parser` does or does not expose the language-version list | The build in S01, `strings`/`rg` over `allium-parser`'s source in the registry cache | S01, T13 | partial | S01 "Step 2: upstream, re-read as data", "Step 3: the reference, the corpus and the harness"; T13's part open (T17) |
| 13 | `cargo llvm-cov nextest -p alliumpy-core` reaches 90% on T00's shape, and the report lists no line of `crates/alliumpy/` | `just coverage`, then `cargo llvm-cov report --show-missing-lines` | T00 first, T02 | holds | T00 "Owned claim outcomes"; T02 "Core coverage: claim 13" |
| 14 | `uv venv --offline --no-python-downloads` and `uv pip install --offline --no-index --no-deps` run under §11's network denial | `just py-develop` and `just wheel-smoke` under the denial, with both negative controls | T00 | holds | T00 "Owned claim outcomes"; T11 "Fresh clone (step 3)" (empty `UV_CACHE_DIR`) |
| 15 | The conda-forge pins of §2 solve together with `python 3.14.*` on both platforms | `pixi lock` | T00 | holds | T00 "Owned claim outcomes" |
| 16 | `cargo insta test … --workspace --exclude alliumpy` is accepted and `snapshots-check` is green with no `insta` dependency and no `.snap` | The recipe on T00's tree, then a stray `.snap` in a scratch commit | T00 first, T02 | holds | T00 "Owned claim outcomes"; T02 "Snapshot rejection without insta: claim 16" |
| 17 | rustqual 1.8.3 runs over `crates/alliumpy` (pyo3 macros) without a finding, or with findings the bindings crate's table explains | `just metrics` | T00 first, T02 | holds | T00 "Owned claim outcomes"; T02 "Metrics: claim 17" |
| 18 | On Windows, the console-script `.exe` launcher propagates `allium`'s exit code, and stdout carries no CRLF that would break a byte comparison | The rehearsal's Windows smoke | T14 | open (T17) | T14's, carried by T17 |
| 19 | The wheel's `.dist-info/licenses/` holds both texts | `python -m zipfile -l dist/*.whl` | T00 first, T14 | partial | T00 "Owned claim outcomes"; T14's part open (T17) |
| 20 | `ruff check` and `mypy` lint an explicitly named file that `ruff.toml` or `mypy.ini` excludes, so the positive controls of §4 fire | `just py-lint`, `just py-typecheck`, and each with the fixture's violation removed in a scratch copy (for ruff, each of `F401` and `E501` in turn) | T00 first, T03 | holds | T00 "Owned claim outcomes"; T03 "Scratch-copy failures (claims 20 and 21)" |
| 21 | `python -m mypy.stubtest alliumpy._alliumpy` imports the extension `py-develop` built into the pixi environment and compares it with `_alliumpy.pyi` | `just py-stubtest`, then with a deliberate stub error | T00 first, T03 | holds | T00 "Owned claim outcomes"; T03 "Scratch-copy failures (claims 20 and 21)" |
| 22 | T `scripts/bootstrap_repo.sh` works on an organisation-owned private repository, or fails in a way the dry run shows; T's script reads the Pages source (step 1, unless `--no-pages`) then protection (step 2) and its `gh_read` aborts on the first non-404 error, which on a private free-plan repository is at latest the protection read's HTTP 403, so the dry run may not complete there; T01 then applies the hygiene settings by hand, each one shown before it is applied | The script without `--apply` | T01 | holds | T01 "State before (step 2, 2026-10-24T05:39:47Z, private)" (the dry run's 403 stop), "Dry run (step 4, 05:55:36Z)", "State after (step 7, 06:23:31Z) and claims 11 and 22"; the by-hand fallback was not needed, the script applied hygiene once public |

## 13. Risks every ticket states where it applies

- **Upstream is pre-release and releases often.** 30 tags in six months, two to five a
  month, with signatures that grow between releases. Every upstream bump is a release of
  this repository, driven by T17's runbook: bump the pin, re-vendor if S01 chose
  vendoring, re-run parity, bump the wheel version, release. `version-check` fails a
  bare pin bump by design.
- **CLI drift.** If S01 chooses vendoring, upstream's CLI source and this repository's
  copy diverge silently between bumps; the parity corpus is the alarm, and it is only as
  good as the corpus. T13 states what the corpus covers and what it does not.
- **The repository was private until 2026-10-24.** It is now public, so Pages and
  branch protection are available on the free plan (T01), and T01's first full CI run of
  seven Ubuntu jobs reported `total_ms: 0` billable. Whether artefact attestation is
  available (§12 claim 5), and what the release matrix's macOS and Windows runners cost,
  T14 reads before acting.
- **Paid-plan features in the release.** A GitHub `release` environment with required
  reviewers, and tag rulesets, may themselves be paid-plan features on a private
  repository; T14 reads what the plan allows before asking.
- **The toolchain pin is stale by the time a ticket runs.** A ticket that bumps it bumps
  `rust-version` with it and re-runs `just clippy`, because the lint set moves.
- **pixi's rust shadows rustup** in a shell that does not source `~/.cargo/env`;
  `check-toolchain` is the alarm (P `tickets/CONVENTIONS.md` §13).
- **The small denominator.** One core crate with a handful of items: one untested branch
  breaches 90%. Keep each item trivially and fully tested until the conversion layer
  grows.
- **`--locked` and the snapshot.** Any recipe that rewrites `Cargo.lock` or `pixi.lock`
  fails `check-clean`; `target/`, `dist/`, the `.so`, `.tools/` and `.pixi/` are ignored
  from T00.
- **The network at first run, none in `check`.** As §11. `wheel-smoke` is the recipe
  most likely to reach for the network by accident (`uv` resolving, `pip` seeding); its
  flags are the guard, and the offline proof is T00's.
- **A gate that cannot fire.** A linter with nothing to lint, a stubtest with an
  allowlist that hides everything, a parity run over an empty corpus: the linters and
  the parity run have a positive control in the recipe (§4, §9); stubtest's guard is
  §12 claim 21's deliberate stub error and T03's allowlist review, and stubtest itself
  rejects an unused allowlist entry. A lane that weakens one hands it back.
- **A red stub run on `main`.** T00's merge is the first time the setup action runs on a
  `BiscuitBin` runner for this repository. If that run is red and T01 then requires
  `check`, every other lane is blocked until T01's workflows land. T01 stops instead of
  requiring a red check.
- **The release build in every `check`.** Stated in §4. Measure before weighing it.
- **Organisation settings.** `BiscuitBin` is an organisation; branch protection, Pages
  and GitHub App installation may need an organisation owner. T01 and T17 say so before
  acting.
- **Frozen files and follow-ups.** T02 and T03 are the lanes most likely to need a
  recipe changed; each change is a small `main` pull request, and T11 reconciles what
  accumulated.
- **Name squatting.** `alliumpy` is free today and a pending publisher does not reserve
  it. T14 is the first ticket that can take it; nothing earlier should wait on it.
- **lychee and typos over `tickets/`.** Ticket prose must pass typos and carry no
  relative links.

## 14. Adversarial review

P `tickets/CONVENTIONS.md` §14 at `bf51e0d`, verbatim, with two clauses changed: under
Phase 1 (a), "Deltas from L" reads "Deltas from P"; under "Network", the sources a brief
may carry read "the P, L, B, T and U files the ticket cites" where P's reads "the L, B
and T files". Nothing else differs.

A ticket marks each point where a mistake is expensive to undo with a bold
**Adversarial review** paragraph at the end of a step. There the agent gets a second
opinion from reviewers who did not write the change, and other subagents check each
finding and fix the valid ones before the work goes on. This is a procedure for the
agent running a ticket; it is unrelated to T05's `review-change` skill, which this
repository ships to its own contributors.

- **When.** At each checkpoint a ticket marks: before a file freezes, before each
  "Authorisation required" stop, after a design choice later steps build on, and before
  the ticket's final commit.
- **Who reviews.** Codex with `-m gpt-6-astra`, or Claude Code with
  `--model claude-opus-5-5`. Use the harness the executing agent is not, if it is on
  `PATH`, so that the review does not share the author's blind spots; otherwise use the
  same harness's preferred model. A weaker model is used only if neither is available,
  and the hand-back notes say so. In the agent's own harness, a fresh-context subagent on
  the preferred model is equivalent; this section does not prescribe any harness's
  subagent API. The commands, which the agent confirms with `--help` on the day, run from
  the worktree (`claude` takes no directory flag):

  ```sh
  codex exec -m gpt-6-astra -s read-only -C <worktree> \
    -o ai_tmp/review/<id>-<n>/findings-<lens>.md "<brief>"
  claude -p --model claude-opus-5-5 --permission-mode plan "<brief>" \
    > ai_tmp/review/<id>-<n>/findings-<lens>.md
  ```

  `<id>` is the ticket id, `<n>` the checkpoint's place among the ticket's checkpoints,
  counting from 1, and `<lens>` is `conformance` or `breakage`. A second round (below)
  writes beside the first with a `-2` suffix.
- **Phase 1, review.** Two reviewer subagents run in parallel, each with a fresh context
  and one lens:
  - **(a) Conformance.** The diff against the ticket's Goal, Files touched, acceptance
    criteria and the sections of this document it cites. Deltas from P beyond the stated
    ones. A frozen file or another lane's file touched.
  - **(b) Breakage.** How the gate could pass while the claim is false. A gate that
    cannot fire. What fails on a fresh clone, in CI, offline, or for a later lane. An
    acceptance criterion asserted but not shown. A verification command that would
    print a pass when it failed: a pipeline whose first command errored, so the filters
    print nothing; `|| true` on a line a claim rests on; a wait that succeeds on timeout;
    a 401, 403 or network error read as "absent"; a network denial with no negative
    control (§11). A verification command separates the producer from any filter that
    reads its output, checks each one's exit status, and keeps a positive control that
    must produce nonempty output, so a filter cannot return its expected exit after the
    producer failed.

  The brief gives the ticket's path, this document's path, `git diff main...HEAD` plus
  the uncommitted changes (or the artefact under review, such as a dry run or a list),
  and the checkpoint's questions. It does not give the author's reasoning or the
  hand-back notes' conclusions. Reviewers are read-only. Each finding has an id, a
  `file:line`, the claim, a concrete failure scenario, a severity (high, medium or low)
  and its evidence.
- **Phase 2, triage.** Separate subagents, neither the reviewers nor the executing agent,
  check every finding against the code, by running a command or reading the pinned
  source. Each finding is marked valid, with a fix written, or invalid, with the reason.
  The verdicts go to `ai_tmp/review/<id>-<n>/verdicts.md`. Subagents pass file paths to
  each other, not pasted text.
- **Phase 3, apply.** The triage subagents apply the valid fixes one at a time, never two
  writers at once. Then the executing agent re-runs the checkpoint's verification
  commands, and `just check` at the final checkpoint.
- **Scope guard.** A fix edits only files in the ticket's Files touched. A valid finding
  whose fix lies outside that list, in a frozen file or in another lane's file, is handed
  back under §11 and never applied. At an authorisation checkpoint the fixes change what
  the agent will ask for, and the agent still stops and asks.
- **Rounds.** If any high-severity finding was valid, one more review runs over the fix
  diff. Two rounds at most; anything still open goes into the ticket's Open points.
- **Network.** The review calls a model API. The ticket's checkpoint is the authorisation
  (§11, "Network"). It runs outside `just check`, so `check` still needs no network. A
  brief carries only this repository's content and the P, L, B, T and U files the ticket
  cites, never a credential.
- **Record.** The hand-back notes record, for each checkpoint: the harness and model, the
  findings, each verdict with a one-line reason, what was applied, what was handed back,
  and the re-run output, headed by the commit it ran at (§11). The raw files stay in
  `ai_tmp/` and are never committed.
