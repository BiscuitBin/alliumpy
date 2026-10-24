---
name: fix-quality
description: Diagnose and repair a failing quality gate at its root instead of suppressing the finding.
---

# Fix a failing gate

1. Read `AGENTS.md`, then reproduce with the narrowest recipe: `just check` names
   the failed recipe; run that one alone and read its first failure.
2. Dispatch on which gate failed:
   - `check-toolchain` — cargo is not rustup's proxy, or rustup is missing. Put
     `~/.cargo/bin` first on `PATH`; only that proxy honours `rust-toolchain.toml`.
   - `lock-check` — run `just lock`, a network recipe needing explicit authorization,
     and read the lockfile diff before accepting it.
   - `lint` — a pre-commit hook failed. Hooks named `fmt-check`, `toml-check`,
     `deps-unused`, `py-lint` or `py-typecheck` go to their gate's line below;
     `validate-docs` goes to `check-docs`, `validate-agents` to `check-agents`.
     For remaining hooks (Markdown, typos, links, shell, workflows, secrets, whitespace),
     run `just fix` for automatic repairs, then fix the remainder by hand. Remove
     secrets found by ripsecrets; never allowlist them.
   - `fmt-check` or `toml-check` — run `just fix`; never hand-format to match.
   - `clippy` — fix the code. A lint wrong for one item gets
     `#[expect(lint, reason = "...")]` there. A lint wrong for the core is changed in
     the workspace table with a comment explaining why. A lint pyo3's macro output
     trips is allowed in `crates/alliumpy/Cargo.toml`'s own `[lints]` table with a
     comment naming the macro, never in the workspace table. Keep unsafe forbidden.
   - `metrics` — lower the complexity, cohesion or coupling rustqual reports. Never
     raise a threshold in `rustqual.toml`. A version mismatch means
     `just install-tools`, a network recipe needing explicit authorization, has not
     run in this worktree.
   - `features` — fix the `cfg` for the failing feature combination; keep every
     combination in the powerset.
   - `test-doc` — fix the example or the item it documents; doc examples are tests.
   - `coverage` below the floor — add the missing test; never lower `coverage_floor`
     in the `Justfile`. Remove genuinely unreachable defensive code instead of
     inventing an input to cover it.
   - `doc` — fix a missing doc comment or broken intra-doc link; warnings are errors.
   - `deny` or `deps-unused` — fix a licence, ban or unused dependency. A new dependency
     needs the decision-0004 note; `just fix` runs cargo shear's fixer. Cargo shear
     takes no `--locked` flag; the invariant 7 gap remains recorded in T05.
   - `py-lint` — `just fix` runs ruff's fixers. A rule wrong for one line gets
     `# noqa: RULE` with a reason. Never add `extend-ignore` in `ruff.toml` without
     a comment and a review. Preserve the fixture's positive control.
   - `py-typecheck` — fix the type; never use `# type: ignore` without a code and a
     reason, and never loosen `strict`. Preserve the positive control.
   - `py-test` — fix the binding or test. `just py-test` rebuilds the extension first;
     a stale `.so` beside `__init__.py` only explains a bare pytest run. Use
     `just py-test` to reproduce.
   - `py-stubtest` — the stub and module disagree: change whichever is wrong. Never
     add an allowlist entry without a reason beside it.
   - `wheel-smoke` — two wheels in `dist/` mean something wrote there after
     `just wheel` emptied it; rerun `just wheel-smoke`. Missing uv means the pixi
     environment is incomplete; `just initialize`, a network recipe needing explicit
     authorization, rebuilds it. A network error means the recipe reached out,
     which is a defect in the recipe: the wheel smoke must install offline.
   - `version-check` — five copies of one version disagree; the message names the two.
     A bare `allium-parser` bump is a release (decision 0010), with the wheel's
     packaging-only `.postN` stripped for comparison.
   - `check-docs` — frontmatter disagreement with `docs/manifest.yml` is often list
     order; the comparison is order-sensitive. Repair the owning page and its entry.
   - `check-agents` — check inventory, required guidance and exact bridge content and
     frontmatter against the canonical file. Bridges and adapters stay thin.
   - `snapshots-check` — a snapshot differs or a `.snap` file is unreferenced. The gate
     writes no pending snapshots. If the change is intended, run
     `just snapshots-accept`, obtaining explicit authorization first if it would delete
     unreferenced snapshots. Review and explain every resulting diff before committing.
     `just snapshots-review` only reviews pending snapshots that already exist.
3. Distinguish an unreachable branch from an untested one: remove defensive code no
   input can reach instead of covering it with a contrived test.
4. Never disable a gate to make a run green. A suppression is a last resort: one rule,
   one line, with a stated reason.
5. A recipe that changes the worktree is defective; repair the recipe within the
   ticket's scope, or hand it back if frozen or owned by another lane.
6. Run the narrow recipe, then `just check` to confirm nothing else moved.
