# 04: This repository gates its own `specs/` through the wheel

**What to build:** `just check` runs `alliumpy gate` from this repository's own built
wheel over the four distilled specifications, offline and reproducibly. A decision
record reopens decision 0013 on its own stated condition ("a way to run a specification
gate through this repository's own installed wheel, proving the selected executable and
retaining an offline, reproducible gate") and says what the gate does and does not
claim: upstream and `just parity` stay the authority on behaviour.

**Blocked by:** 02: `alliumpy gate`, the tracer bullet

**Status:** ready-for-agent

- [ ] A new recipe, part of `just check`, gates `specs/` with the wheel's command and
      prints which executable ran.
- [ ] Positive control: a deliberately broken specification fixture makes the recipe
      fail.
- [ ] If the specifications do not pass today, the findings are fixed in the
      specifications or handed back; no suppression and no loosened policy.
- [ ] `AGENTS.md` and the handbook no longer say `specs/` gates nothing; decision 0013
      is marked superseded in the part that changed.
- [ ] `just check` ends with `All checks passed and the worktree is unchanged.`
