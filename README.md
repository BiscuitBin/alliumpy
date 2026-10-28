# docmirror

`docmirror` turns a product's documentation website into a local, interlinked Markdown
knowledge base and keeps it up to date on later runs. It is for people at a terminal and
for AI coding agents that need a trustworthy offline copy of an API's documentation.

Every page carries a measured quality score and flags, internal links are rewritten to
relative paths, a root index lists every file with keywords and a description, and the
output directory can live in `git` so that a diff shows only real documentation changes.
The first two target sites are Microsoft Learn's Microsoft Graph documentation and Google
Workspace's developer documentation; nothing in the code names a site, only the two
built-in extraction profiles do.

## Installation

Python 3.12 or newer.

```console
uv tool install git+https://github.com/BiscuitBin/alliumpy@claude/prompt-implementation-fhsqh4
# or, from a checkout:
uv tool install .
# or
pipx install .
```

The HTTP tier works at once. The browser tier, used when a page needs JavaScript or when
a site blocks plain HTTP, needs Chromium once:

```console
patchright install chromium
docmirror doctor
```

The optional stealth tier is a separate extra, `docmirror[camoufox]`, which downloads a
Firefox build of its own.

## Quick start

Sixty seconds against the Gmail API guides:

```console
docmirror init https://developers.google.com/workspace/gmail/api/guides ./gmail-docs
docmirror crawl ./gmail-docs --max-pages 25
docmirror verify ./gmail-docs
```

`init` writes `gmail-docs/docmirror.toml` seeded from the URL (host, path prefix, locale,
detected profile) and an empty manifest. `crawl` fetches up to 25 pages politely, converts
them, rewrites their links, and writes `index.md`, `index.jsonl`, `llms.txt` and
`crawl-report.json`. `verify` checks every relative link and fragment offline. Run
`crawl` again later: it re-checks what it has with conditional requests and fetches only
what changed.

```console
docmirror report ./gmail-docs
docmirror fetch https://learn.microsoft.com/en-us/graph/api/user-get --tier http
```

## Commands

Every subcommand accepts `--config PATH`, `--json` (NDJSON progress events on stdout,
human logs on stderr), `--yes`/`--non-interactive`, `-v` (repeatable) and `--quiet`.
When stdout is not a TTY the tool never prompts.

| Command | Purpose |
| --- | --- |
| `docmirror init <url> <out-dir>` | Create `<out-dir>`, write a starter `docmirror.toml` and the manifest. Does not crawl. |
| `docmirror crawl <out-dir>` | Full crawl per config; on a populated directory it behaves like `update`. |
| `docmirror update <out-dir>` | Incremental run: sitemap `lastmod`, conditional GETs, re-convert only changed pages, tombstones and redirects. |
| `docmirror verify <out-dir>` | Offline: frontmatter, body hashes, every relative link and fragment, manifest against the tree. Exit 4 on failure. |
| `docmirror index <out-dir>` | Offline: regenerate `index.md`, `index.jsonl`, `llms.txt` and `_index.md` files. |
| `docmirror report <out-dir>` | Print the last `crawl-report.json` as tables, or as JSON with `--json`. |
| `docmirror doctor` | Check Python, `curl_cffi`, Patchright and its browser, Camoufox, write access. |
| `docmirror schema config\|report\|frontmatter\|index` | Print the JSON Schema (draft 2020-12) of an artefact. |
| `docmirror fetch <url>` | Debug one page: `--tier http\|browser\|stealth` forces a tier, `--dump-html PATH` saves the extracted HTML. |

Crawl flags, each also settable in the TOML: `--allow-host`, `--path-prefix`,
`--include`, `--exclude` (glob or `re:` regex on the normalized URL), `--max-depth`,
`--max-pages`, `--max-bytes`, `--locale`, `--rate` (requests per second per host),
`--concurrency`, `--robots respect|ignore`, `--render auto|never|always`,
`--stealth off|patchright|camoufox`, `--user-agent`, `--timeout`, `--resume` (default
on), `--dry-run`, `--prune`, `--fail-on-low-quality`, `--max-age DURATION`.

### Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Completed; every page fetched, no gate failures. |
| 1 | Completed with failures (pages unfetched, blocked or errored) or an unexpected exception. |
| 2 | Usage or configuration error. |
| 3 | Blocked: the circuit breaker tripped for at least one host. |
| 4 | Quality-gate failure with `--fail-on-low-quality`, or `verify` found failures. |

The highest applicable code wins, and `crawl-report.json` is written before every exit.

## Configuration

`<out-dir>/docmirror.toml`, validated strictly: an unknown key is an error naming its
path. Precedence is CLI flags, then `DOCMIRROR_<SECTION>__<KEY>` environment variables
(`DOCMIRROR_SCOPE__MAX_PAGES=100`), then the TOML, then the defaults below.

| Section | Keys and defaults |
| --- | --- |
| `[site]` | `name`, `root_url`, `start_urls = []`, `locale` (detected from the URL), `profile = "generic"` (`mslearn` and `devsite` are built in). |
| `[scope]` | `allowed_hosts` (the start host), `path_prefixes` (the start directory), `include = []`, `exclude = []`, `max_depth = 10`, `max_pages = 5000`, `max_bytes = "2GiB"`, `meaningful_query_params = []`, `version_param`, `version_default`, `[scope.version_map]`, `sitemap_max_children = 40`. |
| `[fetch]` | `rate_per_host = 2.0`, `concurrency_per_host = 4`, `timeout_s = 30`, `retries = 5`, `robots = "respect"`, `impersonate = "chrome"`, `user_agent = ""`. `[fetch.provider]` is reserved and rejects any value. |
| `[render]` | `mode = "auto"`, `min_text_chars = 200`, `wait_until = "networkidle"`, `max_wait_s = 20`. |
| `[antibot]` | `stealth = "patchright"`, `window = 50`, `block_rate_threshold = 0.20`, `pause_s = 30`. |
| `[extract]` | `fallbacks = ["trafilatura", "readability"]`; `[extract.profiles.<name>]` overrides a profile: `main_selector`, `breadcrumb_selector`, `strip_selectors`, `meaningful_query_params`, `tabs` (or the flat `tab_group`, `tab_label`, `tab_panel`), `admonitions` (or `admonition`, `admonition_title`), `code_lang_attrs`, `heading_anchor_style = "attr"`, `interactive_selectors`, `login_wall_selector`, `last_updated_selector`, `lowercase_paths`. |
| `[convert]` | `backend = "html-to-markdown"` (or `markdownify`), `bullet = "-"`. |
| `[links]` | `path_template = "{path}"`, `keep_external_absolute = true`. |
| `[index]` | `keywords_per_page = 8`, `hierarchical_threshold = 200`, `summarizer = "none"`. |
| `[update]` | `max_age = ""`, `prune = false`. |
| `[report]` | `fail_on_low_quality = false`. |

`docmirror schema config` prints the full schema. The Microsoft Graph starter that
`init` writes sets `profile = "mslearn"`, `meaningful_query_params = ["view"]`,
`version_param = "view"` and maps `graph-rest-1.0` to `v1.0` and `graph-rest-beta` to
`beta`, so `api/user-get?view=graph-rest-1.0` lands at `api/v1.0/user-get.md`.

## What the output looks like

```text
gmail-docs/
  docmirror.toml          the configuration
  index.md                human index: an H2 per top-level directory, one line per page
  index.jsonl             agent index: one JSON object per page (schema: docmirror schema index)
  llms.txt                the llms.txt convention
  crawl-report.json       the last run (schema: docmirror schema report)
  gmail/api/guides.md     one file per page, mirroring the URL path
  _removed/               pages that returned 404/410 since the last run
  .docmirror/             the SQLite manifest and browser profiles
```

Every page begins with YAML frontmatter, keys sorted: `source_url`, `title`,
`fetched_at`, `content_sha256`, `quality_score` and `low_confidence` are always present;
`canonical_url`, `description`, `keywords`, `breadcrumbs`, `etag`, `last_modified`,
`sitemap_lastmod`, `locale`, `version`, `profile`, `extractor`, `converter`, `render`
(`http`, `browser` or `stealth`) and `quality_flags` appear when known. The hash covers
the body alone, so `fetched_at` never changes it.

Quality is measured per page: text coverage of the extracted content, code blocks and
their language tags, tables and cells, headings, links, images, list items and expanded
tab panels, weighted into `quality_score`. A failed gate sets `low_confidence` and names
itself in `quality_flags`, alongside pipeline flags such as `render_needed`,
`extractor_fallback`, `interactive_omitted`, `uncrawled_internal`, `unresolved_fragment`,
`dangling_inbound`, `soft_block_suspected`, `html_table_kept` and `empty_content`.

## Politeness and resilience

Two requests per second per host with jitter, `Retry-After` honoured, exponential
backoff, robots.txt respected unless `--robots ignore` is passed (and then recorded in
the report). A page goes through a three-tier ladder: `curl_cffi` with a browser TLS
fingerprint, then Patchright's Chromium when the page needs JavaScript or the HTTP tier
is blocked, then Camoufox when installed and configured. A per-host circuit breaker
pauses, slows and escalates a host whose block rate passes 20%, and trips (exit 3) when
the highest tier does no better. No proxies, no CAPTCHA services, no paid unblocking.

## What is lossy

Measured against the 40 captured fixture pages and the 200-page acceptance crawls; see
`docs/site-notes.md` for the site-by-site record.

- **Complex tables stay HTML.** A table with `rowspan`, `colspan` or block content in a
  cell (paragraphs, lists, nested tables, code) is kept as sanitized HTML, flagged
  `html_table_kept`. Every devsite REST reference page has such tables; their JSON
  schema samples live inside cells as `<pre>` and cannot become fences.
- **Links inside code become text.** A fence cannot carry a link, so an `<a>` inside
  `<pre>` keeps its text and loses its target.
- **Breadcrumbs are absent on Microsoft Learn.** Learn renders them client-side from a
  `toc.json`; the server HTML has none.
- **Interactive content is a placeholder.** "Try it" explorers, embedded frames and
  videos become `> [!NOTE] Interactive content omitted: <url>` with the flag
  `interactive_omitted`.
- **Images are not downloaded.** Alt text and absolute image URLs are kept; an empty
  `alt` borrows the title or figure caption.
- **Fallback extraction loses extension-less images.** When no profile selector
  matches and Trafilatura takes over, an `<img>` whose URL does not look like an image
  file keeps its place but loses its source; the `images` gate reports it.
- **Header-less tables stay HTML.** A pipe table needs a header row, so a table with
  none, or with row headers down the first column, is kept as HTML.
- **Generated panels are stripped.** devsite's "Page Summary" takeaways panel and Learn's
  "Summarize this article" controls are chrome, not content.
- **Heading anchors are an extension.** `## Heading {#id}` preserves the source id in a
  form GitHub renders as literal text; set `heading_anchor_style = "inline"` for
  `<a id="…"></a>` lines instead.
- **Math without TeX stays HTML.** `$…$` is emitted only when the source carries a TeX
  annotation or `data-tex`.
- **A JavaScript-only site under `--render never`** yields pages flagged `render_needed`
  and `empty_content`; they are low-confidence by definition.

## Development

The repository's gates are driven by `just`; `docs/how-to/develop-locally.md` has the
first-run steps. `just check` runs the offline gates, `just py-test-live` the live
crawls, `just py-test-oracle` the fidelity oracles (Learn's MCP endpoint and devsite's
`.md.txt` pages), `just install-browser` the Chromium download.

## Provenance and licence

Built from `docmirror_POC_Build_Prompt.md` on a branch of the `alliumpy` repository,
whose toolchain it reuses; decision 0015 in `docs/decisions/` records the arrangement.
Apache-2.0, see `LICENSE`.
