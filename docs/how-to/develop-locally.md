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
| `rustup` | Installs the exact toolchain `rust-toolchain.toml` pins, and provides the only cargo the gate accepts. `~/.cargo/bin` must come ahead of `~/.pixi/bin` on `PATH`, or run `pixi global uninstall rust`. |
| `pixi`, 0.81.0 or newer | Installs every other tool, and the Python environment the hook gate runs on, from `pixi.lock` into the gitignored `.pixi/envs/default`. |
| `just` | The task runner, and the only supported interface to the checks. `pixi global install just` provides one. Any `just` launches the recipes, because the pinned one in the environment runs every nested call and CI; `pixi run --frozen just <recipe>` is the escape hatch when no global `just` is installed. |
| A C++ compiler | libfuzzer-sys's build script compiles libFuzzer's C++ whenever the fuzz crate builds, so `just check`'s `clippy` line over `fuzz/` needs one: Xcode's command-line tools on macOS, `g++` on Ubuntu, which the runner image carries. That line is plain cargo and needs nothing else. |
| Rosetta 2, on Apple silicon | For `just fuzz` and `just fuzz-build` only: cargo-fuzz 0.13.2 publishes an x86_64 macOS binary and no arm64 one (`softwareupdate --install-rosetta`). |
| `gh` | Only for the pin-bump commands in [Maintain dependencies](maintain-dependencies.md). |

Nothing else: not uv, not cargo-binstall. `rust-toolchain.toml` names the exact
toolchain, its components, and rustup installs them the first
time cargo runs here. `pyproject.toml` names every other tool and `pixi.lock`
pins it, with `tools.txt` and `tools-source.txt`, one line each, the exceptions for what
conda-forge lacks.
[Configuration](../reference/configuration.md) has each figure; this page states none.
The Justfile supports POSIX development on Linux x86_64 and macOS arm64.
The release matrix adds other wheel platforms in T14.

## First run

Two tools are installed once per machine, and everything after them comes from this
repository's pins.

Install rustup and pixi using their own installation documentation. Ensure rustup's
cargo proxy is first on `PATH`. The pixi floor is `requires-pixi` in `pyproject.toml`.
Then install a global `just` if your shell has none:

```console
pixi global install just
```

One hazard catches almost everyone once. A cargo from `pixi global`, Homebrew's `rust`
formula or a Linux distribution ignores `rust-toolchain.toml` and builds with whatever
release it happens to be, so the lint set and the target list silently differ from CI's.
`just check-toolchain` refuses it before anything else runs, with one of two lines:

```text
rustup is not installed; see docs/how-to/develop-locally.md
cargo resolves to /home/you/.pixi/bin/cargo, not rustup's proxy
```

The remedy is `~/.cargo/bin` ahead of `~/.pixi/bin` on `PATH`, or
`pixi global uninstall rust`. The repository's own pixi environment holds no cargo and is
not the hazard; a `pixi global` rust is.

```console
just initialize
```

This installs the pixi environment from `pixi.lock`, installs the pinned toolchain,
refuses a cargo that is not rustup's, installs cargo-hack and cargo-fuzz from `tools.txt` and builds
rustqual from `tools-source.txt` into `.tools/bin`, syncs the three
lockfiles, and installs the pre-commit hook with every hook
environment. Run it once per clone. It needs the network for the pixi environment, the
toolchain, cargo-hack, rustqual's source, `cargo fetch` and the hook clones. It never stages, commits, tags or pushes.

The hook is installed from the primary checkout only, because every worktree shares one
`.git/hooks`. In a secondary worktree `just initialize` says so and skips it, and the
first `just lint` there clones and builds any hook environment the primary checkout has
not already built, which needs the network too. `just check` runs `lint` as its third
gate and adds no network need of its own, so once the hook environments exist the whole
gate is offline.

`.pixi/envs/default/bin` and `.tools/bin` are both gitignored, and the `Justfile`
prepends them to `PATH`, in that order, for every recipe. They are not on your shell's
`PATH`, so a bare `cargo nextest` from a shell needs
`PATH="$PWD/.pixi/envs/default/bin:$PWD/.tools/bin:$PATH"`, a recipe, or
`pixi run --frozen cargo nextest`.

## Every day

```console
just build
just test
just doc
```

`just build` compiles the workspace with every feature. The workspace consists of
`alliumpy-core` and the thin `alliumpy` bindings. Run `just py-develop` to build the
extension into pixi's environment, then `just py-test` for its Python tests.
The Justfile sets `PYO3_PYTHON` to the pixi interpreter for every Cargo invocation;
set it to that same absolute path when invoking Cargo directly. `CONDA_PREFIX` is set
by `py-develop` so maturin can install into that environment.

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

It installs a moved `pixi.lock` exactly as committed and fetches what `Cargo.lock` and
`fuzz/Cargo.lock` name.
After `tools.txt` or `tools-source.txt` has moved, run `just install-tools` as well; it
skips a version that is already there.

## Related pages

- [Commands](../reference/commands.md)
- [Test and debug](test-and-debug.md)
- [Troubleshooting](../operations/troubleshooting.md)
- [Configuration](../reference/configuration.md)
