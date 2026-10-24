---
id: T05
title: "Agent contract: AGENTS.md, seven house skills, the bridges"
status: open
depends_on: [T00]
parallel_with: [T01, T02, T03, T07, S01]
branch: ticket/t05-agent-contract
estimated_size: M
---

# T05: Agent contract: AGENTS.md, seven house skills, the bridges

## Context

T00 left an `AGENTS.md` stub carrying the six phrases B requires, seven skill stubs with
their final frontmatter, and fourteen frozen bridges. This lane writes the contract for a
repository that packages upstream's parser and command as one wheel: P `AGENTS.md` and
six of P's seven house skills (`spec-change` is not carried, `CONVENTIONS.md` §1
decision 5), adapted as `CONVENTIONS.md` §7 states, plus one new skill, `python-change`,
for which there is no original.

P's T05 is done, so the built files are the source, not the ticket text: P `AGENTS.md`,
and P `.agents/skills/<name>/SKILL.md` for `plan-change`, `rust-change`, `review-change`,
`review-docs`, `fix-quality` and `project-check`, all at `bf51e0d`. P
`tickets/T05-agent-contract.md` is the procedure, and its hand-back notes record the
review findings P met (a dropped authority rule, a skill that did not do what `AGENTS.md`
said it did, a dispatch line that routed a hook nowhere): read them before step 2 so
that none recurs. B `src/biscuit_games_tooling/validate_agents.py` at `6c5c07f` is what
the result must satisfy: the six required phrases (lines 47-54), a 300-word floor, a
frontmatter of exactly `name` and `description` with a description of eight words or
more, a body that contains both `AGENTS.md` and the string `just` followed by a space,
and bridges whose frontmatter equals the canonical file's and whose body is
`BRIDGE_BODY` (lines 23-26).

This repository has no `docs/specs/`, no effects boundary and no Allium skills
(`CONVENTIONS.md` §1 decision 5). B still requires the phrase `docs/specs/`, so
`AGENTS.md` says truthfully that the specifications `allium` checks live in other
repositories (`CONVENTIONS.md` §1 fact 1).

## Goal

`AGENTS.md` states this repository's nine invariants (`CONVENTIONS.md` §7) verbatim and
nothing P-only, in the shape §7 gives: the always-on core, the authority rules with the
exact list of network recipes, the hand-back rule, seven `<important if>` blocks, then
Provenance. The seven house skills are adapted to a core crate, a bindings crate and a
Python package, with `python-change` written new. `just check-agents` prints
`Validated AGENTS.md, 2 adapters, and 7 skills.`

## Non-goals

- No change to `CLAUDE.md`, `.github/copilot-instructions.md` or any bridge (frozen), and
  none to any skill's frontmatter, which the bridges repeat and T00 wrote final
  (`CONVENTIONS.md` §7). A description that reads wrong is handed back, not edited.
- No new skill beyond `python-change` and no removed skill: the seven are fixed by T00's
  stubs, and `bg-validate-agents` counts directories.
- No `.claude/settings.json`: B tolerates it and nothing here needs it
  (`CONVENTIONS.md` §1 fact 1).
- No handbook page. `docs/reference/agent-contract.md` is T07's, written from
  `CONVENTIONS.md` §7 in parallel; this lane records in its hand-back notes every fact
  the built files settle differently from §7, so that T11 reconciles the page.
- No recipe that does not exist on `main` today. The parity recipes are T13's; where
  `AGENTS.md` must mention them (invariant 1, the network list), it says "from T13".
- No Allium skill, no `allium-skill-reference/`, no `skills-lock.json`.

## Files touched

| Path | Class | Content |
| --- | --- | --- |
| `AGENTS.md` | final | P's content, adapted per `CONVENTIONS.md` §7 |
| `.agents/skills/plan-change/SKILL.md` | final | P's, minus specifications and effects; the upstream-decides rule |
| `.agents/skills/rust-change/SKILL.md` | final | body: two crates with a fixed direction, the bindings crate's own lint table, the API's shape |
| `.agents/skills/python-change/SKILL.md` | final | new: the stub first, three artefacts together, the six Python gates of `CONVENTIONS.md` §7 |
| `.agents/skills/review-change/SKILL.md` | final | the nine invariants of `CONVENTIONS.md` §7 in the checklist |
| `.agents/skills/review-docs/SKILL.md` | final | P's |
| `.agents/skills/fix-quality/SKILL.md` | final | one dispatch line for each of the twenty-two gates of `CONVENTIONS.md` §4 |
| `.agents/skills/project-check/SKILL.md` | final | gate numbers of `CONVENTIONS.md` §4; green as `CONVENTIONS.md` §11 defines it |
| `tickets/T05-agent-contract.md` | ticket | `status:` and hand-back notes |

## Steps

1. Create the worktree after T00 has merged (`README.md`, "How to pick up a ticket");
   `just initialize` (network, authorised); then `just check` on the untouched worktree,
   its last line quoted as the baseline (`CONVENTIONS.md` §11).
2. **`AGENTS.md`.** Start from P `AGENTS.md` and adapt it as `CONVENTIONS.md` §7 states.
   In order: the identity paragraph (one wheel; the parser is upstream's and the command's
   behaviour is upstream's; this file decides *how* it is packaged, and a behaviour
   difference from upstream is a defect here unless a decision record says otherwise; the
   untrusted-data rule, which here names upstream source among the untrusted inputs);
   `## Project map` with §7's entries, saying where each kind of test lives (unit tests
   and doctests in `crates/alliumpy-core/src/`, pytest under `crates/alliumpy/tests/`, the
   smoke and lint fixtures under `tests/fixtures/`); `## Invariants` holding §7's nine
   verbatim, then one sentence saying invariant 4 is enforced by the workspace lint table
   in the core and the crate's own table in the bindings crate; then P's authority
   paragraph with the network list exactly as §7 gives it, the parity reference recipe
   marked "from T13", and the sentence that no workflow publishes yet reworded: once
   `release-pypi.yml` exists (T14) a tag is a release, and once Pages deploys from `main`
   (decision 0008) a push there is a deployment; then P's change-workflow paragraph; then
   the hand-back rule (rerun the one recipe `just check` named and read only its first
   failure; hand back only when `just check` ends with
   `All checks passed and the worktree is unchanged.` and `git status --short` is empty).
   Then the seven blocks of §7, each naming only the recipes and the skill its task uses:
   - Rust under `crates/`: `rust-change`, `review-change`; `just fmt-check`, `just
     clippy`, `just test`, `just coverage`, `just doc`; a public type in the core is part
     of the Python API's shape, so the stub and a pytest case move with it.
   - Python under `crates/alliumpy/python/`, `crates/alliumpy/tests/`, `tests/` or
     `scripts/`: `python-change`; `just py-lint`, `just py-typecheck`, `just py-test`,
     `just py-stubtest`, `just wheel-smoke`.
   - Bumping the upstream pin or the version: it is a release, not an update (decisions
     0010 and 0011); `just version-check` fails a bare pin bump by design; the runbook is
     T17's and, until it exists, the block says so.
   - A page under `docs/`: `review-docs`; `just check-docs`.
   - The agent surface: bridges stay thin and repeat the frozen frontmatter; `just
     check-agents`.
   - A failing gate, or handing back: `fix-quality`, `project-check`; `just fix` formats
     (cargo fmt, taplo, ruff); never disable a gate or lower a threshold.
   - Picking up a ticket: `plan-change`; P's text.

   `## Provenance` last: carried by hand from pachinko at `bf51e0d`, which carried
   libpawdoku at `ccdd001`; the deviations recorded in decisions 0004 and 0005; the
   sentence containing `docs/specs/` (this repository checks Allium specifications for
   other repositories and keeps none under a `docs/specs/` of its own); and P's sentence
   containing `runes`. Every recipe named must exist in the `Justfile`, except the two
   marked "from T13". About 1000 words; P landed at 1300 and said why.
3. **The carried skills.** Adapt each from P's, per `CONVENTIONS.md` §7's table:
   - `plan-change`: step 1 reads `AGENTS.md` and upstream's documentation for the
     behaviour in question, not a specification module; step 4 becomes "if behaviour
     changes, it is upstream's to change: a difference from `allium-cli` at the pin is a
     defect here unless a decision record says otherwise (invariant 1)"; step 5's
     boundaries are the crate direction (invariant 2), the Python API's shape (the stub
     is canonical) and a new topic's owning page; no `plan-spec`, no effect trait.
   - `rust-change`: step 1 names the two crates and the direction Cargo enforces, and that
     pyo3 appears only in `crates/alliumpy`; step 2 (the clause) becomes "find upstream's
     behaviour: for a conversion, read how `allium-cli` computes the same value and
     assert it in a test"; step 3 (effects) becomes the lint-table rule: the core
     inherits the workspace table, the bindings crate has its own, and a lint pyo3's
     macro output trips is allowed there with a comment naming the macro, never in the
     workspace table; step 4's test locations are the core's modules, its doctests and,
     for a public item the binding exposes, a pytest case; step 5 adds stable `Display`
     text (invariant 3); step 7 runs `just fmt-check`, `just clippy`, `just test`, `just
     coverage`, then `just check`.
   - `review-change`: step 1 reads `AGENTS.md`, `_alliumpy.pyi` and upstream's behaviour
     at the pin for the value in question, not a specification module; step 2 checks §7's
     nine invariants one at a time, named as they are written; step 3 checks the change
     against upstream's behaviour at the pin (a reinterpreted diagnostic, a reordered
     field, a different exit code is a finding); step 4's evidence is a unit test in the
     core, a pytest case for an exposed item and stubtest for a stub change, not a fake;
     step 5 checks the boundaries of invariant 2 and that no public type lost
     `#[non_exhaustive]` or `Clone`; a change to `_alliumpy.pyi` without the matching
     Rust and pytest change is a finding.
   - `review-docs`: P's.
   - `fix-quality`: P's dispatch lines minus `effects`, `check-specs` and `analyse-specs`;
     the `lint` line drops `check-specs` and `analyse-specs` from its hook list, routes
     `py-lint` and `py-typecheck` hooks to their gates' lines and keeps the remaining
     hooks; `metrics` is P's; the `clippy` line: a lint wrong for the core is changed in
     the workspace table, one that pyo3's macro output trips is set to `allow` in
     `crates/alliumpy/Cargo.toml`'s own `[lints]` table with a comment naming the macro,
     never in the workspace table; new lines for `py-lint` (`just fix` runs ruff's fixers;
     a rule wrong for one line gets a `# noqa: RULE` with a reason, never an
     `extend-ignore` in `ruff.toml` without a comment and a review), `py-typecheck` (fix
     the type, never `# type: ignore` without a code and a reason; never loosen `strict`),
     `py-test` (fix the binding or the test; `just py-test` rebuilds the extension first,
     so a stale `.so` beside `__init__.py` only explains a bare `pytest` run: use
     `just py-test`), `py-stubtest` (the stub and the module disagree: change whichever is
     wrong, never add an allowlist entry without a reason beside it), `wheel-smoke` (two
     wheels in `dist/` means something wrote there after `just wheel` emptied it: rerun
     `just wheel-smoke`; a missing `uv` means the pixi environment is incomplete and
     `just initialize`, a network recipe that needs explicit authorization, rebuilds it; a
     network error means the recipe reached out, which is a defect in the recipe),
     `version-check` (five copies of one version disagree: the message names the two; a
     bare `allium-parser` bump is a release, see decision 0010); and the `deny` line names
     decision 0004.
   - `project-check`: P's, with the prerequisites of this repository (the pixi
     environment's maturin, uv, pytest, ruff, mypy; no `allium` binary in `.tools/bin`),
     the gate numbers of §4 (cargo-hack before gate 8, rustqual before gate 7), and the
     last step as P's: green as `CONVENTIONS.md` §11 defines it.
4. **`python-change`**, new, in the register and length of `rust-change`:
   1. Read `AGENTS.md` and `crates/alliumpy/python/alliumpy/_alliumpy.pyi`. The stub is
      the canonical description of the Python API; what it does not describe does not
      exist to a user.
   2. Decide where the change lands: a conversion or a constant is the core's
      (`rust-change`); a class, function or exception exposed to Python is the bindings
      crate's `src/lib.rs`; a re-export is `__init__.py`; the console script is
      `_cli.py`, whose behaviour is upstream's (invariant 1), so a change there is a
      parity change and goes through `just parity` (from T13).
   3. Change the three artefacts together: the stub, the Rust binding and the pytest case
      under `crates/alliumpy/tests/`. Write the pytest case first and watch it fail.
   4. Every class is `#[pyclass(frozen, eq, hash)]` and `Send + Sync`, with a `__repr__`
      in `CONVENTIONS.md` §9's form; every error reaches Python as `AlliumError` with
      the `Display` text (invariant 3). Nothing derives
      `__version__` from `ALLIUM_VERSION_STRING` or the reverse (decision 0010).
   5. Run `just py-lint`, `just py-typecheck`, `just py-test`, `just py-stubtest`,
      `just wheel-smoke` and `just version-check`, in that order; a stubtest failure is a
      disagreement to resolve, never an allowlist entry without a reason; then
      `just check`.
   6. Report by `file:line`: what changed in the stub, the binding and the test, and which
      upstream behaviour it reproduces.
5. **The inventory and the phrases.** Confirm each skill body contains `AGENTS.md` and a
   `just` recipe invocation (B checks for the string `just` followed by a space); that
   no frontmatter changed (the frontmatter loop in Verification prints nothing); that no
   bridge or adapter changed (the `git diff --exit-code --stat` line in Verification
   prints nothing and exits 0); and that each of B's six phrases appears outside every
   block (the phrase loop in Verification prints nothing). The Verification block begins
   with `mkdir -p ai_tmp`, which the scratch files need.
6. `just check-agents`, `just check-docs`, `just check`, the final adversarial review,
   `just check` again if fixes landed, then commit.

   **Adversarial review** (`CONVENTIONS.md` §14): the lane's diff. Ask: whether
   `AGENTS.md` carries the nine invariants of `CONVENTIONS.md` §7 verbatim; which of B's
   six phrases depends on a block's wording, so that deleting every block would lose it;
   which block or skill names a recipe that `CONVENTIONS.md` §4 does not define and that
   is not marked "from T13"; whether any skill contradicts an invariant (a skill that lets
   the bindings crate carry a Rust test, that lets `_cli.py` differ from upstream, or
   that treats an `allium-parser` bump as a dependency update); whether `AGENTS.md` says
   anything false about the tree on `main` today (a parity recipe, a release workflow, a
   Pages deployment).

## Acceptance criteria

- `just check-agents` prints `Validated AGENTS.md, 2 adapters, and 7 skills.`
- The acceptance `rg` in Verification (the one whose pattern names P's sources, P's
  specification gates and recipes, `skill-reference` and `skills-lock`) prints only the
  Provenance lines that name the sources and the one `docs/specs/` sentence
  `CONVENTIONS.md` §7 requires; the hand-back notes list each printed line.
- `rg -c '^<important if="' AGENTS.md` prints `7`, and each of B's six phrases appears
  outside every block (the phrase loop in Verification prints nothing).
- Every gate of `CONVENTIONS.md` §4 heads a dispatch line (alone, or paired with `or` as
  P writes `fmt-check` or `toml-check`) in `.agents/skills/fix-quality/SKILL.md` (the
  gate loop in Verification prints nothing).
- Every `just <recipe>` named in `AGENTS.md` or a skill is a recipe in the `Justfile`, or
  is `parity` or `install-parity-reference` marked "from T13" (the recipe loop in
  Verification prints nothing).
- No bridge, adapter or skill frontmatter changed: after `git fetch origin` (network,
  authorised), `git diff --exit-code origin/main -- .claude .codex CLAUDE.md
  .github/copilot-instructions.md` exits 0 with no output, and the frontmatter of each
  canonical skill equals `origin/main`'s (T00's).
- `just check` is green.
- The adversarial review in Steps ran (`CONVENTIONS.md` §14), and every valid finding is
  fixed or handed back.

## Verification

```sh
mkdir -p ai_tmp
just check-agents
rg -n -i 'pachinko|pawdoku|sudoku|wasm|no_std|effects|docs/specs|check-specs|analyse-specs|plan-spec|spec-change|install-allium|skills-lock|skill-reference' AGENTS.md .agents/
rg -c '^<important if="' AGENTS.md
awk '/^<important if=/{b=1} !b{print} /^<\/important>/{b=0}' AGENTS.md > ai_tmp/agents-core.md
for p in untrusted 'just check' 'explicit authorization' ai_tmp/ docs/specs/ runes; do
  rg -qiF "$p" ai_tmp/agents-core.md || echo "only in a block: $p"
done
for g in check-toolchain lock-check lint fmt-check toml-check clippy metrics features test-doc coverage doc deny deps-unused py-lint py-typecheck py-test py-stubtest wheel-smoke version-check check-docs check-agents snapshots-check; do
  rg -q "^ *- (\`[a-z-]+\` or )?\`$g\`" .agents/skills/fix-quality/SKILL.md || echo "missing $g"
done
rg -o -N '`just [a-z][a-z-]*' AGENTS.md .agents/ | sed 's/.*`just //' | sort -u > ai_tmp/named.txt
just --summary | tr ' ' '\n' | sort -u > ai_tmp/defined.txt
test -s ai_tmp/named.txt && test -s ai_tmp/defined.txt || echo 'recipe list empty'
comm -23 ai_tmp/named.txt ai_tmp/defined.txt > ai_tmp/extra.txt; echo "comm exit $?"   # must be 0
rg -v '^(parity|install-parity-reference)$' ai_tmp/extra.txt; echo "exit $?"   # must be 1
rg -n '`just (parity|install-parity-reference)' AGENTS.md .agents/ | rg -v 'T13'; echo "exit $?"   # must print nothing and exit 1
git fetch origin   # network, authorised (README.md, "How to pick up a ticket")
git ls-files .claude .codex CLAUDE.md .github/copilot-instructions.md | wc -l   # must print 16
git diff --exit-code --stat origin/main -- .claude .codex CLAUDE.md .github/copilot-instructions.md; echo "exit $?"   # must be 0
for s in plan-change rust-change python-change review-change review-docs fix-quality project-check; do
  git show origin/main:.agents/skills/$s/SKILL.md | sed -n '1,/^---$/p' | sed '1d;$d' > ai_tmp/fm-main.txt
  sed -n '2,/^---$/p' .agents/skills/$s/SKILL.md | sed '$d' > ai_tmp/fm-here.txt
  diff ai_tmp/fm-main.txt ai_tmp/fm-here.txt || echo "frontmatter moved: $s"
done
just check
git status --short
```

The `rg` over `AGENTS.md` and `.agents/` is expected to match the Provenance lines and
the `docs/specs/` sentence; its positive control is that it matches at all. The `test -s`
line must print nothing, `comm` must exit 0, and the `rg` over `ai_tmp/extra.txt` must
print nothing and exit 1; the `rg` for the parity recipes must print nothing and exit 1
(every mention carries its T13 mark on the same line); the `git diff --exit-code --stat`
must print nothing and exit 0 (exit 1 means a frozen file changed), and its positive
control is the `git ls-files` count of 16 just before it. `ai_tmp/named.txt` is written
before `ai_tmp/defined.txt` so that a missing `just` fails the second command, not the
comparison. The recipe pattern anchors on a backtick and a leading letter, so
`just --list` and the English word `just` in prose are not counted as recipe references.

## Hand-back notes

To be written by the executing agent: the baseline `just check` line at its commit; each
line the acceptance `rg` printed and why it stays; the word count of `AGENTS.md` and of
its core outside the blocks; the facts T11 needs to reconcile T07's
`docs/reference/agent-contract.md` (the order of `AGENTS.md`'s sections, the seven blocks
and the skill each names, the exact network-recipe list, the two recipes marked "from
T13"); the review record for the checkpoint (`CONVENTIONS.md` §14); any wording of §7 that
the files could not carry verbatim, handed back as a `CONVENTIONS.md` change; the
Verification block's output at its commit.

## Open points

- Invariant 7 already says "every cargo gate" passes `--locked`, so the Python gates
  and `wheel-smoke` are outside it. `deps-unused` runs `cargo shear`, a cargo gate that
  takes no such flag; P's T05 handed the same gap back. `AGENTS.md` carries §7's
  wording verbatim; the skills may say so.
- `AGENTS.md`'s network list names `install-parity-reference` as "from T13" although the
  recipe does not exist yet. The alternative, omitting it until T13 edits `AGENTS.md` as
  `shared, own lines`, is equally valid; this ticket chooses to name it so that the list
  is complete the day T13 lands; T13's Files touched already lists `AGENTS.md` as
  `shared, own lines` to drop the qualifier. Answered.
