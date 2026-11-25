---
title: "Decision 0020: This repository's `specs/` gated through its own wheel"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_specs_gate"]
requires: []
---

# Decision 0020: This repository's `specs/` gated through its own wheel

## Context

[Decision 0013](0013-no-spec-gate-no-allium-skills.md) kept a specification gate out,
because a second, independently installed `allium` could shadow the wheel's command, or
be shadowed by it, so a passing run might have tested the wrong executable. It named
what would reopen it: "A way to run a specification gate through this repository's own
installed wheel, proving the selected executable and retaining an offline, reproducible
gate."

[Decision 0019](0019-alliumpy-gate-script.md) put that way in the wheel: `alliumpy
gate`, which runs upstream's `check` and `analyse` in process. `just wheel-smoke`
already installs the freshly built wheel offline into `target/wheel-smoke/venv`, so the
gate can run from there with nothing else installed.

The four distilled specifications failed the gate's default policy on one warning:
`allium.externalEntity.missingSourceHint` on `external entity CommandUser {}` in
`specs/allium-cli.allium`, an empty type placeholder that no specification governs. The
choices were to declare it an internal entity, to waive warnings for this repository
with `--fail-on error`, or to wait for upstream to change the warning.

## Decision

Add `just specs-gate` to `just check`, after `version-check`, and to the CI `python` job.
It runs `alliumpy gate specs/` at the default policy from the venv `wheel-smoke` left,
offline, and fails if that venv is missing. It runs the venv's interpreter isolated
(`-I`), so `PYTHONPATH`, the working directory and user site-packages cannot supply the
package, and it fails unless `alliumpy` and its native extension both import from
inside the venv. It prints the extension's path and `allium --version` first, so each
run names the code that gated. Its positive control, `tests/fixtures/gate/warning.allium`,
has one warning and no error, and the recipe fails unless the gate fails it on exactly
that warning, at its position, with a summary of one warning and no error; a policy
loosened to errors only would let the control pass, and the recipe would fail.

Declare `CommandUser` an internal `entity`, the maintainer's choice of 2026-11-25, with a
comment that says it is external in truth. No diagnostic under `specs/` is waived, and
the gate's policy is the one adopters get.

This supersedes the specification-gate half of decision 0013. Nothing else is installed
to check specifications: the gate is this repository's own wheel.

## Consequences

The specifications can no longer drift into a state upstream's checker rejects without
`just check` saying so. They still gate no behaviour. A pass proves that upstream's
`check` and `analyse` both read every file, that neither reports an error or a warning,
and that no file was unreadable; `analyse`'s findings are printed but fail nothing under
the default policy. It does not prove that the specifications describe the code truly. Upstream and
`just parity` stay the authority on what the command does, and decision 0013's point
stands that this repository tests packaging, not the language.

`CommandUser` misstates governance in one line: the specification says nothing else
about it, and the comment beside it records why. The misstatement reaches tools as well
as readers: `allium model` reports it as internal, and nothing in its output carries the
comment. Upstream changing the warning, or
documenting how a placeholder should be declared, would let it go back to `external`.

An upstream bump that adds a warning fails `just check` on `specs/` as well as wherever
else it lands. That is the gate working: the specification is fixed in the same bump.

Inside `just check` and CI the gate's result depends on the wheel built in the same run,
so it moves with each change to the vendored command, and `just check` has one more
recipe after `wheel-smoke`. Run alone, `just specs-gate` gates whatever wheel the last
`wheel-smoke` installed, as `version-check` reads it: after a change, run `just
wheel-smoke` first.

## What would reopen this

A specification that the default policy cannot pass without misstating it, for which a
waiver would be truer than a change. Upstream changing how the checker treats an empty
external entity. Upstream shipping a gate command of its own (decision 0019).

## Related pages

- [Decision 0013](0013-no-spec-gate-no-allium-skills.md)
- [Decision 0019](0019-alliumpy-gate-script.md)
- [Quality gates](../reference/quality-gates.md)
- [Commands](../reference/commands.md)
