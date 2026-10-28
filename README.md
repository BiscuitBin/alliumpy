# docmirror

`docmirror` turns a product's documentation website into a local, interlinked Markdown
knowledge base and keeps it up to date on later runs. It is for people at a terminal and
for AI coding agents that need a trustworthy offline copy of an API's documentation.

This repository is a proof of concept built from `docmirror_POC_Build_Prompt.md` on the
tooling of the `alliumpy` repository, which hosts it on a branch that will not merge.
The full README (installation, quick start, configuration reference, exit codes and the
"What is lossy" section) lands with the final phase; `docs/README.md` is the handbook map
until then.

## Status

Phase 0: the repository is rebuilt around the Python package; `docmirror init`, `doctor`,
`schema` and `report` work; `crawl`, `update`, `verify`, `index` and `fetch` arrive in the
following phases.

## Licence

Apache-2.0, as recorded in `LICENSE` and decision 0015.
