---
id: T07
title: "Handbook: every page, and decision records 0001 to 0013"
status: open
depends_on: [T00]
parallel_with: [T01, T02, T03, T05, S01]
branch: ticket/t07-handbook
estimated_size: L
---

# T07: Handbook: every page, and decision records 0001 to 0013

## Context

T00 registered every page and record in `docs/manifest.yml` and left a stub for each.
This lane writes the handbook pages `CONVENTIONS.md` §6 assigns to T07, each adapted from
the finished page of the same path in L (P's pages are stubs, so L's text is the
original), and the decision index with records 0001 to 0013 (`CONVENTIONS.md` §8).
Record 0014 stays T00's stub: S01 drafts it and T13 lands it. Wave-2 tickets write
records 0015 to 0017 themselves.

The work is in three parts, in order, each closed by its own review:

- **Part 1**, steps 1 to 6: the three project pages, the tutorial and the five how-to
  pages, including the new `how-to/install-and-run.md`.
- **Part 2**, steps 7 to 11: the five explanation pages (the new
  `explanation/packaging.md` among them), the seven reference pages and the two
  operations pages. The architecture page carries the argument this repository is built
  on: upstream's parser under an exact pin, a tested core over it, a thin pyo3 crate, and
  one wheel (`CONVENTIONS.md` §0, §9).
- **Part 3**, steps 12 to 17: the decision index and records 0001 to 0013.

L `docs/reference/documentation-contract.md` at `ccdd001` is the rulebook (frontmatter
equals the manifest entry, one owning page per topic, 40 words minimum, links that
resolve with exact case; P's page at `bf51e0d` is a stub); B's validator enforces it with
the kinds and audiences `CONVENTIONS.md` §6 lists. L `tickets/T07-handbook-a.md`, L
`tickets/T08-handbook-b.md` and L `tickets/T09-decisions.md` are the procedures for the
three parts, P `tickets/T07-handbook.md` is the same procedure adapted once already, and
the index is P `docs/decisions/README.md`'s table at `bf51e0d` (its prose is a stub) with
L `docs/decisions/README.md`'s prose at `ccdd001` adapted under step 2's rule.

Several facts parts 2 and 3 state are settled by other wave-1 lanes running at the same
time (T01's `pages.yml` condition and CI job names, T02's lint tables, T03's
`ruff.toml`, `mypy.ini` and `_alliumpy.pyi`, T05's skills, S01's CLI route). Write from
`CONVENTIONS.md` and L; where a lane's outcome could change a sentence, write the sentence
to the design and list it in the hand-back notes for T11 to reconcile. The pages describe
what exists on `main` when this lane runs: the `allium` command answers `--version` only
(T13 brings the rest), nothing is on PyPI (T14), nothing updates the pins (T17), and
GitHub Pages deploys only if the repository's visibility allows it (`CONVENTIONS.md` §1
fact 6).

`CONVENTIONS.md` §8 gives each record's file name, title, slug and source: seven carried
from P (0002 to 0008), each of which P carried from L, and six new (0001, 0009 to 0013).
A carried record opens "Carried from pachinko's decision NNNN at `bf51e0d`, which carried
libpawdoku's decision NNNN at `ccdd001`" and keeps the slug. The maintainer's decisions
behind the new records are `CONVENTIONS.md` §1, decisions 1 to 7, and the facts under
them.

## Goal

Twenty-three final pages and fourteen final decision files (the index and records 0001 to
0013) that describe this repository as it is after wave 1: a two-crate workspace that
ships one wheel, with the gate, the tools and the Python packaging `CONVENTIONS.md` §4
and §9 describe. The packaging argument is explained once, in `packaging.md`, and the
crate shape once, in `architecture.md`; every other page refers to them. Each record has
P's sections (Context, Decision, Consequences, What would reopen this, Related pages), is
true of this repository, and restates no other. `just check-docs` is green.

## Non-goals

- No page or record outside this lane's twenty-three pages, the index and records 0001 to
  0013; no manifest change and no new page (frozen); no edit to `docs/README.md` or to
  `docs/decisions/0014-cli-strategy.md`. A page that needs a different title, kind or
  audience is handed back to T00's follow-up, never changed in the manifest here.
- No CLI command described as working beyond `--version`, no sdist ruling, no release
  described as made, no Renovate described as installed. A page may say what a later
  ticket adds, in a sentence, naming the ticket.
- No decision the maintainer has not taken. Where a record would need one (0014's route,
  the sdist), it names the spike or ticket that takes it.
- No Allium language documentation. `terminology.md` gives the Allium terms one sentence
  each and points at upstream's documentation as plain text, never as a link.

## Files touched

| Path | Class | Content |
| --- | --- | --- |
| `docs/project/purpose-and-scope.md` | final | `CONVENTIONS.md` §6 |
| `docs/project/repository-map.md` | final | the tree of `CONVENTIONS.md` §3 |
| `docs/project/terminology.md` | final | the glossary seed |
| `docs/tutorials/first-change.md` | final | the test-first exercise across the core, the pyclass, the stub and the pytest case |
| `docs/how-to/install-and-run.md` | final | new: `uvx --from`, `uv tool install`, `pip`, the API, upstream's exit codes |
| `docs/how-to/develop-locally.md` | final | L's; two crates and the Python package, `py-develop`, `PYO3_PYTHON` |
| `docs/how-to/test-and-debug.md` | final | L's; nextest for the core, pytest and stubtest for the binding, `wheel-smoke` |
| `docs/how-to/maintain-dependencies.md` | final | L's; the upstream pin is a release, not an update; nothing updates the pins until T17 |
| `docs/how-to/deploy-to-github-pages.md` | final | both crates' rustdoc; the visibility condition |
| `docs/explanation/architecture.md` | final | upstream's parser, the core, the thin crate, the package; what S01 decides, what wave 2 adds |
| `docs/explanation/layering.md` | final | `alliumpy` -> `alliumpy-core` -> `allium-parser`; pyo3 only in the bindings crate |
| `docs/explanation/packaging.md` | final | new: one wheel, abi3 and `cp314t`, five targets, the static version, two licences, two manifests, the sdist ruling pending |
| `docs/explanation/quality-philosophy.md` | final | L's argument, this gate's examples |
| `docs/explanation/security-model.md` | final | supply chain, unsafe, cargo-deny, trusted publishing, untrusted inputs, the parity reference |
| `docs/reference/commands.md` | final | every recipe of the `Justfile` |
| `docs/reference/configuration.md` | final | every configuration file of `CONVENTIONS.md` §3, both manifests |
| `docs/reference/testing.md` | final | nextest, doctests, pytest, stubtest, the smoke, coverage scope, the insta rule, parity (T13) |
| `docs/reference/quality-gates.md` | final | the twenty-two gates |
| `docs/reference/documentation-contract.md` | final | L's rules verbatim; "Links that leave the repository" (L line 73) rewritten to name only `api.md`, `deploy-to-github-pages.md`, `install-and-run.md` |
| `docs/reference/agent-contract.md` | final | seven skills |
| `docs/reference/api.md` | final | the Python API from `_alliumpy.pyi`, rustdoc for both crates |
| `docs/operations/maintenance.md` | final | L's routine, plus "when upstream releases" naming T17 |
| `docs/operations/troubleshooting.md` | final | L's, minus wasm, plus the pyo3 entries |
| `docs/decisions/README.md` | final | the index, P's format |
| `docs/decisions/0001-one-wheel-two-crates.md` | final | new: `CONVENTIONS.md` §1 decision 2, fact 4 |
| `docs/decisions/0002-hook-runner-and-checkers.md` | final | P 0004 |
| `docs/decisions/0003-apache-2-0-with-upstream-mit.md` | final | P 0006, extended: the wheel carries both texts (`CONVENTIONS.md` §1 fact 7) |
| `docs/decisions/0004-dependency-policy.md` | final | P 0007; names 0011 as the one exception |
| `docs/decisions/0005-rust-quality-gate.md` | final | P 0009; the bindings crate's own lint table |
| `docs/decisions/0006-tool-manager.md` | final | P 0011; the Python tools pixi now owns |
| `docs/decisions/0007-metrics-gate.md` | final | P 0012, thresholds kept, module rules waiting for modules |
| `docs/decisions/0008-api-reference-on-github-pages.md` | final | P 0013, conditioned on visibility |
| `docs/decisions/0009-pypi-name-alliumpy.md` | final | new: `CONVENTIONS.md` §1 decision 2, facts 10 and 11 |
| `docs/decisions/0010-version-tracks-upstream.md` | final | new: `CONVENTIONS.md` §1 decision 4 |
| `docs/decisions/0011-exact-pin-on-allium-parser.md` | final | new: `CONVENTIONS.md` §1 fact 5, §13 |
| `docs/decisions/0012-abi3-wheels-and-platforms.md` | final | new: `CONVENTIONS.md` §1 decision 6, facts 3 and 9 |
| `docs/decisions/0013-no-spec-gate-no-allium-skills.md` | final | new: `CONVENTIONS.md` §1 decision 5 |
| `tickets/T07-handbook.md` | ticket | `status:` and hand-back notes |

## Steps

1. Create the worktree after T00 has merged. Run `just check` on the untouched worktree
   and quote its last line as the baseline.
2. **Part 1: project, tutorial and how-to pages.** For each carried part-1 page, read L's
   page of the same path at `ccdd001` and `CONVENTIONS.md` §6's adaptation column. Keep
   L's structure and every sentence that is still true; rewrite what names sudoku,
   pawdoku, pachinko, effects, specifications, wasm, `no_std`, L's modules or L's URLs.
   Where L says `just initialize` normalises formatting (`develop-locally.md`,
   `commands.md`, `first-change.md`), drop that clause (`CONVENTIONS.md` §5). Parts 2
   and 3 apply the same rule to their pages and records.
3. **`terminology.md`.** One entry each for: the repository, the core crate
   (`alliumpy-core`), the bindings crate (`alliumpy`), the Python package, the wheel, the
   sdist, abi3, the console script, upstream, the upstream pin, parity, a gate, a recipe.
   Then the Allium terms the API exposes, one sentence each: module, diagnostic,
   severity, finding; each says that upstream's documentation defines it and that this
   repository converts, never reinterprets (`CONVENTIONS.md` §7 invariant 1). Each entry
   says which word to use and which to avoid, in L's style.
4. **`install-and-run.md`.** The three installation forms (`uvx --from alliumpy allium`,
   `uv tool install alliumpy`, `pip install alliumpy`) written as what they will do once
   T14 has published, each under one sentence saying so; the Python API in five lines,
   from `_alliumpy.pyi`; the exit codes of `allium check` as upstream defines them
   (`CONVENTIONS.md` §1 fact 5); and one paragraph saying that on this `main` the command
   answers `--version` only and that T13 brings the rest. Run `just py-develop`, then run
   the five API lines with `.pixi/envs/default/bin/python -I -c '...'` from the worktree
   root, and quote the command, its output and its exit status (`CONVENTIONS.md` §11).
5. **`first-change.md`.** An exercise a contributor can follow again on any later `main`,
   test-first as L's is, across the two crates and the stub. In
   `crates/alliumpy-core/src/lib.rs`, add a unit test that reads a new field on
   `Diagnostic` (the tutorial names it: `end_col: u32`, the one-based column of the
   span's end, converted through `SourceMap` as `col` is) and watch `just test` fail to
   compile; add the field and set it where `parse` builds the struct, and watch
   `just test` pass. Add a pytest case under `crates/alliumpy/tests/` that reads the
   attribute and watch `just py-test` fail with `AttributeError` (pytest reads the built
   module, never the stub); in `crates/alliumpy/src/lib.rs`, add the attribute to the
   `Diagnostic` pyclass and its `From` impl, watch `just py-test` pass and
   `just py-stubtest`, which rebuilds through `py-develop`, report the attribute as
   missing from the stub; add it to `_alliumpy.pyi`, then `just check`. The field joins
   `__repr__` last, before `)`, and the T00 `repr` assertion in
   `crates/alliumpy/tests/test_parse.py` moves with it (`CONVENTIONS.md` §9, every field
   in order). Core
   `Diagnostic` is `#[non_exhaustive]` and the Python class is a separate pyclass
   (`CONVENTIONS.md` §9), so a core field alone fails nothing in the binding; the tutorial
   says so. Follow it yourself, start to finish, in a scratch worktree of this branch
   (`git worktree add --detach ai_tmp/tutorial HEAD`) after `just initialize` there
   (network, authorised by this step); quote the commands and failures, then remove the
   worktree (`git worktree remove --force ai_tmp/tutorial`) before part 1 is committed; a
   tutorial no one has run is not done.
6. **`deploy-to-github-pages.md`.** The `pages.yml` T01 writes in parallel (write from
   `CONVENTIONS.md` §10 and T01's ticket text) and the `site` recipe, with the condition:
   the deploy job runs only when the repository is public (`CONVENTIONS.md` §1 fact 6,
   §10), and the URL is the one `gh api repos/BiscuitBin/alliumpy/pages --jq .html_url`
   prints once Pages exists, written here as `https://biscuitbin.github.io/alliumpy/` with
   a note to confirm it. Then `just check-docs`, `just check`, the part-1 review,
   `just check` again if fixes landed, then commit part 1.

   **Adversarial review** (`CONVENTIONS.md` §14): part 1's diff and step 5's transcript.
   Ask: which sentence kept from L is false in this repository; which sentence describes
   a command, a PyPI release or a Pages site as existing on this `main`; whether a
   contributor on a later `main` can replay the tutorial exactly as written.

7. **Part 2, `architecture.md`.** Upstream's `allium-parser` under an exact pin
   (decision 0011); `alliumpy-core`, the conversion layer where Rust is tested and the
   floor is measured; `alliumpy`, the thin pyo3 crate with its own lint table; the Python
   package under `crates/alliumpy/python/` with the console script (decision 0001). The
   rule for what goes where, from `CONVENTIONS.md` §9 "The shape". What S01 decides: how
   the `allium` command gets into the wheel, named as open, with the three options of
   `CONVENTIONS.md` §1 decision 3 and a pointer at record 0014. What wave 2 adds, one
   sentence each, naming the ticket and not described as existing: the command (T13), the
   release (T14), mutation testing, benchmarks and fuzzing (T15), Renovate (T17). T13
   makes its sentence present tense when it lands (`CONVENTIONS.md` §6, and T14 its own);
   the T15 and T17 sentences point at `testing.md` and `maintenance.md`, which those
   tickets edit.
8. **`layering.md` and `packaging.md`.** Layering: Cargo enforces `alliumpy` ->
   `alliumpy-core` -> `allium-parser`; pyo3 appears only in `alliumpy`; Python only under
   `python/`, `tests/` and `scripts/` (`CONVENTIONS.md` §7 invariant 2 for the crate
   direction and pyo3; §3 for where Python lives). Packaging, from
   `CONVENTIONS.md` §9 in full: one wheel; `abi3-py311` plus the `cp314t` wheel; the five
   targets and musllinux, built by the release matrix only, with `just check` building
   the developer's platform and CI the 3.11 floor; the static version and `.postN`
   (decision 0010); the two licence texts (decision 0003); the two manifests and which
   owns what (`CONVENTIONS.md` §1 fact 2); the sdist as S01's ruling, pending.
9. **`quality-philosophy.md` and `security-model.md`.** L's argument verbatim where it
   holds; L's sudoku examples replaced with this gate's: the offline wheel smoke, the
   positive controls on the linters, the coverage floor on a small denominator,
   byte-for-byte parity (T13, named as arriving). Security: supply chain (the exact pin,
   `--locked`, cargo-deny, trusted publishing with no token anywhere),
   `forbid(unsafe_code)` in both crates, untrusted input to the parser (a `.allium` file
   is data), the parity reference built from crates.io into a root off `PATH` and never
   downloaded (`CONVENTIONS.md` §9, §11 "Untrusted material").
10. **The reference pages.** `commands.md` lists every recipe in the `Justfile` with its
    comment's meaning (the `just --summary` loop in Verification is the check), the Python
    recipes included; `quality-gates.md` the twenty-two gates of `CONVENTIONS.md` §4 in
    order; `configuration.md` every configuration file in `CONVENTIONS.md` §3, both
    `pyproject.toml` files and what each owns, `ruff.toml`, `mypy.ini`,
    `scripts/version_check.py`, both lint tables; `testing.md` per L, plus pytest,
    stubtest and the smoke for the binding, the coverage scope (`CONVENTIONS.md` §9), the
    insta rule from L `tickets/T29-snapshot-harness.md` (a snapshot shows a value to a
    reviewer and detects change; it never proves a behaviour, which keeps its own
    asserting test) with the note that `insta` arrives with the first snapshot, and parity
    named as T13's; `api.md` lists every name `alliumpy/__init__.py` re-exports, each as
    `_alliumpy.pyi` (canonical) describes it, noting that
    `alliumpy._alliumpy.ALLIUM_VERSION_STRING` serves the console script and stubtest only
    and is not public API (`CONVENTIONS.md` §9), then rustdoc for both crates, `just doc`,
    `just site`, and Pages when enabled; `agent-contract.md` the seven skills of
    `CONVENTIONS.md` §7; `documentation-contract.md` L's rules verbatim, with its "Links
    that leave the repository" section rewritten to name the three outward pages only; no
    other page or record carries a URL (the acceptance `rg -l 'https?://' docs/` checks
    it).
11. **The operations pages.** L's, with this repository's names; maintenance gains "when
    upstream releases", pointing at T17's runbook once it exists and until then at
    `CONVENTIONS.md` §13's first bullet in prose; troubleshooting loses the wasm entries
    and gains the pyo3 ones `CONVENTIONS.md` §6 lists. Then `just check-docs`,
    `just check`, the part-2 review, `just check` again if fixes landed, then commit
    part 2.

    **Adversarial review** (`CONVENTIONS.md` §14): part 2's diff, since part 1's commit.
    Ask: which fact contradicts `CONVENTIONS.md`, the `Justfile` or `_alliumpy.pyi`;
    whether `quality-gates.md` lists the gates in `CONVENTIONS.md` §4's order and
    `commands.md` every recipe `just --list` prints; which sentence waits on S01, T02 or
    T03 and is not yet listed for T11; which sentence describes a wave-2 deliverable as
    existing.

12. **Part 3, the carried records.** For each of 0002 to 0008, read P's stub at
    `bf51e0d` for the opening sentence and the slug, then L's finished record at
    `ccdd001` under the number P's stub names (L 0004, 0006, 0007, 0009, 0011, 0013,
    0016). Keep its argument; remove what is sudoku, no_std, wasm, effects or
    specifications; rewrite what names L's or P's crates or URLs. Keep the chain in the
    opening sentence ("Carried from pachinko's decision 0004 at `bf51e0d`, which carried
    libpawdoku's decision 0004 at `ccdd001`").
13. **0003, 0004, 0005, 0006 and 0008, the extensions.** 0003 adds why upstream's MIT
    text ships in the wheel beside this repository's Apache-2.0 and where the copies live
    (`CONVENTIONS.md` §1 fact 7, §9 "Licences"). 0004 names `allium-parser` as the one
    exact pin and points at 0011. 0005 adds the bindings crate's own `[lints]` table and
    why a member cannot lower a workspace `forbid` (`CONVENTIONS.md` §3). 0006 adds the
    Python tools pixi owns (maturin, uv, pytest, ruff, mypy) and why `rust` is still
    absent. 0008 adds the condition: the deploy runs only when the repository is public,
    and what reopens it is a change of visibility or plan.
14. **0001, 0009, 0010.** 0001: why one wheel from two crates, from `CONVENTIONS.md` §1
    decision 2 and fact 4 (a cdylib-only workspace leaves the gates empty); what would
    reopen it: a second consumer that needs the core without Python, or a CLI-only
    package. 0009: why `alliumpy` and not `allium` or `allium-cli` (facts 10 and 11); the
    `--from` form; what reopens it: a PEP 541 grant of `allium`. 0010: the wheel version
    tracks upstream, `.postN` for packaging fixes, the static `[project] version`,
    `version-check`; what reopens it: an upstream change that this repository must ship
    ahead of or behind.
15. **0011, 0012, 0013.** 0011: the exact pin, from fact 5 and §13 (pre-release upstream,
    signatures that grow, two to five releases a month), and why Renovate leaves it alone
    (T17); what reopens it: an upstream stability promise. 0012: `abi3-py311`, the
    `cp314t` wheel, the five targets and musllinux, the Justfile's POSIX limit (facts 3
    and 9); what reopens it: a platform request or a new Python floor. 0013: no
    specification gate and no Allium skills, because this repository builds an `allium`
    and a second one on `PATH` would shadow it (decision 5); what reopens it: a way to
    run a spec gate through the wheel itself.
16. **The index.** P's table and L's prose (Context), fourteen rows (0014 with its stub
    title), plus a line that 0015 to 0017 are written by T14, T15 and T17.
17. `just check-docs`, `just check`, the final adversarial review, `just check` again if
    fixes landed, then commit.

    **Adversarial review** (`CONVENTIONS.md` §14): part 3's diff, since part 2's commit.
    Ask: which carried argument still leans on `no_std`, effects or sudoku; which
    record's "What would reopen this" is empty or untestable; whether every slug and
    title matches `CONVENTIONS.md` §8's table and the manifest, list order included;
    whether 0014 is untouched.

## Acceptance criteria

- `just check-docs` is green, and every page's and record's frontmatter equals its
  manifest entry, including list order.
- `rg -n -i 'pachinko|pawdoku|sudoku|wasm|no_std|effects|docs/specs' docs/project docs/tutorials docs/how-to`
  prints nothing, or only a sentence naming P or L as the source.
- The tutorial was followed end to end, and the hand-back notes quote it.
- Every recipe `just --list` prints appears in `docs/reference/commands.md`, and every
  gate in `CONVENTIONS.md` §4 in `docs/reference/quality-gates.md`, in order.
- `rg -l 'https?://' docs/` lists exactly `docs/how-to/deploy-to-github-pages.md`,
  `docs/how-to/install-and-run.md` and `docs/reference/api.md`, the three pages
  `documentation-contract.md` names; every other page and record names upstream in
  prose (`juxt/allium-tools`, crates.io `allium-parser 3.6.1`), never by URL.
- `rg -n -i 'pachinko|pawdoku|sudoku|wasm|no_std|effects|docs/specs' docs/explanation docs/reference docs/operations`
  prints nothing, or only a sentence naming P or L as the source, or `agent-contract.md`'s
  list of the six phrases B requires in `AGENTS.md` (`CONVENTIONS.md` §1 fact 1).
- Every carried record opens with the carried-from chain; every new record has none;
  `docs/decisions/0014-cli-strategy.md` is byte-identical to T00's.
- `rg -n -i 'sudoku|wasm|no_std|effects' docs/decisions` prints nothing.
- `just check` is green.
- The adversarial reviews in Steps ran (`CONVENTIONS.md` §14), and every valid finding is
  fixed or handed back.

## Verification

```sh
just check-docs
just --list
just --summary
for r in $(just --summary); do rg -q -F "\`$r\`" docs/reference/commands.md || echo "missing recipe: $r"; done
for g in check-toolchain lock-check lint fmt-check toml-check clippy metrics features test-doc coverage doc deny deps-unused py-lint py-typecheck py-test py-stubtest wheel-smoke version-check check-docs check-agents snapshots-check; do rg -n -F "\`$g\`" docs/reference/quality-gates.md | head -1; done
rg -c -i 'pachinko|pawdoku|sudoku|wasm|no_std|effects|docs/specs' docs/decisions/000[2-8]-*.md
rg -n -i 'pachinko|pawdoku|sudoku|wasm|no_std|effects|docs/specs' docs/project docs/tutorials docs/how-to
rg -n -i 'pachinko|pawdoku|sudoku|wasm|no_std|effects|docs/specs' docs/explanation docs/reference docs/operations
rg -n -i 'sudoku|wasm|no_std|effects' docs/decisions
rg -l 'https?://' docs/
ls docs/decisions/000[2-8]-*.md
rg --files-without-match 'Carried from pachinko' docs/decisions/000[2-8]-*.md
ls docs/decisions/0001-*.md docs/decisions/0009-*.md docs/decisions/001[0-3]-*.md
rg -l 'Carried from' docs/decisions/0001-*.md docs/decisions/0009-*.md docs/decisions/001[0-3]-*.md
ls docs/decisions/0014-cli-strategy.md
git diff --exit-code origin/main -- docs/decisions/0014-cli-strategy.md
just check
```

`just --summary` alone must print a non-empty list (the positive control); the recipe
loop must then print nothing; the gate loop must print twenty-two lines whose line
numbers increase, matching `CONVENTIONS.md` §4's order. `commands.md` and
`quality-gates.md` write each recipe and gate name as a code span so these loops find
them. The `rg -c` must print seven non-zero counts and exit 0: the positive control of
`CONVENTIONS.md` §11 for the three negative searches after it, each of which must print
nothing and exit 1, or only the lines its acceptance criterion allows. The first `ls`
must list seven files and the `rg --files-without-match` after it must print nothing and
exit 1; the second `ls` must list six files and the `rg -l` after it must print nothing
and exit 1; the third `ls` must list the one file (its positive control), and the
`git diff --exit-code` must print nothing and exit 0 against `origin/main`, after the
`git fetch origin` `README.md` step 6 names, never against a local `main`.

## Hand-back notes

### Part 1 evidence

Baseline: commit `5b76af6` (untouched), `PATH="$HOME/.cargo/bin:$PATH" just check`,
exit 0, last line `All checks passed and the worktree is unchanged.` The initial shell
resolved pixi's global cargo; putting rustup first fixed that environment issue. The
sandbox initially denied prek's existing cache; the same check passed with approved
cache access. No gate was weakened.

Tutorial: detached worktree created with `git worktree add --detach ai_tmp/tutorial HEAD`
at `5b76af6`; `just initialize` exited 0 and printed `Secondary worktree: skipping
install-hooks.` Commands below used rustup first on PATH. All edits were confined to
the scratch worktree, and logs remain ignored under `ai_tmp/`.

| Command and state | Observed output | Exit |
| --- | --- | --- |
| `just check`, untouched scratch | `All checks passed and the worktree is unchanged.` | 0 |
| `just test`, new core assertion only | `error[E0609]: no field end_col on type Diagnostic` | 101 |
| `just test`, core field and span-end conversion | 7 core tests passed, 1 doctest passed | 0 |
| `just py-test`, new Python assertion only | `AttributeError: ... Diagnostic ... has no attribute 'end_col'` | 1 |
| `just py-test`, getter and repr updated | 6 passed | 0 |
| `just py-stubtest`, runtime ahead of stub | `Diagnostic.end_col is not present in stub` | 1 |
| `just py-stubtest`, documented property added | `Success: no issues found in 1 module` | 0 |
| `just check`, initial final run | Ruff PLR2004 on literal expected column | 1 |
| `just check`, expected column named as in final tutorial | `All checks passed and the worktree is unchanged.` | 0 |

The existing binding stores the core diagnostic rather than copying fields through a
From impl; the tutorial explains that actual shape and what a later From impl requires.
The expected exclusive end column 2 was verified against the pinned parser by the test.
The full tutorial gate measured 100% core lines. The worktree was removed with
`git worktree remove --force --force ai_tmp/tutorial` (exit 0); the second force was
needed for Supacode's automatic lock. No experimental field remains in deliverables.

API proof at `5b76af6` with uncommitted documentation: `just py-develop`, exit 0, then:

```sh
.pixi/envs/default/bin/python -I -c 'import alliumpy
diagnostics = alliumpy.parse("-- allium: 1\n?\n")
first = diagnostics[0]
print(first.line, first.col, first.severity)
print(alliumpy.ALLIUM_VERSION)'
```

Output (exit 0):

```text
2 1 error
3.6.1
```

The rendered example adds the formatter-required blank line after the import; there
are five executable statements. Part-1 check-docs exited 0. An early full gate caught
that blank line; another run correctly detected an edit made while checking. Both were
rerun against a stable tree. Final part-1 gate evidence is recorded with its commit below.

Part-1 review: fresh-context Codex subagents, `gpt-6-astra`, separate conformance and
breakage lenses. C1/B2 (Python described as exact) valid: Python uses a patch range;
C2 (old decision label) valid: label now 0004; B1 (offline check detects moved remote tag)
valid: local consistency cannot observe remote changes. A separate `gpt-6-astra` triage
agent checked pinned L source and local recipes and applied these three fixes sequentially.
No high findings, no second round needed. Raw findings/verdicts are under
`ai_tmp/review/T07-1/`, outside deliverables.

## Open points

- If a page's manifest title or audience proves wrong while writing it, hand the change
  back as a T00 follow-up on `main` rather than editing `docs/manifest.yml` here.
- Whether `terminology.md` should name upstream's diagnostic codes. Recommend not: they
  are upstream's and move between releases; the page points at upstream's documentation.
