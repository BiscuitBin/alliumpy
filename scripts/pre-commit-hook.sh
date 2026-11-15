#!/bin/sh
# The pre-commit hook `just install-hooks` copies into .git/hooks. It names no Nix store
# path and no worktree, so a moved flake.lock or a deleted worktree never leaves it
# dangling: it runs prek in the dev shell of whichever checkout the commit is made in,
# entering that shell when the commit comes from outside it (a bare terminal, an editor,
# a GUI client).
set -eu

root=$(git rev-parse --show-toplevel)
cd "$root"

# .git/hooks is shared by every branch and worktree, so this shim also runs for a
# checkout of a commit from before the flake (T19). That checkout has no dev shell to
# enter, and a dev shell's prek would run its old configuration with the wrong tools:
# run the prek of its own pixi environment if it has one, or say what to do.
if [ ! -f "$root/flake.nix" ]; then
    [ -x "$root/.pixi/envs/default/bin/prek" ] && exec "$root/.pixi/envs/default/bin/prek" run --hook-stage pre-commit
    printf '%s\n' "pre-commit: $root has no flake.nix, so it predates the dev shell," \
        'and has no pixi environment of its own to run its hooks with. Run its checks' \
        'by hand and commit with --no-verify, or run just initialize there first.' >&2
    exit 1
fi

# Inside a dev shell already, run its prek. The test comes after the one above, so a
# pre-flake checkout never gets this flake's prek run over its old configuration.
if [ -n "${ALLIUMPY_DEV_SHELL:-}" ]; then
    exec prek run --hook-stage pre-commit
fi

# A GUI client may start the hook with a PATH that lacks Nix; these are the two
# places the installers put it.
command -v nix >/dev/null 2>&1 || PATH="/nix/var/nix/profiles/default/bin:${HOME:-/var/empty}/.nix-profile/bin:$PATH"
exec nix develop --no-update-lock-file "$root" --command prek run --hook-stage pre-commit
