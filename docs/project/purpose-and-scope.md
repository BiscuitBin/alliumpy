---
title: "Purpose and scope"
kind: "project"
audience: ["user", "contributor", "maintainer", "agent"]
canonical_for: ["project_purpose", "project_non_goals"]
requires: []
---

# Purpose and scope

`alliumpy` packages the upstream Allium parser for Python code and provides the
`allium` command for uv users. The repository is Apache-2.0; upstream's MIT text ships
beside it. The [architecture](../explanation/architecture.md) describes the two crates;
[Python packaging](../explanation/packaging.md) explains the one wheel they build.

## What it does

Python callers can parse source into immutable diagnostics. The conversion preserves
upstream messages, severities and order, translating byte spans into one-based source
locations. The console script currently answers `-V` and `--version` only; T13 adds the
upstream command behaviour. T14 publishes the first wheel to PyPI.

## What it deliberately does not do

This repository does not define the Allium language, reinterpret parser results or
maintain a competing parser. Upstream decides behaviour; a difference is a defect here
unless a decision record says otherwise. The handbook documents packaging and engineering,
rather than teaching the language. S01 recommends keeping the source distribution;
T13 records decision 0014.

## Who it is for

Python applications consume the bindings; uv users consume the console script.
Contributors maintain the conversion and packaging boundary and test it against upstream.
Neither consumer needs to choose a separate parser version.

## Related pages

- [Install and run](../how-to/install-and-run.md)
- [Repository map](repository-map.md)
- [Terminology](terminology.md)
