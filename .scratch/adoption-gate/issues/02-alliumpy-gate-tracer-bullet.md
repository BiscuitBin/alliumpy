# 02: `alliumpy gate`, the tracer bullet

**What to build:** the wheel gains a second console script, `alliumpy`, a Typer CLI
with one subcommand, so `uvx alliumpy gate specs/` needs no `--from`. `alliumpy gate
<paths>` runs check and analyse through the Python API of ticket 01, prints a readable
summary and exits by one stated policy. A decision record states: the script's name;
that it is outside the parity invariant, which covers `allium` only; Typer as the
wheel's first runtime dependency, with the decision-0004 note; and a drafted exit
policy. The exit policy stays an **open point** in the record for the maintainer to
settle in review (candidates: fail on errors, warnings and findings; or errors only).
The record also says how the policy follows upstream's `v4` change, where both commands
exit 1 on any error or warning for a specification of language version 4 only; a
version 3 specification keeps today's rule, under which `analyse` takes its status from
findings alone, so an error with no findings exits 0.

**Blocked by:** 01: Python API returns `check` and `analyse` results

**Status:** done. Hand-back: `alliumpy gate` (`_gate.py`) with statuses 0/1/2/3 and the exit policy decided on 2026-11-23, recorded as decided in decision 0019; Typer 0.29.2 locked (closure: pydantic, pydantic-core, rich, shellingham, annotated-doc and their dependencies), Cargo locks unchanged; offline smoke through `--system-site-packages`; `just parity` green; `just check` ended `All checks passed and the worktree is unchanged.`; the CI `wheel-smoke-py311` change is unrun until a push.

- [x] `alliumpy gate` over a clean fixture exits 0; over a fixture with an error exits
      non-zero and names file, line and message; `alliumpy --help` and
      `alliumpy gate --help` work.
- [x] Usage errors and "no specification found" have their own documented exit status,
      distinct from "the gate failed".
- [x] `allium` is byte-for-byte unchanged: `just parity` green.
- [x] Typer is declared as a runtime dependency of the wheel and pinned in the pixi
      lock. `just lock` and `just sync` reach the network and are authorised by this
      ticket.
- [x] The wheel smoke stays offline and still runs `alliumpy gate` from an installed
      wheel. Today it installs with no dependencies, so the ticket states how Typer
      reaches the smoke environment without the network, and the smoke checks that the
      wheel's metadata declares it.
- [x] The decision record extends decision 0004's note, written for cargo dependencies
      only, to a Python runtime dependency, and Renovate (decision 0017) tracks the new
      pin.
- [x] pytest covers the policy; the install-and-run how-to gains the command; the
      packaging specification under `specs/` moves with the new command.
- [x] The decision record is drafted and registered; `just check` ends with
      `All checks passed and the worktree is unchanged.`
