# 05: Release `3.6.1.post1` carrying the gate

**What to build:** `uvx alliumpy@3.6.1.post1 gate specs/` works from PyPI. The release
follows the release how-to and decision 0010: a packaging-only `.postN`, with the
crates, the parser pin and `allium --version` still at 3.6.1 (invariant 9).

**Blocked by:** 02: `alliumpy gate`, the tracer bullet; 03: Gate policy flags and CI
annotations

**Status:** released (2026-11-25). Hand-back: `release/v3.6.1.post1` (PR #53, merged as
`6c73109`) dated the changelog entry 2026-11-25. The rehearsal, run 45541962562
dispatched on `main` at `6c73109` with `publish=false`, built 7 `cp311-abi3` wheels,
7 `cp314t` wheels and one sdist; its `release` job's guards and attestation passed and
`Publish to PyPI` and `Create the GitHub Release` were skipped. The annotated tag
`v3.6.1.post1` on `6c73109` started run 45551293035; after the maintainer approved the
`release` environment, it published to PyPI and created the GitHub Release. PyPI's file
list is the rehearsal's 15 files. Earlier hand-back (2026-11-23): `just version-check`
printed `all 7 versions agree: 3.6.1`, a local sdist carried `report.rs`, `_gate.py`
and `Requires-Dist: typer>=0.29.2,<0.30`, and `just check` ended `All checks passed and
the worktree is unchanged.`.

Post-publish proof, on 2026-11-25, from a temporary directory holding only
`tests/fixtures/smoke/`, with `UV_CACHE_DIR` a fresh `mktemp -d`:

```text
$ uvx -v --from "alliumpy==3.6.1.post1" allium --version 2> uvx.log
allium 3.6.1 (language versions: 1, 2, 3)
exit 0            (uvx.log names pypi.org on 26 lines)
$ uvx --from "alliumpy==3.6.1.post1" allium check tests/fixtures/smoke/ok.allium
exit 0
$ uvx --from "alliumpy==3.6.1.post1" allium check tests/fixtures/smoke/broken.allium
exit 1
$ uvx "alliumpy@3.6.1.post1" gate tests/fixtures/smoke/ok.allium
alliumpy gate: 1 files, 0 errors, 0 warnings, 0 info, 0 findings, 0 unreadable: passed
exit 0
$ uvx "alliumpy@3.6.1.post1" gate tests/fixtures/smoke/broken.allium
tests/fixtures/smoke/broken.allium:5:9: error: expected declaration (...), found '?'
alliumpy gate: 1 files, 1 errors, 0 warnings, 0 info, 0 findings, 0 unreadable: failed
exit 1
```

- [x] `just version-check` passes with the wheel at `3.6.1.post1`; the changelog
      records the new command, the new Typer dependency and that `alliumpy==3.6.1` does
      not match the post-release while `==3.6.1.*` does.
- [x] The release matrix is rehearsed before any tag.
- [x] **Stop and ask:** tagging and publishing are each separately authorised; a tag is
      a release.
- [x] After publishing, from a directory holding `tests/fixtures/smoke/` and nothing
      built, and with a fresh uv cache: `uvx alliumpy@3.6.1.post1 gate` over
      `tests/fixtures/smoke/ok.allium` exits 0; over `tests/fixtures/smoke/broken.allium`
      it exits with the status ticket 02 gives a failed gate and names the error's file
      and line; and `uvx --from 'alliumpy==3.6.1.post1' allium --version` prints 3.6.1.
      Each command is quoted in the hand-back with its exit status.
