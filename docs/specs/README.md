---
title: "Behavioural specification"
kind: "reference"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["behavioural_specification"]
requires: []
---

# Behavioural specification

`docmirror.allium` in this directory is an Allium specification of what docmirror does:
the entities it keeps, the rules that move them between states, the invariants that must
always hold and the thresholds it works to. It describes behaviour, not implementation,
so it names no parser, HTTP client, state store or browser automation library.

The spec was distilled from `src/docmirror/` at commit `f4de0fb`, so it records what the
code does rather than what anyone intended. Where the spec and the code disagree, the
code wins until the spec is tended. [Decision 0016](../decisions/0016-keep-a-distilled-allium-spec.md)
records why the repository keeps it. [Purpose and scope](../project/purpose-and-scope.md)
says what the tool is for.

## What it covers

- The commands `init`, `crawl`, `update`, `fetch` for one URL, `verify`, `index` and
  `report`.
- A run's lifecycle: refusal, start, discovery, scheduling and finish, including the
  interrupt path and the exit-code ranking.
- The frontier and how URLs enter it: start URLs, sitemaps, `llms.txt` and page links,
  with scope and robots.
- The fetch ladder from HTTP to the browser to the opt-in stealth tier, block
  classification, the per-host circuit breaker and politeness.
- Extraction, the quality score and flags, and low confidence.
- The mirror's manifest: pages, paths, aliases, change detection and tombstones.
- Link rewriting, broken links, the indexes and the crawl report.
- One `Fidelity` contract for every DOM-normalization rule: never drop content, keep what
  Markdown cannot carry as a sanitized HTML island, make both converter backends agree,
  and measure what survived against what was expected.

## What it leaves out

The `doctor` and `schema` commands, logging and table rendering, and the parsing of
sizes and durations in configuration are out of scope. So are library choices: browsers
appear as one external `BrowserEngine`. The mechanics of each DOM transform belong to
the golden suite under `tests/golden/`, which witnesses the `Fidelity` contract case by
case.

## How to read it

The file follows the Allium section order: external entities, value types, contracts,
enumerations, entities, config, rules, invariants, surfaces and open questions. The
rules are grouped by flow, from setting up a mirror to finishing a run. Free-standing
calls such as `normalize_url` or `extract_main_content` are black boxes the code
defines; the header lists them. The `config` block marks with `toml:` each value an
operator can set in `docmirror.toml`; every other value is fixed in code.

The open questions at the end are the distillation's real findings. Each is a place where
the code's behaviour may be accidental, such as a check that never fires, a definition
given twice, or an exception to an invariant. Answer one by changing the code or the
spec, then delete the question.

## Keeping it true

No Allium checker runs in `just check`, so nothing stops the spec drifting from the
code. Re-check it with the `weed` skill after a behavioural change. Edit it with the
`tend` skill, which keeps the syntax valid.

## Related pages

- [Purpose and scope](../project/purpose-and-scope.md)
- [Quality philosophy](../explanation/quality-philosophy.md)
- [Decision 0016: Keep a distilled Allium spec](../decisions/0016-keep-a-distilled-allium-spec.md)
