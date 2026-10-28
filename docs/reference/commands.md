---
title: "Commands"
kind: "reference"
audience: ["contributor", "maintainer", "operator", "agent"]
canonical_for: ["command_reference"]
requires: []
---

# Commands

`just --list` prints the live set. This page says what each recipe is for. The `Justfile`
is the supported interface: if something is worth running twice, it belongs there
rather than in a shell history.

`initialize`, `install-hooks`, `install-browser`, `sync`, `lock`, `lock-upgrade`,
`py-test-live`, `py-test-oracle` and `check-links-online` reach the network.
Initialization prepares the caches; later `check` runs need no network. A cold cache
fails instead of fetching. Setup recipes and mutating recipes sit outside `check`.

## Setup

| Recipe | Purpose |
| --- | --- |
| `default` | Print the recipe list when just has no arguments. |
| `initialize` | Install pixi's pinned environment, including the package, and prepare hooks only in the primary checkout. Never formats, stages, commits, tags or pushes. |
| `sync` | Install pixi's committed resolution without rewriting the lock. |
| `lock` | Relock after a manifest edit. Read the diff. |
| `lock-upgrade` | Move the resolution within manifest constraints. |
| `lock-check` | Compare the manifest to the lock offline without writing. |
| `install-hooks` | Install the shared hook shim and prepare environments; primary checkout only. |
| `install-browser` | Download the Chromium build Patchright drives, for the browser tier. |

## Format and check

| Recipe | Purpose |
| --- | --- |
| `format` | Write ruff and taplo formatting. |
| `fix` | Run the mutating hook configuration twice, then lint. |
| `lint` | Run the complete read-only hook gate over all files. |
| `toml-check` | Check TOML formatting and lint. |

## Python

| Recipe | Purpose |
| --- | --- |
| `py-lint` | Ruff lint and format; require the package in its input and the positive fixture's F401 and E501 failures. |
| `py-typecheck` | mypy over the package, tests and scripts; require the deliberate type-error fixture to fail with status 1. |
| `py-test` | The offline suites: unit and golden tests. |
| `py-test-accept` | Rerun the golden suite and rewrite changed snapshots. Read the diff. |
| `py-test-live` | Real crawls of the target sites behind the `live` marker. |
| `py-test-oracle` | Fidelity against upstream Markdown endpoints behind the `oracle` marker. |
| `wheel` | Empty dist and build the wheel with the environment's hatchling, offline. |
| `wheel-smoke` | Build the wheel, require exactly one, install it offline into a fresh venv that sees the environment's dependencies, run the isolated smoke and the console script. |
| `version-check` | Compare the manifest version, `__version__` and the smoked command's output; a missing smoke venv fails. |

## Documents

| Recipe | Purpose |
| --- | --- |
| `check-docs` | markdownlint, typos and offline links, then the documentation contract. |
| `check-agents` | Validate the agent inventory, adapters, skills and bridges. |
| `check-links-online` | Resolve external links manually; network failures keep it outside check. |

## Aggregate

| Recipe | Purpose |
| --- | --- |
| `check` | Run the ten configured gates in order with worktree snapshots, then check-clean. |
| `check-clean` | Require a clean worktree, or equality with a supplied baseline. |

## Related pages

- [Quality gates](quality-gates.md)
- [Develop locally](../how-to/develop-locally.md)
