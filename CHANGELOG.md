# Changelog

All notable changes to docmirror are recorded here. The format follows Keep a Changelog
and the versions follow semantic versioning once there is a release to version.

## [Unreleased]

- The repository is rebuilt around the `docmirror` package, on the toolchain carried from
  `alliumpy` (pixi, just, prek, ruff, mypy, pytest and the `bg-*` validators).
- `docmirror init`, `doctor`, `schema` and `report` subcommands.
- `docmirror crawl`: sitemap, llms.txt and link discovery, polite curl_cffi fetching, the
  `mslearn` and `devsite` profiles, DOM normalization for tabs, code languages,
  admonitions, tables, definition lists, details, images, math, footnotes and
  interactive embeds, two converter backends, frontmatter, quality gates and the report.
- Golden tests over 39 captured pages with syrupy snapshots.
