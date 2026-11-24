# 05: Release `3.6.1.post1` carrying the gate

**What to build:** `uvx alliumpy@3.6.1.post1 gate specs/` works from PyPI. The release
follows the release how-to and decision 0010: a packaging-only `.postN`, with the
crates, the parser pin and `allium --version` still at 3.6.1 (invariant 9).

**Blocked by:** 02: `alliumpy gate`, the tracer bullet; 03: Gate policy flags and CI
annotations

**Status:** ready-for-agent

- [ ] `just version-check` passes with the wheel at `3.6.1.post1`; the changelog
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
