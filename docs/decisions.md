---
title: "Build decisions"
kind: "explanation"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["build_choices"]
requires: []
---

# Build decisions

The build prompt fixes the stack, the scope and the index strategy and says not to ask
questions during the build: where it leaves a choice open, the agent chooses the option
that preserves more content, is more deterministic or is easier to test, in that order,
and records the choice here. Repository-level decisions with lasting consequences get a
numbered record under `decisions/`; this page is the running log of the smaller ones.

## Phase 0: the host

- The repository keeps Apache-2.0 instead of the prompt's MIT, on the maintainer's
  instruction; the dependency rule that motivated MIT (no AGPL in the default install)
  still holds, and [decision 0015](decisions/0015-docmirror-in-place-of-alliumpy.md)
  records both.
- The package ships `src/docmirror` with hatchling; the pixi environment installs it
  editable with its `dev` extra so the console script, pytest and mypy all see the
  worktree.
- The ruff rule set stays `select = ["ALL"]` as carried; the copyright-header rule is
  ignored once in `ruff.toml` because `LICENSE` carries the notice.
- Environment overrides use `DOCMIRROR_<SECTION>__<KEY>`, with a double underscore
  between section and key, because the TOML has nested sections and a single
  underscore would be ambiguous against keys such as `max_pages`.
- The flat profile keys the prompt's example uses (`tab_group`, `tab_label`,
  `tab_panel`, `admonition`, `admonition_title`) fold into the structured `tabs` and
  `admonitions` lists, so a profile can describe more than one tab shape (devsite has
  two) without a second mechanism.
- lychee comes from the pixi environment, pinned exactly, and its hooks are `local`
  entries naming that binary. Upstream's auto-installing hook resolves its download
  through the GitHub API, which the build container forbids, and a binary a hook
  fetches at first run is a pin nothing hashes; the conda-forge package is both.
- `[fetch.provider]` exists, validates, and rejects any non-empty value with a message
  saying it is reserved and not implemented.

## Phases 2 and 3: crawl, convert, fidelity

- Sitemap entries queue at depth 2 and the frontier is ordered by depth, so a bounded
  crawl samples the pages near the start URL rather than the sitemap's first entries;
  start pages are fetched alone first so their links are queued before anything deeper.
- A page without the version parameter keeps its plain path and reports
  `version_default` in its frontmatter; inserting the default into every path would
  move every conceptual page under a version it does not have.
- The page title is the first H1 of the main content, then `og:title`, then `<title>`,
  because both sites suffix `<title>` with the site name.
- Raw-HTML islands: a subtree that must stay HTML (a complex table, a block definition
  list, `<details>`, math without TeX, an inline heading anchor) is replaced by a token
  before conversion and restored afterwards, so one mechanism serves every backend.
  Blank lines inside an island are removed, and a blank line inside `<pre>` inside an
  island becomes a line holding one space, because a blank line ends a Markdown HTML
  block.
- Element counts for the quality gates come from the normalized tree plus its islands
  (what the output must carry), not from the raw DOM: expanding a tab group adds
  headings and removes a tablist's links and list items by design, and the
  `tabs_expanded` gate covers the expansion itself. Text coverage still uses the raw
  DOM's words. The language-tag rate counts fences only; a `<pre>` kept inside an HTML
  table cannot be a fence.
- Links inside `<pre>` become their text: a fence cannot carry a link, and a Markdown
  link inside code would be read as code. This is listed under "What is lossy".
- A `<dl>` term and its definition share one paragraph joined by a hard break, so the
  four-space indent is a continuation line, never an indented code block.
- Hidden elements are stripped except `section[hidden]`, which is how Learn marks an
  inactive tab panel; `<iframe>` is not stripped but replaced by the interactive
  placeholder, which keeps the URL.
- Titles such as "Page Summary" from devsite's generated takeaways panel are stripped
  as chrome, not kept as content, because the site generates them per visit.

## Phase 5: resilience

- `low_confidence` is true when a gate fails or when a pipeline flag says the content
  is known to be incomplete (`render_needed`, `empty_content`, `soft_block_suspected`):
  an empty shell scores 1.0 on every gate because there was nothing to lose, and the
  prompt's acceptance criterion for `--render never` needs the count to be non-zero.
- A soft block at the last available tier still writes the page, flagged
  `soft_block_suspected` and counted as blocked for the host, because the page may be
  a legitimately short one; a hard block or challenge writes nothing.
- The browser tiers go through the same per-host limiter as HTTP, so escalation never
  doubles the request rate.
- The breaker trips immediately when no higher tier exists, which is what
  `[antibot] stealth = "off"` or `--render never` means for a blocked host.
- `docmirror fetch` keeps its browser profile under `~/.cache/docmirror` (or
  `DOCMIRROR_STATE_DIR`) because it has no output directory.

## Related pages

- [Site notes](site-notes.md)
- [Architecture decisions](decisions/README.md)
