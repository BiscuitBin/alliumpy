# 01: Python API returns `check` and `analyse` results

**What to build:** Python code can call `alliumpy.check(paths)` and
`alliumpy.analyse(paths)` and get typed, immutable results per file (diagnostics and
findings carrying whatever the command's JSON carries, typed), plus the status
upstream's command would exit with. The results are upstream's, converted and never
reinterpreted (invariant 1): they come from the same vendored command the `allium`
script runs, with its output captured rather than printed. Today the Python API exposes
only `parse` and a private entry point that writes to the process's own streams, so a
Python caller has no `check` or `analyse` result to read; the core's command runner
already takes output handles, which makes this a prefactor for the gate command.

**Blocked by:** None (can start immediately)

**Status:** done. Hand-back: `alliumpy.check`/`analyse` over `alliumpy_core::report`; `just check` ended `All checks passed and the worktree is unchanged.`; `just parity` green against a reference copied from the t13 worktree (`allium 3.6.1`), not rebuilt here.

- [x] Results for the smoke fixtures equal what `allium check` and `allium analyse`
      print as JSON for the same paths, and the reported status equals the command's
      exit code.
- [x] An unreadable file, an unreadable directory and an empty path list behave as the
      command does (an unreadable file exits 1 with no result for it; an unreadable
      directory is skipped silently, so the status is 2 when nothing else is found; an
      empty path list exits 2), surfaced as documented values or `AlliumError`.
- [x] The stub, a pytest case, stubtest and the wheel smoke move with the binding; new
      core types meet invariant 3; coverage of the core stays at or above 90%.
- [x] `just parity` is unchanged and green: the `allium` command's behaviour did not
      move.
- [x] The packaging specification under `specs/` moves with the new API surface.
- [x] `just check` ends with `All checks passed and the worktree is unchanged.`
