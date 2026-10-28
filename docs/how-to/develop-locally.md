---
title: "Develop locally"
kind: "how-to"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["local_development"]
requires: []
---

# Develop locally

## Prerequisites

| Tool | Why |
| --- | --- |
| `pixi`, 0.81.0 or newer | Installs every tool, the Python environment and the package itself from `pixi.lock` into the gitignored `.pixi/envs/default`. |
| `just` | The task runner, and the only supported interface to the checks. `pixi global install just` provides one. Any `just` launches the recipes, because the pinned one in the environment runs every nested call and CI; `pixi run --frozen just <recipe>` is the escape hatch when no global `just` is installed. |

Nothing else: not uv, not a system Python. `pyproject.toml` names every tool and
`pixi.lock` pins it. The Justfile supports POSIX development on Linux x86_64 and macOS
arm64, which are the pixi platforms.

## First run

Install pixi using its own installation documentation; the floor is `requires-pixi` in
`pyproject.toml`. Then install a global `just` if your shell has none and run the one
first-run command:

```console
pixi global install just
just initialize
```

This installs the pixi environment from `pixi.lock`, which includes `docmirror` itself
as an editable install with its test extras, and installs the pre-commit hook with every
hook environment. Run it once per clone. It needs the network for the environment and
the hook clones. It never stages, commits, tags or pushes.

The hook is installed from the primary checkout only, because every worktree shares one
`.git/hooks`. In a secondary worktree `just initialize` says so and skips it, and the
first `just lint` there clones any hook environment the primary checkout has not already
built, which needs the network too. `just check` runs `lint` as its second gate and adds
no network need of its own, so once the hook environments exist the whole gate is offline.

The browser tier is separate: `just install-browser` downloads the Chromium build that
Patchright drives. The gate never needs it; the live suite and a real crawl of a
JavaScript-rendered site do. `docmirror doctor` reports whether it is present.

`.pixi/envs/default/bin` is gitignored, and the `Justfile` prepends it to `PATH` for
every recipe. It is not on your shell's `PATH`, so a bare `docmirror` or `pytest` from a
shell needs `PATH="$PWD/.pixi/envs/default/bin:$PATH"`, a recipe, or
`pixi run --frozen docmirror`.

## Every day

```console
just py-test
just py-lint
just py-typecheck
```

`just py-test` runs the offline suites: the unit tests and the golden tests over the
captured fixtures. A changed golden snapshot is reviewed with `just py-test-accept`,
which rewrites the `.ambr` files; read the diff and explain it in the commit. The live
and oracle suites reach the network and have their own recipes, `just py-test-live` and
`just py-test-oracle`; run them only when the task authorises it.

A real crawl for inspection goes under `ai_tmp/`, which is gitignored:

```console
docmirror init https://developers.google.com/workspace/gmail/api/guides ai_tmp/gmail
docmirror crawl ai_tmp/gmail --max-pages 10
```

## Before handing work back

```console
just fix       # formats and applies the safe automatic repairs
just check     # the whole gate, read-only
```

Of the two, only `just fix` modifies files; outside the pair, `just lock`,
`just format` and `just py-test-accept` write too. Every check is read-only, and
`just check` proves it by comparing the worktree before and after each recipe.

## Keeping the workspace current

After pulling, re-sync so the installed environment matches the lockfile:

```console
just sync
```

It installs a moved `pixi.lock` exactly as committed, including the package's own
dependencies. After editing `pyproject.toml`, run `just lock` (network) and commit the
lockfile with the manifest; `just lock-check` fails until the two agree.

## Related pages

- [Commands](../reference/commands.md)
- [Troubleshooting](../operations/troubleshooting.md)
