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

## Profiles

The selector verification for `mslearn` and `devsite` is recorded here, selector by
selector, as phase 2 captures fixtures from the live pages. Until then the profiles carry
the build prompt's starting points.

## Related pages

- [Build decisions](decisions.md)
- [Purpose and scope](project/purpose-and-scope.md)
