---
title: "Purpose and scope"
kind: "project"
audience: ["user", "contributor", "maintainer", "agent"]
canonical_for: ["project_purpose", "project_non_goals"]
requires: []
---

# Purpose and scope

`docmirror` turns a product's documentation website into a local, interlinked Markdown
knowledge base and keeps that knowledge base up to date on later runs. It serves humans
at a terminal and AI coding agents that need a trustworthy offline copy of an API's
documentation. The first two target sites are Microsoft Learn's Microsoft Graph
documentation and Google Workspace's developer documentation; the tool is generic, and
only optional per-site extraction profiles know anything about them.

## What it does

A crawl discovers pages from the start URLs, sitemaps and `llms.txt`, fetches them
politely through a three-tier ladder (HTTP impersonation, a stealth Chromium, an optional
stealth Firefox), extracts the main content with a profile's selectors or a heuristic
fallback, normalizes the DOM so tabs, code languages, admonitions, tables and heading
anchors survive, converts to GitHub-Flavored Markdown, rewrites internal links to
relative paths, measures a quality score per page and writes a root index for humans
and agents. An update run fetches only what changed and records moves and deletions so
the output can live in `git`.

## What it deliberately does not do

The proof of concept has no source adapters that bypass HTML (Google's `.md.txt`
endpoints or the Learn MCP endpoint are fidelity oracles in tests, never the pipeline),
no LLM summaries, no proxies or CAPTCHA services, no binary asset downloads, and no GUI,
web service or MCP server. A gate that cannot be measured is not claimed: a page that
loses content is flagged rather than silently accepted.

## Who it is for

A person runs `docmirror init` and `docmirror crawl` and reads the result; an agent reads
`index.jsonl`, `llms.txt` and the frontmatter of every page, and relies on deterministic
exit codes and `--json` events. Contributors maintain the pipeline and its golden tests.

## Related pages

- [Site notes](../site-notes.md)
- [Build decisions](../decisions.md)
- [Develop locally](../how-to/develop-locally.md)
