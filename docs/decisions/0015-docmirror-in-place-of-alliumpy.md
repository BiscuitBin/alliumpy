---
title: "Decision 0015: docmirror in place of alliumpy, on its toolchain"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_docmirror_host", "decision_dependency_policy"]
requires: []
---

# Decision 0015: docmirror in place of alliumpy, on its toolchain

## Context

The `docmirror` proof of concept needed a repository with a working quality gate on day
one. `alliumpy` had one: pixi pinning every tool, just as the only interface to the
checks, prek running the read-only hooks, the shared `biscuit-games-tooling` validators
for the handbook and the agent surface, and `bg-project-check` snapshotting the worktree
between gates. It also had a Rust workspace, cargo gates and a maturin wheel that mean
nothing to a pure-Python tool. The maintainer chose to host docmirror on a branch of
that repository, in place of alliumpy rather than beside it, and to keep the licence.

## Decision

The branch replaces the product and keeps the toolchain. The Rust crates, `Cargo.toml`,
`Cargo.lock`, the clippy, deny, rustfmt, rustqual and nextest configuration, the cargo
tool lists, the audit and Pages workflows and the `rust-change` skill are removed. The
root `pyproject.toml` becomes docmirror's own manifest (hatchling, `src/` layout, a
`docmirror` console script) and stays the pixi workspace; the package is installed
editable with its `dev` extra so every recipe sees the worktree. The gate list shrinks
to ten recipes: locks, hooks, TOML, ruff, mypy, pytest, wheel smoke, versions,
documentation and agents. The licence stays Apache-2.0 on the maintainer's instruction,
though the build prompt asked for MIT; the prompt's reason for MIT, no AGPL dependency
in the default install, is kept as a rule.

### Dependency policy

`pixi.lock` is the pin. `pyproject.toml` writes lower bounds for the runtime
dependencies, exact pins for the pixi tools, and the lock resolves both; `just sync`
installs the lock as committed and `just lock-check` proves it matches. Every runtime
dependency below was chosen by the build prompt, which fixes the stack; the note says
why each is in the default install.

| Dependency | Why |
| --- | --- |
| `typer` | The CLI framework: agent-friendly flags, generated help, easy `--json`. |
| `pydantic` | Validates the configuration and publishes the JSON Schemas. |
| `curl_cffi` | Tier 0 fetching with a browser-grade TLS fingerprint, no browser process. |
| `patchright` | Tier 1: Playwright with the CDP leaks closed; the browser is a separate download. |
| `html-to-markdown` | The default converter, chosen for measured table, image and escaping fidelity. |
| `markdownify` | The subclassable fallback backend a profile can switch to. |
| `trafilatura`, `readability-lxml` | Main-content fallbacks when no profile selector matches. |
| `lxml`, `selectolax` | DOM pre-normalization and fast selection. |
| `markdown-it-py`, `mdit-py-plugins` | Counting elements in the output for the quality gates. |
| `yake`, `scikit-learn` | Per-page keywords and corpus TF-IDF, deterministic and offline. |
| `rich` | Logging handlers on stderr and the human report table. |
| `protego` | robots.txt parsing with `Crawl-delay`. |
| `pyyaml` | Frontmatter. |
| `jsonschema` | Validating `index.jsonl` and the schemas the tool prints. |
| `camoufox` (extra) | Tier 2, opt-in; AGPL-free, but a Firefox download of its own. |

Test-only: `pytest`, `syrupy` (golden snapshots), `pytest-httpserver` (the fake server
for the update algorithm), and the stub packages mypy needs. No dependency under AGPL
enters the default install; nodriver, Lightpanda and Firecrawl are out for that reason.

## Consequences

A green gate from the first commit, the same gate the house repositories run, and a
handbook and agent surface that were already validated. The cost is a repository whose
history, tickets and retired decision numbers belong to another product, which the
decisions index explains, and a licence that differs from the prompt's.

## What would reopen this

Moving docmirror to a repository of its own: the subtree is designed to lift out whole,
and the carried-from notes in this handbook would then name this branch.

## Related pages

- [Decision 0002: Hook runner and checkers](0002-hook-runner-and-checkers.md)
- [Build decisions](../decisions.md)
- [Quality gates](../reference/quality-gates.md)
