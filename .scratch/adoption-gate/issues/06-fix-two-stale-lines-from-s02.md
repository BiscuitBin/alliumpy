# 06: Fix the two stale lines S02 handed back

**What to build:** the handbook no longer contradicts the published wheel. The
purpose-and-scope page stops saying the script answers `--version` only until T13, and
decision 0009's "nothing has been published yet" is marked as overtaken, as the
decisions index requires ("marked rather than deleted") and as decision 0013 was marked
when 0018 superseded part of it; the original sentence stays.

**Blocked by:** None (can start immediately)

**Status:** done. Hand-back: purpose-and-scope now describes the vendored command and the check/analyse API; 0009 carries an "overtaken in part" banner with its sentence kept; no other unpublished claim found in `docs/`; `just check` ended `All checks passed and the worktree is unchanged.`

- [x] Both statements match the state since 2026-11-05, as the changelog records it.
- [x] A search of the handbook finds no other claim that the wheel is unpublished or
      the command incomplete.
- [x] `just check-docs` passes and `just check` ends with
      `All checks passed and the worktree is unchanged.`
