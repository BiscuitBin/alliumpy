---
title: "Site notes"
kind: "reference"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["site_behaviour", "profile_selectors"]
requires: []
---

# Site notes

What the live sites actually do, verified during the build, and where that differs from
the build prompt's starting points. The prompt says to follow the site, implement the
general mechanism and record the deviation here; a hostname never appears in code, so
every finding below lands in a profile under `src/docmirror/config/profiles.py`.

## Reachability, as probed on 2026-10-28

| Endpoint | Result |
| --- | --- |
| `https://learn.microsoft.com/en-us/graph/api/overview` | `301` to the same path with `?view=graph-rest-1.0` appended: the version parameter is part of the identity of a Graph reference page. |
| `https://learn.microsoft.com/sitemap.xml` | `302` to `/en-us/sitemap.xml`; `robots.txt` names `https://learn.microsoft.com/_sitemaps/sitemapindex.xml`, which covers the whole site, so sitemap discovery must stream-filter by scope rather than load it whole. |
| `https://developers.google.com/workspace/gmail/api/guides` | `200`, 168 KB of server-rendered HTML; `robots.txt` names `https://developers.google.com/sitemap.xml`. |
| `https://developers.google.com/workspace/gmail/api/guides.md.txt` | `200`, 5 KB of Markdown: the oracle for devsite pages works. |
| `https://learn.microsoft.com/api/mcp` | `200` to a JSON-RPC `tools/list` POST: the Learn MCP oracle is reachable. |

## JavaScript-rendered candidates for the escalation test

Probed without JavaScript, these serve an empty shell: `https://redocly.github.io/redoc/`
(623 bytes, a `#root` div), `https://docs.zoom.us/` (187 KB with zero text), and
`https://petstore.swagger.io/` (10 characters of text). The one used by the live suite is
recorded here when phase 5 lands.

## Sitemaps

Learn's `sitemapindex.xml` lists 5,497 child sitemaps named by product and locale
(`graph_en-us_1.xml`, `dotnet_zh-cn_12.xml`, `previous-versions_en-us_3.xml`). Reading
them all at the polite rate takes most of an hour, so discovery ranks children by the
scope's own tokens (a non-locale segment of a path prefix such as `graph`, and the
pinned locale), drops children that name another locale, and reads at most
`[scope] sitemap_max_children` (default 40) of them. For Graph this reads the
`graph_en-us_*` files first and finds every Graph page in seconds. devsite's
`sitemap.xml` is an index of 40 unnamed children (`sitemap_24_of_40.xml`); none can be
ranked, so the budget reads them in order and stops once `max_pages × 4` in-scope
URLs are queued. Sitemap entries queue at depth 2, one hop below the start page's own
links, so a small crawl stays near the start URL.

## Profiles

Every selector below was checked against the captured fixtures under
`tests/fixtures/<profile>/`. "Prompt" is what the build prompt proposed; "Site" is what
the HTML holds.

### mslearn (Microsoft Learn, Microsoft Graph)

| Construct | Prompt | Site | Profile |
| --- | --- | --- | --- |
| Main content | `main#main`, `div.content` | `main#main` holds the article; `div.content` is a child wrapper. | As the prompt. |
| Breadcrumbs | `ul#breadcrumbs, .breadcrumbs` | Rendered client-side from `/graph/ref-breadcrumb/toc.json` (a `<meta name="breadcrumb_path">`); the server HTML has no trail. | Selector kept; `breadcrumbs` is absent on Learn pages. |
| Tab groups | `.tabGroup` with `ul[role=tablist] a[data-tab]` and `section[data-tab]` | Exactly that; inactive panels carry `hidden`. | As the prompt; `hidden` on a `section` is never stripped. |
| Admonitions | `div.alert` with `p.alert-title` | `div.NOTE`, `div.TIP`, `div.IMPORTANT`, `div.WARNING`, `div.CAUTION`; the kind is the class and the label is the first `<p>`. | Both shapes; kind from the class. |
| Code | `pre > code.lang-*` | `code.lang-http`, `lang-json`, `lang-csharp`; interactive samples are `lang-msgraph`, which is HTTP. | `msgraph` is an alias of `http`. |
| Chrome inside `main` | `.page-metadata`, `#user-feedback`, `nav`, `[data-bi-name=feedback]` | Also the table-of-contents header, the "Exit editor mode" and "Summarize this article" buttons, an `[unauthorized-private-section]` notification (hidden) and `details.popover` menus. | All stripped; `button` is stripped wholesale. |
| Last updated | `<time>` in the header | `<local-time datetime="…">` inside `ul.page-metadata`. | `local-time[datetime], time[datetime]`, read before the metadata is stripped. |
| Query parameters | `view` meaningful, `tabs` not | Reference URLs 301 to `?view=graph-rest-1.0`; `tabs=` only selects a tab. | `view` is the version parameter; `tabs` is dropped. |

### devsite (developers.google.com, Google Workspace)

| Construct | Prompt | Site | Profile |
| --- | --- | --- | --- |
| Main content | `article.devsite-article`, `.devsite-article-body` | `article.devsite-article` holds the article plus its meta block. | As the prompt. |
| Breadcrumbs | not given | `ul.devsite-breadcrumb-list` inside `.devsite-article-meta`. | `.devsite-breadcrumb-list`, read before the meta block is stripped. |
| Tab groups | `devsite-selector` with `section[aria-labelledby]`, or `devsite-tabs` / `div[role=tabpanel]` | `devsite-selector` holds one `<section>` per tab whose first `<h3>` is the label; there is no server-rendered tablist. `devsite-tabs.upper-tabs` is site navigation, not content. | `devsite-selector` with `panel_heading = "h2, h3, h4"`; `devsite-tabs:not(.upper-tabs)` kept for the role-based shape. |
| Admonitions | `aside.note`, `.caution`, `.warning`, `.key-point`, `.objective` | Those plus `aside.special` ("Important:"), `aside.tip`, `aside.beta`, `aside.deprecated`; the label is a leading `<strong>`. | All of them, kind from the class, `special` mapped to IMPORTANT. |
| Code | `pre.prettyprint[class*=lang-]` or `devsite-code pre` | `devsite-code > pre[syntax="Python"]`; terminals are `code.devsite-terminal`; REST reference JSON is a bare `<pre style>` inside a table cell. | `syntax` is the first language attribute; `devsite-terminal` is `bash`; `Bash Session` is an alias of `bash`. |
| Chrome inside the article | `devsite-feedback`, `.devsite-article-meta`, `devsite-toc`, `.devsite-banner`, `devsite-page-rating` | Also `devsite-thumb-rating`, `devsite-recommendations-*`, `.nocontent`, `[data-nosnippet]` and the generated "Page Summary" panel `devsite-key-takeaways-panel`. | All stripped. |
| Reference tables | plain tables | Parameter tables use `colspan` headers and block cells with `<p>`, nested `<table>` and `<pre>`, so they stay HTML; the JSON representations inside them cannot be fences. | `html_table_kept` on every REST reference page. |
| Last updated | `<time>` | None in the HTML. | The `Last-Modified` header is used. |

## Related pages

- [Build decisions](decisions.md)
- [Purpose and scope](project/purpose-and-scope.md)
