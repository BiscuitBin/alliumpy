---
title: "Troubleshooting"
kind: "operations"
audience: ["contributor", "maintainer", "operator", "agent"]
canonical_for: ["troubleshooting"]
requires: []
---

# Troubleshooting

Symptoms as headings, causes and fixes as bodies.

## `just check` reports that a recipe changed the worktree

The recipe is the defect, not your change. Checks are read-only; anything that writes
belongs in `.pre-commit-fix.yaml` and runs from `just fix`. The report names which paths
moved. Move the offending hook, or add the generated path to the ignore rules.
Here the usual paths are a build or tool directory that escaped the ignore rules —
`target/`, `.tools/` or `.nix/` — or a rewritten `Cargo.lock` or `flake.lock`, which
means a recipe resolved dependencies instead of reading the lockfile.

## `docs validation: frontmatter <field> disagrees with the manifest`

Almost always list order. The comparison between `docs/manifest.yml` and a page's
frontmatter is order-sensitive, so `[maintainer, contributor]` fails against
`["contributor", "maintainer"]`. Copy the order from the manifest.

If the field is `title`, check for a stray difference in punctuation — the level-one
heading must match it byte for byte as well.

## `docs validation: not reachable from docs/README.md`

The page exists and is registered, but nothing links to it. Add it to
[the documentation map](../README.md), or to a page that is already reachable.

## `agent validation: unexpected managed file`

Something appeared under `.agents/`, `.claude/` or `.codex/` that is neither a declared
skill nor `.claude/settings.json`. If it is local tool state, add it to `.gitignore` —
the inventory reads Git, so an ignored file is invisible to it. If it is real content, it
belongs in `.agents/skills/` with bridges, or somewhere else entirely.

## `agent validation: must stay a thin pointer to the canonical skill`

A bridge under `.claude/` or `.codex/` has grown content, or its frontmatter has drifted
from the canonical skill. Regenerate it: the canonical frontmatter verbatim, one blank
line, then the fixed pointer sentence and nothing else. The body is compared against a
template rather than measured, so a clause of your own fails however short it is —
[Agent contract](../reference/agent-contract.md#what-a-bridge-must-be) carries the text.

## Coverage fails but everything is tested

Distinguish two cases. If a real path is untested, add the test. If the uncovered branch
cannot be reached by any input — a bounds check after a modulo, a fallback after an
exhaustive assignment — delete the branch. Do not lower the threshold.

On a crate this small the denominator is small too, so one untested branch in
the conversion is enough to breach the floor on its own. Test it or delete it; the number
stays where it is.

## `error: not in the dev shell`

Every recipe refuses to run outside the dev shell `flake.nix` defines, because outside it
a recipe would run whatever tools the machine has. Enter it with `nix develop`, or run
one recipe from any shell with `nix develop --command just <recipe>`. With direnv,
`direnv allow` once makes the shell follow `cd` into the checkout.
[Develop locally](../how-to/develop-locally.md) describes both.

## `check-toolchain: <tool> resolves to <path>, not the flake's toolchain`

`just check-toolchain`, the first gate, found a `cargo`, `rustc`, `rustfmt` or
`cargo-clippy` on `PATH` from outside the flake's toolchain: usually a rustup proxy in
`~/.cargo/bin` or a Homebrew cargo put ahead of the shell's `PATH` after it was entered,
by a shell startup file or by hand. Such a cargo ignores the pin and builds with whatever
release it is. Remove the directory from the front of `PATH`, or leave and enter the
shell again, until `command -v cargo` prints a path under `$ALLIUMPY_RUST_TOOLCHAIN`.

## `check-toolchain: <tool> resolves to <path>, not the dev shell`

The same gate, for every other tool a gate calls: one resolved outside `/nix/store`, such
as a uv in `~/.local/bin` or a just from a package manager, ahead of the shell's own.
The fix is the same: nothing from outside the store may come before the shell on `PATH`.

## `check-toolchain: the dev shell is stale`

`flake.nix`, `flake.lock`, `rust-toolchain.toml` or a file under `nix/` changed after
this shell was entered: a pull, a `just lock` or an edit. Leave the shell and run
`nix develop` again; a direnv shell reloads on its own. A file the shell lists that is
missing fails the same way.

## The first `nix develop` downloads for minutes

Expected once per machine and once after each `flake.lock` move: Nix substitutes the
toolchain and tools from cache.nixos.org and builds the two packages nixpkgs lacks.
It needs the network, as `just initialize` does. Re-entering an unchanged shell is
offline, and `just sync` records a GC root at `.nix/dev-shell`, so a store garbage
collection keeps it.

## `nix develop` fails on a TLS certificate

Behind a TLS-intercepting proxy Nix must trust the proxy's CA. Point `ssl-cert-file` in
the Nix configuration, or `NIX_SSL_CERT_FILE`, at a bundle that contains it.
`nix develop` keeps the caller's `SSL_CERT_FILE` and `NIX_SSL_CERT_FILE`, so the network
recipes inside the shell see the same bundle.

## `Path 'nix/<file>.nix' ... is not tracked by Git`

A flake sees only the files Git tracks. A new file under `nix/`, or a new file
`flake.nix` names, must be added (`git add`) before the flake can evaluate it; nothing
needs to be committed.

## `just lock-check` fails: `requires lock file changes but they're not allowed`

`flake.lock` disagrees with `flake.nix`: an input was added, removed or its URL edited
without relocking. Run `just lock`, read the `flake.lock` diff, and commit it with the
`flake.nix` change. Then enter the shell again.

## `cargo` reports that `Cargo.lock` needs to be updated but `--locked` was passed

Every cargo recipe that builds passes `--locked` or runs after `lock-check`, so a
manifest edit that the lockfile does not reflect fails every build until the lockfile
is solved again. Run `just lock`, read the diff, and commit `Cargo.lock` with the
manifest. A new dependency is a decision before it is an edit:
[Decision 0004](../decisions/0004-dependency-policy.md) says what one has to
justify.

## A commit fails in the hook with `nix: not found`, or is slow

The installed hook is `scripts/pre-commit-hook.sh`. From inside the dev shell it runs
prek directly. From outside, as from an editor or a GUI client, it enters the shell with
`nix develop` first, which costs a few seconds, and it looks for `nix` on `PATH`, then in
`/nix/var/nix/profiles/default/bin` and `~/.nix-profile/bin`. A Nix installed anywhere
else needs that directory on the client's `PATH`. A hook that predates this shim names an
old path: run `just install-hooks` from the primary checkout.

## After a store garbage collection, a reference or a build fails to start

`nix-collect-garbage` removes store paths nothing roots. The dev shell itself is rooted
once `just sync` has run, but two things built from it are not: the parity reference in
`.tools/parity/`, and the build scripts and proc macros under `target/`, which link
against store libraries. A reference that no longer starts fails `version-check`: run
`just install-parity-reference` again. A build script that no longer starts needs
`cargo clean`.

## pyo3 finds the wrong Python

The dev shell exports `PYO3_PYTHON` as its own interpreter, so every Cargo invocation
inside it builds the bindings against that Python. A direct Cargo call from outside the
shell can select a system Python older than the ABI floor, and is outside the pins anyway:
run it inside the shell, or through `nix develop --command`. Rebuild after correcting it.

## maturin develop cannot find an environment

Use `just py-develop`. The shell's Python is read-only, so the recipe recreates the venv
`target/py-env` on it, then runs maturin with `VIRTUAL_ENV` naming that venv. A bare
`maturin develop` has no venv to install into.

## Python still sees an old attribute set

A stale native `.so` beside `__init__.py` means source edits have not been built into
Python. Run `just py-develop`, then `just py-test` and `just py-stubtest`. Editing the
stub alone cannot change runtime behaviour.

## wheel-smoke reports two wheels in dist

`just wheel-smoke` calls wheel, which empties dist before building. Check whether a
concurrent build or manual copy added an artefact after that cleanup; stop that writer
and rerun. Do not weaken the exactly-one-wheel guard or choose an arbitrary glob match.

## Related pages

- [Test and debug](../how-to/test-and-debug.md)
- [Quality gates](../reference/quality-gates.md)
- [Maintenance](maintenance.md)
