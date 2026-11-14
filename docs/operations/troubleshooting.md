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
Here the usual paths are a build directory that escaped the ignore rules — `target/`
or `dist/` — or a rewritten `Cargo.lock` or `flake.lock`, which means a recipe resolved
dependencies instead of reading the lockfile.

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

## `check-toolchain: cargo is <version>, not the pinned <version>`

`just check-toolchain`, the first gate, asked the `cargo` on `PATH` for its release and
got one other than the channel `rust-toolchain.toml` pins; the line ends with that
cargo's path. The dev shell builds its compiler from that file, so another release
means something put a cargo from Homebrew, rustup or a distribution ahead of the shell's
on `PATH`, or the shell is stale after the pin moved. Remove that directory from `PATH`
inside the shell, or leave the shell and enter it again, until `command -v cargo` prints
a path under `/nix/store`.

The same gate says `rustc is <version>` when cargo is right and the compiler it would
run is not, and `<component> is '<version line>', not the pinned compiler's` when
rustfmt or clippy on `PATH` belongs to another toolchain.

## `check-toolchain: cargo (<path>) cannot run the pinned <version>`

The same gate, one step earlier: the `cargo` on `PATH` cannot run at all, or there is
none. The dev shell always puts one there, so something ahead of it on `PATH` is broken,
or the shell is stale: remove that directory from `PATH`, or leave the shell and enter
it again as [Develop locally](../how-to/develop-locally.md) describes.

## `check-toolchain: cargo resolves to <path>, outside the Nix store`

The release was right but the compiler is not the dev shell's: a cargo or rustc of the
same version from rustup or a distribution sits ahead of the shell's on `PATH`. Remove
it from `PATH`, or enter the dev shell again.

## A recipe cannot find a tool, `prek` or a `bg-*` script

Every tool comes from the dev shell. Outside it the Justfile refuses to load at all,
naming `ALLIUMPY_PYTHON`, so a tool missing from a recipe that did run means the shell is
stale. Leave it and enter it again, with `nix develop` or by letting direnv do it.

## `cargo` reports that `Cargo.lock` needs to be updated but `--locked` was passed

Every cargo recipe that builds passes `--locked` or runs after `lock-check`, so a
manifest edit that the lockfile does not reflect fails every build until the lockfile
is solved again. Run `just lock`, read the diff, and commit `Cargo.lock` with the
manifest. A new dependency is a decision before it is an edit:
[Decision 0004](../decisions/0004-dependency-policy.md) says what one has to
justify.

## `just lock-check` fails on `flake.lock`

`nix flake metadata --offline --no-update-lock-file` found an input `flake.nix` names
that `flake.lock` lacks or has moved. Run `just lock`, read the diff, and commit the
lockfile with `flake.nix`.

## `just metrics` reports the wrong rustqual

The flake builds rustqual and the dev shell exports the version it built in
`ALLIUMPY_RUSTQUAL_VERSION`. `metrics: rustqual missing on PATH, flake.nix pins 1.8.3`
means the shell's rustqual is not on `PATH`, and a version in place of `missing` means
another rustqual is ahead of it. `the dev shell has rustqual <version>, flake.nix states
<version>` means the shell was entered before `rustqualVersion` moved. Either way, leave
the shell and enter it again. The gate refuses any other rustqual because its version
decides what the gate reports.

## A hook still runs an old checker after `flake.lock` moved

No hook has a `rev`: each checker is the dev shell's own, so a moved `flake.lock` takes
effect on the next shell entry. Leave the shell and enter it again.

## A commit fails: commit from inside the Nix dev shell

The first hook, `in-dev-shell`, refuses a commit made from a terminal, editor or tool
that never entered the shell, because every other hook calls the shell's tools by name.
Commit from inside the dev shell, or let direnv enter it for this directory.

## A commit fails naming a missing `prek` or configuration file

The hook shim in `.git/hooks` came from an earlier install and names a `prek` that no
longer exists, or a configuration file the repository no longer has. Run
`just install-hooks` from the primary checkout, inside the dev shell; it overwrites the
shim with one that reads `.pre-commit-config.yaml`.

## pyo3 finds the wrong Python

A direct Cargo call without `PYO3_PYTHON` can select a system Python older than the ABI
floor. Use the Justfile, which sets it to the dev shell's own interpreter, or export
that same path, `$ALLIUMPY_PYTHON` in the shell, for direct calls. Rebuild after
correcting it.

## maturin develop cannot find an environment

Use `just py-develop`. It creates the virtual environment `target/py-develop/` on the
dev shell's interpreter if it is missing, hands it to maturin through `VIRTUAL_ENV`
for that invocation with `CONDA_PREFIX` unset, and finds the dev shell's uv on PATH.

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
