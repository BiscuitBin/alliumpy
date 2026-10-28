# Acceptance crawl examples

Committed output of the two 200-page acceptance crawls from the build prompt, run
with the released `docmirror` wheel installed through `uv tool install .`:

- `graph/`: `docmirror init https://learn.microsoft.com/en-us/graph/api/overview`
  then `docmirror crawl --max-pages 200` (profile `mslearn`).
- `gmail/`: the same against `https://developers.google.com/workspace/gmail/api/guides`
  (profile `devsite`).

Each directory holds the run's `crawl-report.json` and, under `samples/`, ten pages
chosen at a fixed stride through the sorted path list, with the path's slashes replaced
by `__` in the file name. Every sample is byte-identical to the crawl output, so the
frontmatter, the relative links and the `content_sha256` are the real ones. The links
point at the rest of the mirror, which is not committed.

The numbers behind the acceptance summary (mean `quality_score`, low-confidence rate,
tiers used, gate failures) are in the reports; `docs/site-notes.md` records the site
behaviour behind each remaining gate failure and unresolved fragment.
