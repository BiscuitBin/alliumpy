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
- Every hard break, from `<br>` or a `<dl>` term, is a trailing backslash in both
  backends. Two trailing spaces would not survive post-processing, which trims trailing
  whitespace.
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

## Phase 7: acceptance findings

The final acceptance runs (reports under `examples/`): Microsoft Graph, 200 pages,
mean `quality_score` 0.9997, 3 low-confidence pages (1.5%), all over HTTP; Gmail,
200 pages, mean 0.994, 9 low-confidence (4.5%), 40 soft-block escalations tried the
browser and every one kept the HTTP copy. `verify` reports no broken relative link on
either tree; the 24 and 4 unresolved fragments are the sites' own stale or client-only
anchors recorded in the site notes. A second run changed no page or index file on
either tree, only `crawl-report.json` and the state under `.docmirror/` (the manifest
and, on devsite, the browser profile's cache).

- A soft block (main text under 10% of the host median) is recorded on the page as
  `soft_block_suspected` and no longer feeds the breaker or makes the page
  low-confidence: devsite's Gmail markup type reference holds dozens of legitimately
  tiny pages, and the first acceptance crawl tripped the breaker on them.
- The "thin text for a large HTML body" render rule applies only when no profile
  selector matched: a profile match on a short REST reference page is a short page,
  not a shell, and escalating every one of them to the browser cost timeouts.
- A browser render that never reaches `networkidle` within the cap settles for
  `domcontentloaded` plus a short wait rather than failing the page.
- HTML islands are dedented outside `<pre>` and every blank line inside them is
  removed, because an indented line of an interrupted HTML block reads as an indented
  code block; the Markdown-side counter joins island text with spaces so adjacent
  cells never glue into one token.
- Learn links to `#non-admin-user-cant-...` while its heading id is
  `#nonadmin-user-cant-...`: the site's own fragment is stale, `verify` reports it,
  and no fuzzy matching papers over it.
- A 304 Not Modified is never a block. Its body is empty by design, and the session
  jar still holds the host's challenge cookies, so the "tiny body with a challenge
  cookie" signature read every unchanged Learn page as a challenge and the breaker
  escalated the update run to the browser after ten of them.
- A self-link is no edge of the link graph. The rewriter used to record an absolute
  `page#fragment` link to the page itself as internal and the bare `#fragment` it had
  rewritten it to as nothing, so `inbound_internal` and `outbound_internal` changed on
  the second run; now neither form is counted, as the frontier already did.
- An `<a name>` or `<a id>` without href survives conversion: it lends an id-less
  heading directly after it its id, or stays as an empty `<a id>` island. Fragment
  checks also accept the percent-decoded form, since javadoc anchors hold spaces.
- A soft block escalates once, but the rendered copy replaces the HTTP copy only when
  it carries at least twice the main text. devsite's Gmail markup type reference and
  Drive picker enums are tiny pages on purpose: rendering them added nothing and the
  browser DOM measured worse, so the HTTP page stands with `soft_block_suspected`.
- A response that is not HTML (a PDF under `/assets/`) never escalates: a browser
  navigation to a download fails, and the page is skipped as not HTML at the first
  tier instead.
- Forms are unwrapped before conversion. html-to-markdown drops `<form>` whole, and
  devsite's support pages put their "Ask a new question" and "Submit bug" links inside
  one; the controls go, a button keeps its label as text.
- The quality summary of an update describes the mirror: an unchanged page carries
  the score it was measured with into the run's mean, p10 and low-confidence list.
- Newline runs inside a text node that holds words collapse to one space outside
  `<pre>`, as a browser renders them. devsite writes `<li>Install the\n\n Node.js
  <a>…</a></li>`, and the blank line made the converter indent the rest of the item
  into an indented code block. Whitespace-only nodes between tags are left alone so an
  HTML island keeps its line structure. Paragraph text is therefore one line per
  paragraph rather than the source's hard wraps.
- A table with no header row cannot be a pipe table: a single row of `<td>` became a
  bullet list under html-to-markdown and an empty header under markdownify, and a
  `<th>` down the first column (javadoc parameter tables) has no pipe-table form. Both
  stay HTML and count as `html_table_kept`.
- A bare `<pre>` is tagged from its text, in this order: HTTP request or status
  lines, a lower-case shell command word (`pip`, `npm`, `node`, `python`,
  `easy_install`, `docker`, `cd`, `./…` and the like; "Python 3.8 or later" is prose),
  JSON (a block that parses strictly, or a lax start of `{"key":`, an array of objects
  or an array of arrays of values, so a sample with `...` or comments qualifies but a
  TOML `[[bin]]` table or a double-brace template does not), markup (the first element
  decides: `<!doctype html>` or a lower-case HTML element without a namespace prefix
  is `html`, as is a custom element such as `gmp-map` that declares no `xmlns` and
  holds HTML elements; anything else, PascalCase XAML, `appengine-web-app` and
  fragments opening on `title`, `summary` or `source` included, is `xml`; a whole block
  that is one `<PLACEHOLDER>` is not markup), then language signatures over the first
  six lines (C# `using …;`, Java `import …;` or a declaration with a modifier, after
  any annotations, Objective-C with a typed method or `[[Class msg]`, JavaScript,
  Python, Go, PHP). A block with no code characters is tagged `text` when its first
  line is prose starting with a capital or a digit that is neither a `Key: value` line
  nor a PowerShell `Verb-Noun` cmdlet, a bare URL, a single token such as a UUID or an
  address, or a box-drawing line; later lines may be any wrapped prose. Learn's
  "Snippet not available" placeholder and an ASCII diagram qualify. A lower-case
  command (`terraform init`), YAML (`name: x`), a header line (`GData-Version: 3.0`),
  and therefore also an `Error: …` or `Note: …` line or lower-case sample output,
  stays untagged and counts against `code_lang_rate` rather than claiming `text`.
- A link inside an inline code span (a run of backticks closed by a run of the same
  length on the same line) is shown code, not a link: the rewriter leaves it as
  written and `verify` does not check it, as fenced code already is.
- Images whose URL has no file extension (Google-hosted `lh3.googleusercontent.com`
  images in the newsletter issues) lose their `src` in the trafilatura fallback, which
  only keeps sources that look like image files; readability-lxml loses the tables as
  well. The `images` gate measures the loss and the page is low-confidence; nothing
  is reconstructed.
- `verify` counts each gate once per page: the stored gate flags and its own
  re-measurement of `code_lang_rate` are merged before counting, where the
  acceptance run showed every flagged page counted twice.
- An id on an element Markdown converts away travels as an empty `<a id>` before it:
  every alert and figure keeps its id, and any other element keeps it when a link on
  the page carries that fragment. devsite's `aside.note#delegated-admin-note` is the
  target of eleven links on its own page, and the REST reference pages link their
  resource list to `<div id="v1.users.threads">` blocks.
- A tagged `<pre syntax="HTML">` inside a `<dd>` of a block definition list stays a
  `<pre>` inside the dl island, so it is the one tagged source block in the fixture set
  without an info string; the alternative, a fence indented under the term, would be
  read as an indented code block.

## Phase 6: maintenance

- `max_pages` is the mirror's size, not a per-run fetch count: an update re-checks every
  written page for free and admits new pages only while the mirror is below the limit,
  so running `crawl` twice with the same limit leaves the same set of pages.
- A page that moves (301/308 to an in-scope URL) keeps its path; the old URL becomes an
  alias of the new identity with `redirect_to` set. The prompt says to move the file to
  the new URL's path, but the path mapping is promised to be stable once assigned, and
  every inbound relative link already points at the old path.
- A re-check is a conditional GET unless `--max-age` forced it or the sitemap's
  `lastmod` is newer than the stored one; a 200 whose raw HTML hash is unchanged, or
  whose pre-rewrite Markdown is unchanged, leaves the file and its `fetched_at` alone.
- `index.md` says when the newest page was fetched, not when the last run happened, so an
  update that changed nothing rewrites no index file; the run id and time are in
  `crawl-report.json`.
- A removed page's inbound relative links go back to the absolute source URL with
  `dangling_inbound` on the linking page, through the same rewriter pass that made
  them relative.
- Every update rechecks the tombstoned pages too, after every other URL, so one that
  answers 200 again is restored to its old path, its `_removed/` copy deleted, and it is
  reported as added. When a sitemap, a start URL or a link rediscovers it first, it is
  fetched at the discovery's priority instead of last. A page that is still gone keeps
  its first tombstone and is not reported as removed again.

## Related pages

- [Site notes](site-notes.md)
- [Architecture decisions](decisions/README.md)
