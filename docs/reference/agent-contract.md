---
title: "Agent contract"
kind: "reference"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["agent_contract"]
requires: []
---

# Agent contract

Enforced by `scripts/validate_agents.py`, which this repository owns, run by
`just check-agents` and by a pre-commit hook. `AGENTS.md` is the single
source of truth for how an agent works in this repository; everything else in the agent
surface exists only so a particular tool can find it.

## The four surfaces

| Path | Role |
| --- | --- |
| `AGENTS.md` | Canonical. Read natively by Codex, and by anything following the convention. |
| `CLAUDE.md` | A pointer, byte-pinned to `@AGENTS.md` and nothing else. |
| `.github/copilot-instructions.md` | A pointer, byte-pinned to one paragraph. |
| `.agents/skills/` | Canonical task procedures, mirrored by thin bridges under `.claude/skills/` and `.codex/skills/`, beside the [vendored skills](#vendored-skills). |

A `CODEX.md` at the repository root is forbidden: Codex reads `AGENTS.md` directly, and a
second file would be a second source of truth.

## What `AGENTS.md` must contain

- At least 300 words.
- Six phrases, each naming an invariant that is expensive to rediscover: `untrusted`,
  `just check`, `explicit authorization`, `ai_tmp/`, `docs/specs/`, and `runes`.

The phrase list is a crude check and is meant to be. It does not verify that the guidance
is good; it verifies that the six topics were not dropped in an edit.

The sixth phrase names the games' reactivity rule, which has nothing to govern in this
repository. `AGENTS.md` satisfies it with one honest sentence saying the rule does not apply
here. The validator is this repository's own since
[decision 0018](../decisions/0018-vendored-allium-skills.md); dropping the phrase is a
change to `scripts/validate_agents.py`, not to this page alone.

## What a skill must be

This repository carries seven canonical house skills with fourteen bridges, and
`AGENTS.md` routes to them through its task blocks. Their triggers are:

| Skill | Trigger |
| --- | --- |
| `plan-change` | Establish scope, risks and validation before implementation. |
| `rust-change` | Change the core or bindings while preserving layering and Rust evidence. |
| `python-change` | Change the package, stub, tests or console script together. |
| `review-change` | Review a diff against invariants, tests and documentation. |
| `review-docs` | Revise a reachable page under the documentation contract. |
| `project-check` | Prepare and interpret the complete gate. |
| `fix-quality` | Diagnose and repair a failing gate at its cause. |

Frontmatter of exactly two keys:

```markdown
---
name: rust-change
description: Implement or review a change to the core or the bindings crate with the layering, tests and documentation evidence the invariants require.
---
```

- `name` equals the directory name.
- `description` is at least eight words and states a real trigger.
- The body cites `AGENTS.md` and names at least one `just` recipe. A procedure that ends
  without saying how to verify it is not a procedure.

The frontmatter parser is deliberately literal. It splits every line between the `---`
markers on the first colon and treats a line without one as an error, so a blank line
inside the block fails the check with `invalid frontmatter line`. Keep the two keys
adjacent, with nothing between them. The same parser reads the bridges, so the rule holds
there too.

A key that appears twice is an error rather than an overwrite. Left to the usual last-wins
behaviour, a block of three lines would satisfy a rule about two keys on whichever copy
happened to survive, which is the opposite of what "exactly two" is for.

## What a bridge must be

Each of `.claude/skills/<name>/SKILL.md` and `.codex/skills/<name>/SKILL.md` carries the
canonical frontmatter verbatim, then exactly this sentence and nothing else:

```markdown
Follow `../../../.agents/skills/<name>/SKILL.md`. That file is canonical and this bridge adds nothing to it.
```

The body is compared against that template rather than measured against a word budget. A
budget was the earlier rule and it enforced the wrong thing: a bridge could carry an
instruction of its own — an extra step, a caveat, a second pointer — and pass on being
brief. This is an instruction surface, so a clause smuggled into it is read as guidance and
becomes a second source of truth for the skill it points at. A bridge that grows content
fails whether or not it is short.

## Vendored skills

The skills `skills-lock.json` names are third-party, installed unchanged by the skills
tool that wrote the lock: today, seven Allium skills from `juxt/allium`. They are exempt
from the rules above, and from the style and content linters, under
[decision 0018](../decisions/0018-vendored-allium-skills.md). In their place:

- `.agents/skills/<name>/SKILL.md` is a versioned regular file. The rest of the
  directory is the skill's own.
- `.claude/skills/<name>` is a versioned link to `../../.agents/skills/<name>`, the
  link the tool makes. Codex reads `.agents/skills/` itself, so there is no
  `.codex/skills/<name>`; one would be an unexpected file.
- A lock entry with no installed skill fails, as does a lock without a readable
  `skills` table.

Update them only through the skills tool and the lock, never by hand. Taking a skill out
of the lock makes it a house skill, and every rule above then applies to it.

## The inventory

The validator lists managed files from Git, honouring only this repository's
`.gitignore`, and compares that against what it expects.

- Every expected file must exist. A house skill without its two bridges fails.
- No unexpected file may exist under `.agents/`, `.claude/` or `.codex/`. The single
  exception is `.claude/settings.json`, which is tolerated but not required — it carries
  provider configuration rather than agent guidance.
- Managed files must be regular files, never symlinks. A vendored skill's Claude link
  is the one exception, and it is checked as described above.

Local assistant state stays out of the inventory by being listed in `.gitignore`. That is
deliberate: the check reads Git rather than walking the filesystem, so an ignored file is
invisible to it.

On this tree `just check-agents` prints
`Validated AGENTS.md, 2 adapters, 7 skills, and 7 vendored skills.`

## Related pages

- [Documentation contract](documentation-contract.md)
- [Quality gates](quality-gates.md)
- [Decision 0013](../decisions/0013-no-spec-gate-no-allium-skills.md)
- [Decision 0018](../decisions/0018-vendored-allium-skills.md)
