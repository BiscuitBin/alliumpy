#!/bin/sh
set -eu

project_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
cd "$project_root"

git rev-parse --is-inside-work-tree >/dev/null

# The environment: every tool binary, Python, prek, the `bg-*` scripts and the
# package itself, editable with its test extras. `--locked` refuses a lockfile
# that disagrees with `pyproject.toml`, so a stale lock is fixed by `just lock`
# and committed, never rewritten silently by a first run.
pixi install --locked
just sync

# Hooks are installed only from the primary checkout. Every worktree of this
# repository shares one .git/hooks directory, and `prek install` writes a shim
# naming an absolute path into whichever worktree ran it, so a hook installed
# from a secondary worktree runs that worktree's prek for commits made
# anywhere, and keeps doing so after the worktree is deleted. The comparison is
# the test git itself uses: in a secondary worktree the common directory and
# the git directory differ. The recipe also provisions every hook environment,
# so this is the last line of the first-run path that reaches the network.
if [ "$(git rev-parse --git-common-dir)" = "$(git rev-parse --git-dir)" ]; then
    just install-hooks
else
    printf '%s\n' 'Secondary worktree: skipping install-hooks.' >&2
    printf '%s\n' 'Run just install-hooks once from the primary checkout.' >&2
fi

printf '\n%s\n' 'Ready. Next: just check. Tier 1 rendering also needs: just install-browser.'
printf '%s\n' 'Nothing has been formatted, staged, committed, tagged, or pushed.'
