---
title: "Troubleshooting"
kind: "operations"
audience: ["contributor", "maintainer", "operator", "agent"]
canonical_for: ["troubleshooting"]
requires: []
---

# Troubleshooting

Symptoms as headings, causes and fixes as bodies.

## `just check` reports that a recipe changed the worktree

The recipe is the defect, not your change. Checks are read-only; anything that writes
belongs in `.pre-commit-fix.yaml` and runs from `just fix`. The report names which paths
moved. Move the offending hook, or add the generated path to the ignore rules.
Here the usual paths are a build or tool directory that escaped the ignore rules —
`target/`, `dist/` or `.pixi/` — or a rewritten `pixi.lock`, which means a recipe
resolved dependencies instead of reading the lockfile. A crawl run for inspection
belongs under `ai_tmp/`, never beside the sources.

## `docs validation: frontmatter <field> disagrees with the manifest`

Almost always list order. The comparison between `docs/manifest.yml` and a page's
frontmatter is order-sensitive, so `[maintainer, contributor]` fails against
`["contributor", "maintainer"]`. Copy the order from the manifest.

If the field is `title`, check for a stray difference in punctuation — the level-one
heading must match it byte for byte as well.

## `docs validation: not reachable from docs/README.md`

The page exists and is registered, but nothing links to it. Add it to
[the documentation map](../README.md), or to a page that is already reachable.

## `agent validation: unexpected managed file`

Something appeared under `.agents/`, `.claude/` or `.codex/` that is neither a declared
skill nor `.claude/settings.json`. If it is local tool state, add it to `.gitignore` —
the inventory reads Git, so an ignored file is invisible to it. If it is real content, it
belongs in `.agents/skills/` with bridges, or somewhere else entirely.

## `agent validation: must stay a thin pointer to the canonical skill`

A bridge under `.claude/` or `.codex/` has grown content, or its frontmatter has drifted
from the canonical skill. Regenerate it: the canonical frontmatter verbatim, one blank
line, then the fixed pointer sentence and nothing else. The body is compared against a
template rather than measured, so a clause of your own fails however short it is —
[Agent contract](../reference/agent-contract.md#what-a-bridge-must-be) carries the text.

## A recipe cannot find `prek` or a `bg-*` script

The pixi environment under `.pixi/` is installed per worktree, and a fresh worktree has
none. `pixi install --frozen` restores it, and `just initialize` does that and the hooks.
A worktree
that was renamed or moved needs `pixi install --frozen` again even though `.pixi/` is
there: the `bg-*` scripts' shebangs name the Python at the worktree's old absolute path.

## `just lock-check` or `pixi install --locked` fails on `pixi.lock`

`pixi.lock` is stale against `pyproject.toml`: a pin moved in the manifest and the
lockfile was not solved again. Run `just lock`, read the diff, and commit the lockfile.

## `just lint` clones or downloads

Every hook environment should already be prepared, so `lint`, and `just check` around
it, never reaches the network. If it does, prek's cache was cleared, or this is a
secondary worktree whose primary checkout never ran `just initialize`. Run
`just install-hooks` from the primary checkout; it prepares every hook environment and
warms the link checker. `just initialize` is where the network belongs, and `just check`
must not need it.

## The ripsecrets hook fails to install: the package believes it is in a workspace

`PREK_HOME` points inside a Cargo workspace. ripsecrets is a Rust hook, built in prek's
cache with the machine's rustup, and a build under a workspace root is taken for a
member of it. Point `PREK_HOME` at a directory outside any checkout, as CI does with the runner's
temporary directory, and run `just install-hooks` again.

## prek behaves as if a pin had not moved

A hook whose `rev` changed still runs its old environment. Clear prek's cache with
`pixi run --frozen prek cache clean`, then run `just install-hooks` again to prepare
every environment from the current configuration.

## `uv build` cannot import hatchling

`just wheel` builds without isolation so that the build never reaches the network, and
passes the pixi interpreter explicitly because uv would otherwise pick a Python from the
shell. If the message names a missing `hatchling`, the pixi environment is stale: run
`just sync`.

## `docmirror doctor` reports the Patchright browser as missing

The browser tier needs a Chromium build that Patchright downloads on request; the pixi
environment does not carry it. Run `just install-browser` (network). The gate never
needs it; a crawl of a server-rendered site never escalates, and `--render never`
records `render_needed` on pages that would have.

## A golden test fails after a converter or profile change

That is the gate doing its job: the snapshot under `tests/golden/__snapshots__/` is the
reviewed output for a captured page. Read the diff. If the new output keeps more of the
page, accept it with `just py-test-accept` and explain the change in the commit; if it
keeps less, the change is a regression.

## wheel-smoke reports two wheels in dist

`just wheel-smoke` calls wheel, which empties dist before building. Check whether a
concurrent build or manual copy added an artefact after that cleanup; stop that writer
and rerun. Do not weaken the exactly-one-wheel guard or choose an arbitrary glob match.

## Related pages

- [Develop locally](../how-to/develop-locally.md)
- [Quality gates](../reference/quality-gates.md)
