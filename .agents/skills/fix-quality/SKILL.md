---
name: fix-quality
description: Diagnose and repair a failing quality gate at its root instead of suppressing the finding.
---

# Fix a failing gate

1. Read `AGENTS.md`, then reproduce with the narrowest recipe: `just check` names
   the failed recipe; run that one alone and read its first failure.
2. Dispatch on which gate failed:
   - `lock-check` — run `just lock`, a network recipe needing explicit authorization,
     and read the lockfile diff before accepting it.
   - `lint` — a pre-commit hook failed. Hooks named `toml-check`, `py-lint` or
     `py-typecheck` go to their gate's line below; `validate-docs` goes to
     `check-docs`, `validate-agents` to `check-agents`. For remaining hooks (Markdown,
     typos, links, shell, workflows, secrets, whitespace), run `just fix` for automatic
     repairs, then fix the remainder by hand. Remove secrets found by ripsecrets; never
     allowlist them.
   - `toml-check` — run `just fix`; never hand-format to match.
   - `py-lint` — `just fix` runs ruff's fixers. A rule wrong for one line gets
     `# noqa: RULE` with a reason. Never add to `ignore` in `ruff.toml` without a
     comment and a review. Preserve the fixture's positive control.
   - `py-typecheck` — fix the type; never use `# type: ignore` without a code and a
     reason, and never loosen `strict`. Preserve the positive control.
   - `py-test` — fix the code or the test. A golden mismatch is a fidelity change:
     read the snapshot diff, and accept with `just py-test-accept` only when the new
     output is more faithful to the fixture's HTML. A quality gate failing on a fixture
     stays failing with an `xfail` naming the construct; never relax a threshold.
   - `wheel-smoke` — two wheels in `dist/` mean something wrote there after
     `just wheel` emptied it; rerun `just wheel-smoke`. Missing uv or hatchling means
     the pixi environment is incomplete; `just initialize`, a network recipe needing
     explicit authorization, rebuilds it. A network error means the recipe reached
     out, which is a defect in the recipe: the wheel smoke must install offline.
   - `version-check` — three copies of one version disagree; the message names them.
   - `check-docs` — frontmatter disagreement with `docs/manifest.yml` is often list
     order; the comparison is order-sensitive. Repair the owning page and its entry.
   - `check-agents` — check inventory, required guidance and exact bridge content and
     frontmatter against the canonical file. Bridges and adapters stay thin.
3. Distinguish an unreachable branch from an untested one: remove defensive code no
   input can reach instead of covering it with a contrived test.
4. Never disable a gate to make a run green. A suppression is a last resort: one rule,
   one line, with a stated reason.
5. A recipe that changes the worktree is defective; repair the recipe within the
   task's scope, or hand it back.
6. Run the narrow recipe, then `just check` to confirm nothing else moved.
