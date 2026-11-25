# 04: This repository gates its own `specs/` through the wheel

**What to build:** `just check` runs `alliumpy gate` from this repository's own built
wheel over the four distilled specifications, offline and reproducibly. A decision
record reopens decision 0013 on its own stated condition ("a way to run a specification
gate through this repository's own installed wheel, proving the selected executable and
retaining an offline, reproducible gate") and says what the gate does and does not
claim: upstream and `just parity` stay the authority on behaviour.

**Blocked by:** 02: `alliumpy gate`, the tracer bullet

**Status:** done (2026-11-25). The maintainer chose to declare `CommandUser` an
internal `entity`, with a comment that it is external in truth; `alliumpy gate specs/`
then passes the default policy (4 files, 0 errors, 0 warnings, 4 info, 0 findings).
`just specs-gate`, after `version-check` in `just check` and in the CI `python` job,
runs the wheel-smoke venv's interpreter isolated, requires the package and its extension
to import from the venv and names them with `allium --version`, requires
`tests/fixtures/gate/warning.allium` to fail on exactly its one warning, then gates
`specs/`. An adversarial review by Codex (`gpt-6.2-sol`) on 2026-11-25 found the
launcher could import the checkout through `PYTHONPATH`, a loose control match and an
unchecked version probe; all three are fixed, with the docs it flagged. Decision 0020 records it and supersedes decision 0013's gate half.
Earlier hand-back (2026-11-23): two of the three warnings were fixed with join lookups
(`SpecFile{path: ...}`, `Module{spec_file: ...}`), which also cleared two unused-field
infos.

- [x] A new recipe, part of `just check`, gates `specs/` with the wheel's command and
      prints which executable ran.
- [x] Positive control: a deliberately broken specification fixture makes the recipe
      fail.
- [x] If the specifications do not pass today, the findings are fixed in the
      specifications or handed back; no suppression and no loosened policy.
- [x] `AGENTS.md` and the handbook no longer say `specs/` gates nothing; decision 0013
      is marked superseded in the part that changed.
- [x] `just check` ends with `All checks passed and the worktree is unchanged.`
