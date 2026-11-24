# 04: This repository gates its own `specs/` through the wheel

**What to build:** `just check` runs `alliumpy gate` from this repository's own built
wheel over the four distilled specifications, offline and reproducibly. A decision
record reopens decision 0013 on its own stated condition ("a way to run a specification
gate through this repository's own installed wheel, proving the selected executable and
retaining an offline, reproducible gate") and says what the gate does and does not
claim: upstream and `just parity` stay the authority on behaviour.

**Blocked by:** 02: `alliumpy gate`, the tracer bullet

**Status:** handed back (2026-11-23, maintainer's choice). Hand-back: `alliumpy gate
specs/` fails on one warning, `specs/allium-cli.allium:29:17`,
`allium.externalEntity.missingSourceHint` on `external entity CommandUser {}`, an empty
type placeholder that alliumpy.allium's `ConsoleProcess` plays and that no rule can name
truthfully. Two of the three warnings were fixed in the spec with join lookups
(`SpecFile{path: ...}`, `Module{spec_file: ...}`), which also cleared two unused-field
infos. No `specs-gate` recipe was added, decision 0013 and `AGENTS.md` are unchanged,
and the placeholder finding is recorded in decision 0019's consequences. Choices left to
the maintainer: an `entity` (misstates governance), a `--fail-on error` waiver for this
repository, or an upstream change to the warning.

- [ ] A new recipe, part of `just check`, gates `specs/` with the wheel's command and
      prints which executable ran.
- [ ] Positive control: a deliberately broken specification fixture makes the recipe
      fail.
- [x] If the specifications do not pass today, the findings are fixed in the
      specifications or handed back; no suppression and no loosened policy.
- [ ] `AGENTS.md` and the handbook no longer say `specs/` gates nothing; decision 0013
      is marked superseded in the part that changed.
- [x] `just check` ends with `All checks passed and the worktree is unchanged.`
