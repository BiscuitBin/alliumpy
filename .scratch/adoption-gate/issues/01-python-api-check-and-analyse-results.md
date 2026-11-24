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

**Status:** ready-for-agent

- [ ] Results for the smoke fixtures equal what `allium check` and `allium analyse`
      print as JSON for the same paths, and the reported status equals the command's
      exit code.
- [ ] An unreadable path and an empty path list behave as the command does (exit 1 with
      no result for the file; exit 2), surfaced as documented values or `AlliumError`.
- [ ] The stub, a pytest case, stubtest and the wheel smoke move with the binding; new
      core types meet invariant 3; coverage of the core stays at or above 90%.
- [ ] `just parity` is unchanged and green: the `allium` command's behaviour did not
      move.
- [ ] The packaging specification under `specs/` moves with the new API surface.
- [ ] `just check` ends with `All checks passed and the worktree is unchanged.`
