#!/bin/sh
set -eu

project_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
cd "$project_root"

git rev-parse --is-inside-work-tree >/dev/null

# The flake's dev shell holds the compiler and every tool (decision 0018), and
# entering it was the step that downloaded them. Outside it there is nothing to
# initialize with, so this refuses and names the way in.
if [ -z "${ALLIUMPY_PYTHON:-}" ]; then
    printf '%s\n' 'initialize: run this inside the dev shell: nix develop --command just initialize' >&2
    printf '%s\n' '(or run direnv allow once, and direnv enters the shell for you)' >&2
    exit 2
fi

# This refuses a compiler other than the one `rust-toolchain.toml` pins, or one
# without its components, before anything is built with it.
just check-toolchain

# `Cargo.lock` is committed and every gate passes `--locked`; this line exists
# for a clone whose lockfile was deleted by hand. `just sync` fetches the crates
# the gates later build offline.
test -f Cargo.lock || cargo generate-lockfile
just sync

# Hooks are installed only from the primary checkout. Every worktree of this
# repository shares one .git/hooks directory, and `prek install` writes a shim
# naming an absolute path to the prek that ran it, so a hook installed from a
# secondary worktree is that worktree's for commits made anywhere. The
# comparison is the test git itself uses: in a secondary worktree the common
# directory and the git directory differ.
if [ "$(git rev-parse --git-common-dir)" = "$(git rev-parse --git-dir)" ]; then
    just install-hooks
else
    printf '%s\n' 'Secondary worktree: skipping install-hooks.' >&2
    printf '%s\n' 'Run just install-hooks once from the primary checkout.' >&2
fi

printf '\n%s\n' 'Ready. Next: just check.'
printf '%s\n' 'Nothing has been formatted, staged, committed, tagged, or pushed.'
