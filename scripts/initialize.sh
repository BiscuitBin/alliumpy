#!/bin/sh
set -eu

project_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
cd "$project_root"

git rev-parse --is-inside-work-tree >/dev/null

# The dev shell provides every tool below, the compiler included; entering it the first
# time is what downloads them (decision 0018). The Justfile refuses to run outside it
# before this script starts, so this line only covers `sh scripts/initialize.sh`.
if [ -z "${ALLIUMPY_DEV_SHELL:-}" ]; then
    printf '%s\n' 'not in the dev shell: run nix develop --command just initialize' >&2
    exit 2
fi

# The shell is the one the committed flake produces, and its cargo is the pinned one,
# before anything is built with it.
just check-toolchain

# `Cargo.lock` is committed and every gate passes `--locked`; this line exists
# for a clone whose lockfile was deleted by hand.
test -f Cargo.lock || cargo generate-lockfile

# The cargo cache, and the shell recorded as a GC root under .nix/: the last line of
# the first-run path that reaches the network.
just sync

# Hooks are installed only from the primary checkout. Every worktree of this
# repository shares one .git/hooks directory, so one installation serves them all, and
# one made from a secondary worktree would be overwritten by the next. The comparison is
# the test git itself uses: in a secondary worktree the common directory and the git
# directory differ.
if [ "$(git rev-parse --git-common-dir)" = "$(git rev-parse --git-dir)" ]; then
    just install-hooks
else
    printf '%s\n' 'Secondary worktree: skipping install-hooks.' >&2
    printf '%s\n' 'Run just install-hooks once from the primary checkout.' >&2
fi

printf '\n%s\n' 'Ready. Next: just check.'
printf '%s\n' 'Nothing has been formatted, staged, committed, tagged, or pushed.'
