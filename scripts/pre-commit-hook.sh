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

# .git/hooks is shared by every branch and worktree, so this shim also runs for a
# checkout of a commit from before the flake (T19). That checkout has no dev shell to
# enter: run its prek from PATH if there is one, or say what to do.
if [ ! -f "$root/flake.nix" ]; then
    command -v prek >/dev/null 2>&1 && exec prek run --hook-stage pre-commit
    printf '%s\n' "pre-commit: $root has no flake.nix, so it predates the dev shell," \
        'and no prek is on PATH to run its hooks. Commit from that checkout'"'"'s own' \
        'environment, or with --no-verify after running its checks by hand.' >&2
    exit 1
fi

# A GUI client may start the hook with a PATH that lacks Nix; these are the two
# places the installers put it.
command -v nix >/dev/null 2>&1 || PATH="/nix/var/nix/profiles/default/bin:${HOME:-/var/empty}/.nix-profile/bin:$PATH"
exec nix develop --no-update-lock-file "$root" --command prek run --hook-stage pre-commit
