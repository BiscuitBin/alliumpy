# The parity corpus

The inputs `just parity` runs both `allium` commands on (`tests/parity/README.md`).

## Upstream's files

Every `.allium` file in `juxt/allium-tools` at tag `v3.6.1` (27 files), in upstream's
directory shape and with no edit: one `gh api` read per path from
<https://github.com/juxt/allium-tools/tree/v3.6.1>, each checked with `git hash-object`
against the blob sha in that tag's tree. They are upstream's files under upstream's MIT
licence, whose full text ships as `crates/alliumpy/LICENSE-allium-tools`. Nothing in this
repository edits them; a bump replaces them all at the new tag.

## This repository's files

`alliumpy/xmod/core.allium` and `alliumpy/xmod/app/orders.allium` are written for this
repository (Apache-2.0, as the rest of it) and contain no upstream text. Upstream's tree
at `v3.6.1` has no local cross-module `use`, so this pair supplies one: `orders.allium`,
in a subdirectory, `use`s `../core.allium` as `core` and references it. The harness
finds the pair and compares it named together in both orders, in the directory form and
as the importer alone.

## What the corpus covers

Upstream's parser fixtures, its own specifications under `docs/project/specs/` and its
editor extension's format and refactor fixtures, plus the pair above. It is thin on
cross-module resolution (one pair) and on modules with two or more entities carrying
`when`-qualified fields, the one path where upstream's `plan` iterates a hash map into
its output; parity is only as strong as the corpus.
