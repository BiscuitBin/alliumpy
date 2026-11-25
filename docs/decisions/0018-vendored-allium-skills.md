---
title: "Decision 0018: Vendored upstream Allium skills, exempt from the house rules"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_vendored_allium_skills"]
requires: []
---

# Decision 0018: Vendored upstream Allium skills, exempt from the house rules

## Context

[Decision 0013](0013-no-spec-gate-no-allium-skills.md) kept the Allium skills out, because
a second installed `allium` could shadow the wheel's command or be shadowed by it. The
skills only call `allium` when one is available; they install nothing. `AGENTS.md` now
tells an agent to call this checkout's own build by path, so the skills add no competing
executable.

The skills are third-party. A skills tool installs them unchanged from `juxt/allium`
into `.agents/skills/<name>/`, links each one into `.claude/skills/<name>`, and pins the
commit and a content hash in `skills-lock.json`. Their Markdown follows upstream's style,
not this repository's. They do not cite `AGENTS.md` or name `just` recipes, and they have
no Codex bridges. Holding them to the house rules would mean editing someone else's files
on every update.

`bg-validate-agents` from biscuit-games-tooling v0.3.0 reads every directory under
`.agents/skills/` as a house skill and offers no exemption.

## Decision

Commit the Allium skills that `skills-lock.json` names, as the tool installs them. This
supersedes the skills half of decision 0013. The specification gate stayed out until
[decision 0020](0020-gate-specs-through-the-wheel.md) brought it in through the wheel.

Exempt the vendored skills from the style and content gates: ruff, markdownlint, typos,
lychee and EditorConfig, and every rewriting hook behind `just fix`. Each tool's
configuration lists the seven paths. The secret scan and the file checks still read them.

Validate the agent surface with `scripts/validate_agents.py`, which this repository owns.
It is a port of `bg-validate-agents` at v0.3.0 with one addition: a skill named in
`skills-lock.json` is exempt from the house rules. The validator still checks that each
vendored skill is installed as a versioned `SKILL.md` and that its Claude entry is the
versioned link the tool makes. A stray Codex entry fails, as before. The tooling package
still supplies the gate runner, the documentation validator and the secret scan.

## Consequences

Agents get upstream's language, specification and test-generation procedures, and run
them against the `allium` this repository builds.

The exemption lists are written out in six configuration files. A vendored skill added
or removed means editing each of them to match `skills-lock.json`. The validator follows
the lock by itself, but nothing checks the other lists against it.

The vendored files are reviewed as upstream's, not as this repository's. A change to them
comes from the skills tool and the lock, never from a hand edit.

The agent validator is now this repository's code to maintain. A change to the package's
copy does not reach this repository.

## What would reopen this

A tool that derives every exemption from `skills-lock.json`. Upstream skills that meet
the house rules. A need for the specification gate itself, which decision 0013
governed and [decision 0020](0020-gate-specs-through-the-wheel.md) now does.

## Related pages

- [Decision 0013](0013-no-spec-gate-no-allium-skills.md)
- [Decision 0020](0020-gate-specs-through-the-wheel.md)
- [Agent contract](../reference/agent-contract.md)
- [Install and run](../how-to/install-and-run.md)
- [Maintain dependencies](../how-to/maintain-dependencies.md)
