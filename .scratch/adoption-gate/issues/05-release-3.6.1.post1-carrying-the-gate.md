# 05: Release `3.6.1.post1` carrying the gate

**What to build:** `uvx alliumpy@3.6.1.post1 gate specs/` works from PyPI. The release
follows the release how-to and decision 0010: a packaging-only `.postN`, with the
crates, the parser pin and `allium --version` still at 3.6.1 (invariant 9).

**Blocked by:** 02: `alliumpy gate`, the tracer bullet; 03: Gate policy flags and CI
annotations

**Status:** prepared, stopped before release (2026-11-23). Hand-back: `[project] version`
is `3.6.1.post1` and the changelog's `[3.6.1.post1] - 2026-11-23` entry records the
command, Typer and `==3.6.1` against `==3.6.1.*`; `just version-check` printed `all 7
versions agree: 3.6.1`; a local sdist carries `report.rs`, `_gate.py` and
`Requires-Dist: typer>=0.29.2,<0.30`; `just check` ended `All checks passed and the
worktree is unchanged.`. Not done, each awaiting its own authorisation: the pre-flight
reads (`gh api`, PyPI), the `release/v3.6.1.post1` branch from `main` (this work is on
`spike-prek-and-more`), push and pull request, the rehearsal, the tag, the publish and
the post-publish `uvx` proof. The changelog date needs re-dating if the merge lands later.

- [x] `just version-check` passes with the wheel at `3.6.1.post1`; the changelog
      records the new command, the new Typer dependency and that `alliumpy==3.6.1` does
      not match the post-release while `==3.6.1.*` does.
- [ ] The release matrix is rehearsed before any tag.
- [ ] **Stop and ask:** tagging and publishing are each separately authorised; a tag is
      a release.
- [ ] After publishing, from a directory holding `tests/fixtures/smoke/` and nothing
      built, and with a fresh uv cache: `uvx alliumpy@3.6.1.post1 gate` over
      `tests/fixtures/smoke/ok.allium` exits 0; over `tests/fixtures/smoke/broken.allium`
      it exits with the status ticket 02 gives a failed gate and names the error's file
      and line; and `uvx --from 'alliumpy==3.6.1.post1' allium --version` prints 3.6.1.
      Each command is quoted in the hand-back with its exit status.
