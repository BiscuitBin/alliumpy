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
| Nix, with the `nix-command` and `flakes` features | Builds the dev shell `flake.nix` describes and `flake.lock` pins: the compiler from `rust-toolchain.toml`, Python and every tool the gates run, `just` included. Install it once per machine with any installer; the repository uses it only through its own flake and never changes anything else on the machine. |
| `git` | The flake sees only files Git tracks. |
| `direnv`, optional | Enters the dev shell on `cd` through the checked-in `.envrc` once you allow it with `direnv allow`. |
| `gh` | Only for the pin-bump commands in [Maintain dependencies](maintain-dependencies.md). |

Nothing else. The dev shell carries the C and C++ compiler the fuzz crate's build needs,
and builds cargo-fuzz for the host, so Apple silicon needs no Rosetta. Which tool comes at
which version is [decision 0018](../decisions/0018-nix-owns-the-tools.md)'s and
`flake.lock`'s; [Configuration](../reference/configuration.md) names each file. The
Justfile supports POSIX development on Linux x86_64 and macOS arm64, and the dev shell
also builds on Linux arm64, for a container on an Apple silicon Mac. The release workflow
builds the other wheel platforms ([decision 0015](../decisions/0015-release-process.md)).

## First run

Nix is installed once per machine. Everything after it comes from this repository's
pins. In the clone, enter the dev shell:

```console
nix --extra-experimental-features 'nix-command flakes' develop --no-update-lock-file
```

(plain `nix develop --no-update-lock-file` where those features are already enabled, or
`direnv allow` once and then just `cd` into the clone; `.envrc` passes the same flag). The
first entry downloads and builds the shell, several gigabytes, and needs the network; later
entries reuse the store and work offline. With `--no-update-lock-file`, entering the shell
never rewrites `flake.lock`: a lock that no longer matches `flake.nix` stops the entry
instead, and `just lock` is the fix. The recipes name the experimental features on every
Nix command they run, so they work whether or not your Nix enables them. Then, inside it:

```console
just initialize
just check
```

`just initialize` checks the compiler, fetches the crates `Cargo.lock` and
`fuzz/Cargo.lock` name, and installs the pre-commit hook; it needs the network for the
crates. It never formats, stages, commits, tags or pushes. The hook is installed from the
primary checkout only, because every worktree shares one `.git/hooks`; in a secondary
worktree `just initialize` says so and skips it. Every hook is a tool the shell holds,
so nothing is prepared or fetched for them, and once the crates are fetched
the whole of `just check` is offline.

`just check-toolchain` refuses a compiler that is not the pinned one before anything else
runs. It asks whether cargo and the compiler it runs are the pinned release with the
pinned components, and that they come from the Nix store, so a cargo ahead of the shell's
on `PATH` is refused with both versions named:

```text
check-toolchain: cargo is 1.96.0, not the pinned 1.99.1 (/opt/homebrew/bin/cargo)
```

Outside the shell `just` itself refuses to load, because only the shell sets
`ALLIUMPY_PYTHON`, and `just initialize` refuses with the command that enters it.

Inside the dev shell every tool is on your shell's `PATH` too, so `cargo nextest` and the
others run directly. Commit from inside the shell as well: the installed hook calls the
shell's tools by name, and a commit from outside it fails rather than passing.

## Every day

```console
just build
just test
just doc
```

`just build` compiles the workspace with every feature. The workspace consists of
`alliumpy-core` and the thin `alliumpy` bindings. Run `just py-develop` to build the
extension and install it editable, then `just py-test` for its Python tests. The
install goes into a virtual environment under `target/py-develop/`, built on the dev
shell's interpreter and seeing its pytest and mypy, because the shell's own environment
is in the read-only store. The recipes put that environment first on `PATH`, so `python`
in a recipe is the interpreter that can import the extension.
The Justfile sets `PYO3_PYTHON` to the dev shell's own interpreter, `ALLIUMPY_PYTHON`,
for every Cargo invocation. Set it to that same path when invoking Cargo directly.

`just build` compiles the workspace with every feature. `just test` runs the unit and
integration tests through nextest, then the doctests. `just doc` builds the API
documentation into `target/doc/`, with warnings as errors, as CI does.

## Before handing work back

```console
just fix       # formats and applies the safe automatic repairs
just check     # the whole gate, read-only
```

Of the two, only `just fix` modifies files; outside the pair, `just lock` and
`just format` write too. Every check is read-only, and `just check` proves it by comparing
the worktree before and after each recipe.

## Keeping the workspace current

After pulling, re-sync so the installed dependencies match the lockfiles:

```console
just sync
```

It fetches what `Cargo.lock` and `fuzz/Cargo.lock` name. A moved `flake.lock` takes
effect on the next shell entry, which downloads what changed: leave the shell and enter
it again, or let direnv do it.

## Related pages

- [Commands](../reference/commands.md)
- [Test and debug](test-and-debug.md)
- [Troubleshooting](../operations/troubleshooting.md)
- [Configuration](../reference/configuration.md)
