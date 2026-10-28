---
name: review-change
description: Review a change in this repository against its invariants, the build prompt's fidelity rules, tests, and documentation contract.
---

# Review a change

1. Read `AGENTS.md` and the build prompt's section for the stage the change touches.
   Review the whole diff.
2. Check the nine invariants in `AGENTS.md` one at a time:
   - Fidelity first: a dropped construct, a tab panel emitted only when active, a fence
     without its language, or a table flattened without a count is a finding.
   - No hostname in code: a `if "learn.microsoft.com" in url` is a finding; the
     knowledge belongs in a profile.
   - Measured quality: a page written without `quality_score` and `quality_flags`, or a
     run that exits without `crawl-report.json`, is a finding.
   - Determinism: unsorted index entries, a timestamp inside `content_sha256`, CRLF or
     a missing final newline are findings.
   - Politeness and visibility: a proxy, a CAPTCHA service, a spoofed referrer or a
     silent retry on a blocked host is a finding.
   - Offline gates: a test under `tests/unit/` or `tests/golden/` that reaches the
     network is a finding; it belongs behind `live` or `oracle`.
   - `pixi.lock` is the pin; a `pyproject.toml` pin without a lock move is a finding.
   - A new dependency without a decision-record note is a finding.
   - One version in three places; `just version-check` must still prove it.
3. Check evidence: a normalizer change has a golden snapshot whose diff was read; a
   config change has a precedence or schema test; an update-algorithm change has a
   fake-server test covering the status code it handles. A test that only asserts a
   function was called is insufficient.
4. Check documentation ownership: a site behaviour goes in `docs/site-notes.md`, an open
   choice in `docs/decisions.md`, durable facts on the page owning their topic in
   `docs/manifest.yml`.
5. Check scope: unrelated refactors, new dependencies and speculative abstractions are
   findings in themselves.
6. Report findings by severity with `file:line`, what breaks and the smallest fix.
   Run `just check` before concluding.
