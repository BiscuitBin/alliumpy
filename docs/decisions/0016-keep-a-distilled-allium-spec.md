---
title: "Decision 0016: Keep a distilled Allium spec"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_behavioural_spec"]
requires: []
---

# Decision 0016: Keep a distilled Allium spec

## Context

docmirror's behaviour is spread across thirteen stage packages and a page pipeline of
about a thousand lines. The invariants in `AGENTS.md` say what must hold, and the golden
suite pins what each DOM transform outputs. Neither says how a run moves a URL from
discovery to a written page, a tombstone or a skipped row, or which thresholds decide
it. Reading that from the code took eight readers over every stage.

`AGENTS.md` said the repository kept no Allium specifications under a `docs/specs/` of
its own. That sentence was carried from the hosting repository, whose Allium specs
described other projects. The Allium skills (`distill`, `tend`, `weed`, `propagate`)
were already installed under `.agents/skills/`.

## Decision

Keep one spec, `docs/specs/docmirror.allium`, distilled from `src/docmirror/` at commit
`f4de0fb`. It specifies the crawl and update lifecycle rule by rule. The DOM-normalization
rules are not specified one rule per transform; they become one `Fidelity` contract
whose obligations are: never drop content, keep as a sanitized island what Markdown
cannot carry, make both backends agree, and compare what survived with what was
expected. The golden suite remains the witness for each transform.

The code is authoritative. The spec describes what the code does, including behaviour
that may be accidental, and parks each such judgement as an `open question`. It is not a
handbook page: `bg-validate-docs` checks only Markdown, so the spec has no manifest
entry. [Behavioural specification](../specs/README.md) owns how to read it.

## Consequences

Contributors and agents get the whole lifecycle in one file, with its states,
transitions and thresholds named. The distillation also surfaced about fifty places
where the code's intent is unclear, recorded as open questions rather than lost.

The cost is a second description that can drift from the code. No Allium checker runs in
`just check`, and this environment has no `allium` command, so the syntax was reviewed
against the language reference rather than checked by a tool. A behavioural change
should be followed by the `weed` skill to find the drift.

## What would reopen this

A spec nobody tends, so that it misleads more than it helps, would be a reason to delete
it. An `allium` checker available to the gate would be a reason to add it to `just check`.
A decision to make the spec authoritative, with tests generated from it by `propagate`,
would supersede this record.

## Related pages

- [Behavioural specification](../specs/README.md)
- [Decision 0015: docmirror in place of alliumpy, on its toolchain](0015-docmirror-in-place-of-alliumpy.md)
- [Quality philosophy](../explanation/quality-philosophy.md)
