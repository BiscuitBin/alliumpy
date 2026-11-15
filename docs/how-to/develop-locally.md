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
| Nix, with the `nix-command` and `flakes` features enabled | Builds the dev shell `flake.nix` defines and `flake.lock` pins: the exact Rust toolchain `rust-toolchain.toml` names, Python, every tool a recipe or hook calls, and the C++ compiler the fuzz crate's libFuzzer build needs. Nothing else is installed on the machine. |
| `gh` | Only for the pin-bump commands in [Maintain dependencies](maintain-dependencies.md). |

Nothing else: not rustup, not just, not uv, not Python. The dev shell carries all of them,
and the `Justfile` refuses to run outside it ([decision 0018](../decisions/0018-nix-dev-environment.md)).
The shell is defined for Linux x86_64 and macOS on Apple silicon. CI builds it on both
(`macos-smoke` is the Apple silicon proof). The release workflow builds the other wheel
platforms ([decision 0015](../decisions/0015-release-process.md)).
[Configuration](../reference/configuration.md) has each file and variable; this page
names no version.

Install Nix with its own installer or with the Determinate Systems installer. Either
works; the Determinate one enables flakes for you. With the upstream installer, add this
line to `~/.config/nix/nix.conf` (or `/etc/nix/nix.conf`):

```text
experimental-features = nix-command flakes
```

## First run

```console
nix develop
just initialize
```

`nix develop` downloads the toolchain and the tools the first time, mostly prebuilt from
`cache.nixos.org`, and builds the two that nixpkgs lacks (rustqual and the shared
checkers). Later entries are offline and take a second. `just initialize` then proves
the shell with `just check-toolchain`, fetches what `Cargo.lock` and `fuzz/Cargo.lock`
name, records the shell as a garbage-collector root under the gitignored `.nix/`, and
installs the pre-commit hook. Run it once per clone. It needs the network for the cargo
fetch, and never stages, commits, tags or pushes.

The hook is installed from the primary checkout only, because every worktree shares one
`.git/hooks`. In a secondary worktree `just initialize` says so and skips it. The hook
is a committed shim, `scripts/pre-commit-hook.sh`, that names no store path: it runs prek
inside the dev shell of whichever checkout the commit is made in, entering the shell
itself when the commit comes from an editor or a terminal outside it. Every hook runs a
binary the shell provides, so nothing is cloned or downloaded, and the whole gate is
offline once the shell exists.

### From a shell that is not the dev shell

Agents, scripts and one-off commands use one spelling:

```console
nix develop --command just check
```

Any other spelling refuses before the recipe runs
([Troubleshooting](../operations/troubleshooting.md#error-not-in-the-dev-shell)).

### direnv

The committed `.envrc` holds `use flake`. After `direnv allow` once, entering the
directory enters the shell. nix-direnv makes it cache the shell. It is opt-in, and the
recipes do not depend on it.

### A stale shell

The shell records a digest of `flake.nix`, `flake.lock`, `rust-toolchain.toml` and the
files under `nix/`. After a pull, a `just lock` or an edit that moved one of them, the
first gate refuses the old shell; leave it and run `nix develop` again
([Troubleshooting](../operations/troubleshooting.md#check-toolchain-the-dev-shell-is-stale)).

## Every day

```console
just build
just test
just doc
```

`just build` compiles the workspace with every feature. The workspace consists of
`alliumpy-core` and the thin `alliumpy` bindings. `just test` runs the unit and
integration tests through nextest, then the doctests. `just doc` builds the API
documentation into `target/doc/`, with warnings as errors, as CI does.

Inside the shell every tool is on `PATH`, so `cargo nextest run -p alliumpy-core` works
directly. The shell exports `PYO3_PYTHON`, so a bare `cargo` builds the bindings against
the shell's Python too. Run `just py-develop` to build the extension into the venv
`target/py-env`, then `just py-test` for its Python tests; for one file,
`target/py-env/bin/python -m pytest crates/alliumpy/tests/test_parse.py`.

## Before handing work back

```console
just fix       # formats and applies the safe automatic repairs
just check     # the whole gate, read-only
```

Of the two, only `just fix` modifies files; outside the pair, `just lock` and
`just format` write too. Every check is read-only, and `just check` proves it by comparing
the worktree before and after each recipe.

## Keeping the workspace current

After pulling, leave the shell and enter it again if `flake.lock` moved, then re-sync so
the cargo cache matches the lockfiles:

```console
just sync
```

It fetches what `Cargo.lock` and `fuzz/Cargo.lock` name and moves the `.nix/dev-shell`
root to the current shell, so a store garbage collection keeps it. It rewrites no
lockfile.

## Related pages

- [Commands](../reference/commands.md)
- [Test and debug](test-and-debug.md)
- [Troubleshooting](../operations/troubleshooting.md)
- [Configuration](../reference/configuration.md)
- [Decision 0018: Nix owns the development environment](../decisions/0018-nix-dev-environment.md)
