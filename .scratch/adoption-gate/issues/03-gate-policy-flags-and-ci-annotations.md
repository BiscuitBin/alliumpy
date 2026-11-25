# 03: Gate policy flags and CI annotations

**What to build:** a repository adopting with existing warnings can choose what fails,
and a CI log points at the failing line. `alliumpy gate` takes a `--fail-on` severity
choice and an output format option that emits GitHub Actions annotations. No baseline
file: S02 leaves that open, and it is not in this ticket.

**Blocked by:** 02: `alliumpy gate`, the tracer bullet (and the maintainer's answer to
its exit-policy open point)

**Status:** done. Hand-back: `--fail-on` (default `warning`, the decided policy), `--fail-on-findings` and `--format github` with escaped workflow commands; fixtures `tests/fixtures/gate/` matched against the reference `allium-cli` 3.6.1; 0019 amended; `just check` ended `All checks passed and the worktree is unchanged.`

- [x] Each `--fail-on` value has a pytest case over fixtures holding an error, a
      warning, an `info` and an `analyse` finding; the default equals the decided
      policy.
- [x] The annotation format produces one well-formed annotation per diagnostic with
      file, line and column; the default output is unchanged from ticket 02.
- [x] The how-to documents both options; `just check` ends with
      `All checks passed and the worktree is unchanged.`
