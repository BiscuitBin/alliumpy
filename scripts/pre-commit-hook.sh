#!/bin/sh
# The pre-commit hook `just install-hooks` copies into .git/hooks. It names no Nix store
# path and no worktree, so a moved flake.lock or a deleted worktree never leaves it
# dangling: it runs prek in the dev shell of whichever checkout the commit is made in,
# entering that shell when the commit comes from outside it (a bare terminal, an editor,
# a GUI client).
set -eu

root=$(git rev-parse --show-toplevel)
cd "$root"

if [ -n "${ALLIUMPY_DEV_SHELL:-}" ]; then
    exec prek run --hook-stage pre-commit
fi

# A GUI client may start the hook with a PATH that lacks Nix; these are the two
# places the installers put it.
command -v nix >/dev/null 2>&1 || PATH="/nix/var/nix/profiles/default/bin:${HOME:-/var/empty}/.nix-profile/bin:$PATH"
exec nix develop --no-update-lock-file "$root" --command prek run --hook-stage pre-commit
