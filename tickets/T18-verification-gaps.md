---
id: T18
title: "Verification gaps: the checks the wave-0 and wave-1 hand-backs did not run"
status: done
depends_on: [T11]
parallel_with: [T12, T13, T14, T15, T17]
branch: ticket/t18-verification-gaps
estimated_size: M
---

# T18: Verification gaps: the checks the wave-0 and wave-1 hand-backs did not run

## Context

T11 read every wave-0 and wave-1 hand-back (T00, T01, T02, T03, T05, T07 and S01) and
listed the checks they did not run in its second table, "Checks the hand-backs did not
run" (T11's hand-back notes). Rows that T11 closed, or that an existing ticket owns, are
not here. Each item below is a row that no existing ticket owns: an enforcement gap in a
frozen file, a recipe nobody exercised, or a `CONVENTIONS.md` §12 claim that T11
recorded as `partial` because one half was never shown. None is known to be broken;
each is unproven. A green `just check` or CI run closes an item only if it runs the
thing the item names (`CONVENTIONS.md` §12, §14).

This ticket is off the critical path: no wave-2 ticket waits for it, and it waits only
for T11. Wave-2 rules apply (`CONVENTIONS.md` §11): the frozen list has lifted, every
shared file is edited on its own lines, and this ticket merges rebased on whatever
wave-2 ticket merged before it.

## Goal

Every item below is closed with the evidence its row names, or is recorded as a
maintainer ruling with its reason. No item is closed by inference from an unrelated
green gate.

## Non-goals

- Anything T12 to T17 owns: the sdist assertions and the release matrix (T14), the
  vendored CLI and parity (T13), `SECURITY.md` (T12), and claims 2, 4, 5, 7 and 18 and
  T13's and T14's parts of claims 1, 12 and 19 (T17).
- Re-litigating T01's design points beyond what item 10 asks: a point the maintainer
  rules out stays out.

## Files touched

A path is edited only on the route its item takes; a route that a maintainer ruling
closes edits nothing. A route that needs a path not listed here stops and is handed back
(`CONVENTIONS.md` §14, "Scope guard").

| Path | Class | Content |
| --- | --- | --- |
| `scripts/version_check.py` | shared, own lines | item 1: each member crate's inherited or explicit version |
| `Justfile` | shared, own lines | item 2: the `check-toolchain` recipe only |
| `docs/reference/commands.md` | shared, own lines | item 2: the `check-toolchain` row |
| `docs/reference/quality-gates.md` | shared, own lines | item 2: the `check-toolchain` row |
| `.github/workflows/ci.yml` | shared, own lines | item 10: only the points the maintainer accepts |
| `.github/workflows/audit.yml` | shared, own lines | item 10: only the points the maintainer accepts |
| `.github/actions/setup/action.yml` | shared, own lines | item 10: only the points the maintainer accepts |
| `crates/alliumpy/pyproject.toml` | shared, own lines | item 11: a `[tool.maturin]` exclusion, only if bytecode ships and the maintainer wants it out |
| `tickets/CONVENTIONS.md` | shared, own lines | item 12: one sentence in §14, only after the maintainer approves its text |
| `tickets/README.md` | shared, own lines | this ticket's status cell; item 12's sentence in "Ticket format" instead of §14, if the maintainer approves that route |
| `tickets/T18-verification-gaps.md` | ticket | `status:` and hand-back notes |

## Steps

Each item names its source (ticket and lines, as T11 cited them), what is unproven, and
the evidence that closes it. Run `just check` on the untouched worktree first and quote
its last line.

1. **Member-crate versions (T05:434-438; T07:518-521).** `scripts/version_check.py`
   reads the workspace version only, so invariant 9 is not proved for each crate
   manifest. Closed by a checker that reads each member's inherited or explicit
   version, with a scratch-copy control: an explicit wrong `version` in one member
   makes `just version-check` exit non-zero, quoted, then restored.
2. **`check-toolchain` against the pin (T07:518-521).** The recipe checks that `cargo`
   is rustup's proxy, not that the selected toolchain equals `rust-toolchain.toml`.
   Closed by a recipe change plus a control: `RUSTUP_TOOLCHAIN=<another installed
   version> just check-toolchain` exits non-zero, quoted.
3. **The primary checkout's hook shim (T00, not stated).** No hand-back shows the
   installed hook refusing a commit. Closed by a commit attempt with a deliberate
   violation in the primary checkout (hooks are never installed from a secondary
   worktree, `AGENTS.md`), quoting the refusal and its exit, then the clean state.
4. **`snapshots-review` and `snapshots-accept` (T00, not stated).** Never run: there
   was no snapshot to act on, and the workspace has no `insta` dependency (T02:345-347:
   the first ticket that takes a real snapshot adds it). A run with nothing pending
   proves nothing: `snapshots-accept` exits 0 with nothing to accept, and its
   `--unreferenced delete` removes an orphan `.snap` (`Justfile`). Closed in a scratch
   copy that adds `insta` as a core dev-dependency and one test whose assertion
   produces a pending `.snap.new`, all restored afterwards and never committed
   (invariant 8; resolving `insta` into the scratch `Cargo.lock` runs `just lock`, a
   network recipe the maintainer authorises first). Each recipe gets its own fresh
   pending snapshot. For `snapshots-accept`: exit 0, the `.snap.new` gone and the
   accepted `.snap` holding the expected content, quoted. For `snapshots-review`, which
   needs a terminal: its prompt naming that snapshot, the accept chosen there and its
   exit, quoted. Then `git status --short` empty. Or by a maintainer ruling that the
   first ticket to take a real snapshot runs both and quotes the same evidence; no
   ticket in this directory does yet.
5. **Claim 8, `PYO3_BUILD_EXTENSION_MODULE` (T00, T02).** No hand-back shows maturin
   setting it during `py-develop`. Closed by `py-develop` output at a verbosity that
   prints the cargo invocation and shows the variable set, quoted with its commit.
6. **Claim 9, the installer (T00:507, T00:538; T11 step 3).** T11 showed `maturin
   develop` finding the pixi environment through `CONDA_PREFIX` from an unactivated
   shell, but no output names the installer or shows it is `uv 0.13.5`. Closed by
   output that names the installer and its version during `py-develop`.
7. **Initialization with no global cache (T00:620).** Every `just initialize` so far
   reused the cargo registry, rustup, pixi or uv caches. Closed by a run with each of
   those cache locations pointed at an empty directory, quoting `just initialize` and
   then `just check`, or by a maintainer ruling that CI's cold runners are the proof
   (cite the run).
8. **Claim 10, the full run (T01:681-685; `CONVENTIONS.md` §12).** T01's full CI run hit
   `main`'s pixi cache, so B was not fetched there; T11's dispatch would hit it too.
   Closed by a full `ci.yml` run on `main` whose setup-pixi cache misses and fetches B
   with no credential, quoting the cache-miss line and the fetch.
9. **Claim 11, the Pages half and the private skip (T01:416-418, 505-507, 759-760).**
   The Pages read gave 404, not a plan message, and the conditional deploy never ran on
   a private repository. The repository has been public since 2026-10-24, so the skip
   cannot be run as built. The two halves close separately; closing one leaves the
   other open.
   - Pages availability on the free organisation plan: closed by a read on a private
     repository whose answer shows availability either way (a plan message or a Pages
     object, not a bare 404), quoted with its exit, or by a maintainer ruling with
     its date that it is moot while the repository is public. A skipped deploy does
     not close it.
   - The private skip: closed by a `pages.yml` run on `refs/heads/main` of a private
     repository, quoting the event's `repository.private` as `true`, the build job
     green and the deploy job `skipped`. A run on another branch does not count: the
     `if:` (`.github/workflows/pages.yml`) also requires `main`, so it would skip for
     the wrong reason. Or by a maintainer ruling with its date that it is moot while
     the repository is public.
10. **T01's seven review points (T01:782-800).** The full setup in `audit`;
    `check-toolchain` only in `rust`; the setup action's "no step reaches the network"
    comment against `audit`'s RustSec fetch; `py-develop` twice in `python`;
    `snapshots-check` and nextest run twice; seven rust-cache keys; no
    `overwrite: true` on the uploads (unverified). Each point closes by a maintainer
    ruling with its reason, or by a change and the run that executes it. `audit.yml` is
    its own workflow and is not in `ci.yml`'s `check` `needs`, so the two `audit`
    points (the full setup, the RustSec fetch) close only by a green `audit.yml` run
    after the change, quoted. The `overwrite: true` point closes only by rerunning
    an uploading job in the same `ci.yml` run after its first attempt uploaded the
    artefact, quoting the attempt numbers and the rerun's upload step; a fresh dispatch
    never reaches the conflict. The other four close by a green dispatched `ci.yml` run
    after the change, quoting the job whose behaviour changed.
11. **Python bytecode in the wheel (T00:558-560).** Closed by a wheel listing
    (`python -m zipfile -l`) that shows whether `__pycache__` or `.pyc` entries ship,
    and a maintainer ruling or a manifest change if they do.
12. **The verification-template rule (T05:439-443).** T05's B2: a filter can return its
    expected exit after the producer failed. Closed by a sentence in `CONVENTIONS.md`
    §14 or in `tickets/README.md`, "Ticket format", that splits producers from filters,
    checks each exit and keeps a nonempty positive control. That is a change to the
    rules every ticket obeys: the maintainer approves the sentence's text and its place
    before it is written, and this ticket does not grant that approval itself. Quote
    the approval with its date, then the commit that adds the sentence.
13. `just check`, the final adversarial review, `just check` again if fixes landed, then
    commit. **Authorisation required: push and open a pull request.** A dispatched or
    rerun CI run that items 8 and 10 name runs after the merge, each separately
    authorised, and its evidence follows in one evidence commit, reviewed as below
    before its own push.

    **Adversarial review** (`CONVENTIONS.md` §14): the lane's diff and every item's
    closing evidence or ruling, before the push. Ask: which item is closed by a gate or
    run that does not execute the thing it names; which item 9 half is closed by the
    other half's evidence, or by a skip on a branch other than `main`; whether item 1's
    checker and item 2's recipe fail on their scratch controls and pass once restored;
    whether item 4's accept ran against a referenced pending snapshot and not an empty
    set; whether item 10's artefact point rests on a same-run rerun and its `audit`
    points on an `audit.yml` run; whether each ruling records its reason and date;
    whether every scratch edit, including item 4's `insta` dependency, was restored.

## Acceptance criteria

- Each of the twelve items is closed with the evidence its step names, quoted with its
  commit, or carries a maintainer ruling with its reason.
- No item is closed by citing a gate that does not run it.
- `just check` ends with `All checks passed and the worktree is unchanged.` and
  `git status --short` is empty.

## Verification

```sh
just check
just version-check; echo "exit $?"     # item 1, before and after the scratch control
just check-toolchain; echo "exit $?"   # item 2, before and after the scratch control
git status --short; echo "exit $?"
```

The other items' commands depend on the route each takes; quote each with its exit.

## Hand-back notes

### Baseline

At `c09f6fa` (`main`, untouched worktree), `just check` ended `exit 0` with:

```text
All checks passed and the worktree is unchanged.
```

### Maintainer answers (2026-10-29)

Before the work started the maintainer ruled: run items 3, 4 and 7; item 9's two
halves are moot while the repository is public; rule out all seven item 10 points; add
item 12's sentence to `CONVENTIONS.md` §14 with the wording quoted under item 12.
During the work the maintainer also authorised `just sync` in item 4's scratch clone and
approved item 11's `[tool.maturin]` exclusion (both 2026-10-29).

### Item 1: member-crate versions

`f476bd5`, then `e6ed03d` and `cc8e96b` after review findings B1 and R6:
`scripts/version_check.py` adds each workspace member's version, as
`cargo metadata --no-deps --locked --offline` resolves it (inherited or explicit), as an
entry `"crate <name> version"`, and fails when cargo reports no member. Cargo decides membership, so a path-dependency member counts and an excluded
directory does not. The message counts the entries instead of saying "five".
`just py-lint` and `just py-typecheck` exited 0.

Controls at `cc8e96b`, in an `rsync` copy of the worktree with `target`, `.pixi` and
`.tools` symlinked. `crates/alliumpy-core/Cargo.toml` set to `version = "9.9.9"`:

```text
$ just version-check; echo "exit $?"
python -I scripts/version_check.py
version-check: workspace version='3.6.1' differs from crate alliumpy-core version='9.9.9'
error: recipe `version-check` failed on line 308 with exit code 1
exit 1
```

B1's scenario, `members = ["crates/alliumpy"]` with `alliumpy-core` at `version = "3.6.2"`
(core still a member through the path dependency):

```text
version-check: workspace version='3.6.1' differs from crate alliumpy-core version='3.6.2'
exit 1
```

Restored (`diff -r` against the worktree exited 0), then:

```text
$ just version-check; echo "exit $?"
python -I scripts/version_check.py
version-check: all 7 versions agree: 3.6.1
exit 0
```

### Item 2: `check-toolchain` against the pin

`f476bd5`, then `e6ed03d` and `cc8e96b` after review findings B2, R2, R3 and R4: after
the proxy check, the recipe reads `channel` from `rust-toolchain.toml` with `sed` and
rustup's `Default host:` from `rustup show`, failing if either is empty, and requires
the first word of `rustup show active-toolchain` to be exactly the pin or
`<pin>-<host>`, naming both on stderr and exiting 2 otherwise. No `rustc` runs, and both
rustup calls carry `RUSTUP_AUTO_INSTALL=0`, so an uninstalled toolchain is refused
rather than downloaded. The two reference rows (`commands.md`, `quality-gates.md`) say
so. CI installs through `rust-toolchain.toml` with no `RUSTUP_TOOLCHAIN`
(`.github/actions/setup/action.yml:35-39`), so its runner matches. `just check-docs`
exited 0. At `cc8e96b`, in this worktree (1.98.1 and `1.99.1-x86_64-apple-darwin` are
installed, 1.97.0 is not):

```text
$ RUSTUP_TOOLCHAIN=1.98.1 just check-toolchain; echo "exit $?"
the active toolchain is 1.98.1-aarch64-apple-darwin, not the pinned 1.99.1
error: recipe `check-toolchain` failed on line 39 with exit code 2
exit 2
$ RUSTUP_TOOLCHAIN=1.99.1-x86_64-apple-darwin just check-toolchain; echo "exit $?"
the active toolchain is 1.99.1-x86_64-apple-darwin, not the pinned 1.99.1
error: recipe `check-toolchain` failed on line 39 with exit code 2
exit 2
$ RUSTUP_TOOLCHAIN=1.97.0 just check-toolchain; echo "exit $?"
info: the active toolchain `1.97.0-aarch64-apple-darwin` is not installed
error: override toolchain '1.97.0-aarch64-apple-darwin' is not installed: the RUSTUP_TOOLCHAIN environment variable specifies an uninstalled toolchain
error: recipe `check-toolchain` failed on line 39 with exit code 1
exit 1
$ just check-toolchain; echo "exit $?"
1.99.1-aarch64-apple-darwin (overridden by '<worktree>/rust-toolchain.toml')
exit 0
```

`rustup toolchain list` was the same before and after the 1.97.0 control.

### Item 3: the primary checkout's hook shim

In `/Users/scutting/projects/biscuitbin/alliumpy` (clean, `main` at `c09f6fa`, shim
naming that checkout's `.pixi/envs/default/bin/prek`): an untracked
`t18-hook-control.txt` holding one line with trailing whitespace was staged and
committed.

```text
$ git commit -m "T18 item 3 hook control (must be refused)"; echo "commit exit $?"
EditorConfig.............................................................Failed
- hook id: editorconfig-checker
- description: This runs editorconfig-checker to validate files against your .editorconfig
- exit code: 1

  t18-hook-control.txt:
          1: Trailing whitespace

  1 errors found
commit exit 1
$ git log --oneline -1
c09f6fa Merge pull request #24 from BiscuitBin/ticket/t11-integration
```

The hook indents its finding with a tab, shown here as spaces. After
`git restore --staged t18-hook-control.txt` and removing the file, `git status --short`
printed nothing (`exit 0`, 0 lines).

### Item 4: `snapshots-accept` and `snapshots-review`

In a `git clone` of this branch at `f476bd5` in the session scratchpad, with `.pixi` and
`.tools` symlinked: `insta = "1.48.0"` added to `alliumpy-core`'s `[dev-dependencies]`
(resolved to 1.49.0) and a test `t18_snapshot_control` asserting
`"t18 accept control"`. `just lock` exited 0 (15 packages added; `pixi lock` unchanged).
`INSTA_UPDATE=new cargo nextest run -p alliumpy-core` failed the test (exit 100) and
stored `src/snapshots/alliumpy_core__tests__t18_snapshot_control.snap.new`.

Finding: the first `just snapshots-accept` then failed before any test ran, because
cargo-insta's `cargo metadata` runs under `CARGO_NET_OFFLINE=true` and needed a crate
the lock added but nothing fetched:

```text
error: failed to load cargo metadata: `cargo metadata` exited with an error: error: failed to download `encode_unicode v1.0.0`
  attempting to make an HTTP request, but --offline was specified
error: recipe `snapshots-accept` failed on line 131 with exit code 1
```

The ticket that first adds `insta` runs `just sync` after `just lock`. Here, with the
maintainer's authorisation, `just sync`'s `cargo fetch --locked` downloaded
`encode_unicode v1.0.0`; its `pixi install --frozen` refused the symlinked environment
("the environment directory has moved") and changed nothing (`pixi install --frozen` in
this worktree afterwards: "The default environment has been installed.", exit 0). Then:

```text
$ just snapshots-accept; echo "snapshots-accept exit $?"
        PASS [   0.053s] (7/7) alliumpy-core tests::t18_snapshot_control
     Summary [   0.054s] 7 tests run: 7 passed, 0 skipped
info: no unreferenced snapshots found
insta review finished
accepted:
  crates/alliumpy-core/src/lib.rs (t18_snapshot_control.snap)
snapshots-accept exit 0
$ find crates -name '*.snap*'
crates/alliumpy-core/src/snapshots/alliumpy_core__tests__t18_snapshot_control.snap
$ cat crates/alliumpy-core/src/snapshots/alliumpy_core__tests__t18_snapshot_control.snap
---
source: crates/alliumpy-core/src/lib.rs
expression: "\"t18 accept control\""
---
t18 accept control
```

`snapshots-review`: a second test, `t18_review_control`, left a fresh
`alliumpy_core__tests__t18_review_control.snap.new`. The maintainer ran
`just snapshots-review; echo "exit $?"` in that clone at a terminal on 2026-10-30,
accepted with `a`, and pasted the end of the session (the interactive prompt itself was
not captured):

```text
insta review finished
accepted:
  crates/alliumpy-core/src/lib.rs (t18_review_control.snap)
exit 0
```

Afterwards the clone held no `.snap.new`, only the two accepted snapshots, and
`alliumpy_core__tests__t18_review_control.snap` read:

```text
---
source: crates/alliumpy-core/src/lib.rs
expression: "\"t18 review control\""
---
t18 review control
```

The scratch clone, with its `insta` dependency, test and lock change, was then deleted;
none of it reached this branch.

### Items 5 and 6: `PYO3_BUILD_EXTENSION_MODULE` and the installer

At `f476bd5`, `RUST_LOG=maturin=debug just py-develop` exited 0 (maturin 1.15.0); the
log is in `ai_tmp/t18/item5-6-py-develop.log`. With the ANSI codes stripped, line 28
(maturin's cargo command, cut at the program name) and line 22:

```text
maturin::compile: Running env -u CARGO CARGO_ENCODED_RUSTFLAGS="-C\u{1f}link-arg=-undefined\u{1f}-C\u{1f}link-arg=dynamic_lookup" PYO3_BUILD_EXTENSION_MODULE="1" ... "cargo" "rustc"
maturin::develop::install_backend: Found uv binary in PATH version=uv 0.13.5 (aarch64-apple-darwin)
```

The install step's own command is not logged; within the `install_wheel` span maturin
then runs `UV_PYTHON="<worktree>/.pixi/envs/default/bin/python" "uv" "pip" "show"
"--files" "alliumpy"`, and ends with `🛠 Installed alliumpy-3.6.1`.

### Item 7: initialisation with no global cache

A fresh `git clone` of this branch at `f476bd5` in the scratchpad, with its own `.git` and
no `.pixi` or `.tools`. `RUSTUP_HOME`, `CARGO_HOME`, `PIXI_CACHE_DIR`, `UV_CACHE_DIR` and
`PREK_HOME` pointed at new empty directories; `$CARGO_HOME/bin` held only symlinks named
`rustup`, `cargo`, `cargo-clippy`, `cargo-fmt`, `clippy-driver`, `rustc`, `rustdoc` and
`rustfmt` to `~/.cargo/bin/rustup`, first on `PATH`. The tail of `just initialize`:

```text
prek install --overwrite --hook-type=pre-commit --prepare-hooks
Installed Git hook at `.git/hooks/pre-commit`
prek prepare-hooks --config .pre-commit-fix.yaml
RUSTUP_AUTO_INSTALL=0 prek run lychee --files README.md
lychee...................................................................Passed

Ready. Next: just check.
Nothing has been formatted, staged, committed, tagged, or pushed.
initialize exit 0
```

and of `just check`:

```text
==> just check-clean
bg-project-check clean "$1"
The worktree matches the check baseline.

All checks passed and the worktree is unchanged.
check exit 0
```

`git status --short` in the clone printed 0 lines. The caches were filled from empty:
`rustup` 605M (toolchain `1.99.1-aarch64-apple-darwin`, "downloading 6 components"),
`cargo` 28M, `pixi` 384M, `prek` 966M, `uv` 856K. Initialisation's own
`check-toolchain` printed `1.99.1-aarch64-apple-darwin`. The clone's hook names the
clone's `prek`; the primary checkout's still names its own. The clone was deleted.

### Item 8: claim 10, the full run (open)

Left open (2026-10-29). The pixi cache key has been unchanged since 2026-10-24, so every
`ci.yml` run on `main` hits it. Closing it needs a separately authorised post-merge
action (deleting the pixi cache, or a `pixi.lock` change), then a `ci.yml` run on `main`
quoting the setup-pixi cache miss and B's fetch with no credential.

### Item 9: claim 11, both halves (ruling)

Maintainer ruling, 2026-10-29: both halves, Pages availability on a private repository
and the private skip, are moot while the repository is public. It has been public since
2026-10-24 (`gh repo view` reports `PUBLIC`).

### Item 10: T01's seven review points (ruling)

Maintainer ruling, 2026-10-29: all seven points are ruled out, and no workflow changes.
The reasons:

- The full setup in `audit`, and the setup action's "no step reaches the network"
  comment against `audit`'s RustSec fetch: `audit.yml` was green in 10 of its 10 most
  recent runs, each taking 31 to 42 s.
- `check-toolchain` only in `rust`, `py-develop` twice in `python`, and
  `snapshots-check` and nextest each run twice: the repeated builds and test runs cost
  minutes and nothing else.
- Seven rust-cache keys: the three that compile nothing are 3.9 MiB each, and the
  caches total about 1.5 GB of the 10 GB quota.
- No `overwrite: true` on the uploads: still unverified, and no CI run has ever had a
  second attempt that would reach the conflict.

### Item 11: Python bytecode in the wheel

At `f476bd5`, `just wheel` exited 0, and
`python -I -m zipfile -l dist/alliumpy-3.6.1-cp311-abi3-macosx_11_0_arm64.whl` exited 0.
Bytecode shipped, copied from the `__pycache__` the Python gates leave beside the
source:

```text
alliumpy/__init__.py                           1980-01-01 00:00:00          339
alliumpy/__pycache__/__init__.cpython-314.pyc  1980-01-01 00:00:00          519
```

With the maintainer's approval (2026-10-29), `9da65ce` adds
`exclude = ["**/__pycache__/**", "**/*.pyc"]` under `[tool.maturin]`. With
`crates/alliumpy/python/alliumpy/__pycache__/__init__.cpython-314.pyc` still present in
the source tree, `just wheel` exited 0 and the listing exited 0; the positive control
`grep -c 'alliumpy/__init__.py'` printed `1` (exit 0) and
`grep -cE '__pycache__|\.pyc'` printed `0` (exit 1). `just wheel-smoke` then exited 0,
ending `allium 3.6.1 (language versions: 1, 2, 3)`.

### Item 12: the verification-template rule

Maintainer approval, 2026-10-29: the sentence goes in `CONVENTIONS.md` §14, at the end of
the Breakage lens bullet, worded:

> A verification command separates the producer from any filter that reads its output,
> checks each one's exit status, and keeps a positive control that must produce
> nonempty output, so a filter cannot return its expected exit after the producer
> failed.

`f476bd5` adds it there verbatim.

### Close-out

#### Review record (`CONVENTIONS.md` §14)

Two read-only Codex reviewers (`gpt-6-astra`, `codex exec -s read-only`), one per lens,
read the ticket, `CONVENTIONS.md` and `git diff main...HEAD` plus the uncommitted
changes at `9da65ce` (`ai_tmp/review/T18-1/`). `/code-review` (medium) then read the
branch at `e6ed03d`. Deviation from §14 Phase 2, as the approved plan directed: the
executing agent triaged and applied the fixes, not separate triage subagents.
Triage:

- B1 (medium, `version_check.py`): glob membership misses a path-dependency member and
  ignores `exclude`. Valid; fixed in `e6ed03d` (`cargo metadata`), control above.
- B2 (low, `Justfile:37`): the `"$pin"-*` prefix accepts a dated or other channel
  sharing the prefix. Valid; fixed in `e6ed03d` (exact pin or `<pin>-<host>`).
- B3 and C1 (medium): `status: done` while item 8 is open. Kept: the maintainer chose
  `done` (2026-10-29), with item 8's post-merge evidence commit to follow (step 13).
- B4 and C2 (medium): item 4's review half and the scratch clone's cleanup. Closed
  under item 4.
- C3 (medium): no final `just check` on the reviewed state. Closed below.
- R1 (`/code-review`): placeholders while `done`. Closed by these notes.
- R2 (`Justfile:37`): the host came from a `rustc` that the override under test
  selects, so `<pin>-<other host>` passed. Valid; fixed in `cc8e96b` (rustup's default
  host), control above.
- R3 (`Justfile:37`): the proxy's `rustc` could auto-install a missing toolchain.
  Valid. While the review ran, its probe of a `1.99.1-x86_64-apple-darwin` override
  (it reported running `rustup show active-toolchain` and `rustc -vV`) installed that
  toolchain into `~/.rustup` at 22:26:39, a download nothing authorised; which of the
  two calls installed it was not established, and the unguarded path was not retried.
  Fixed in `cc8e96b`: no `rustc` runs, and `RUSTUP_AUTO_INSTALL=0` on both rustup calls
  makes an uninstalled toolchain a refusal (the 1.97.0 control above). That toolchain
  is still installed and is the maintainer's to remove.
- R4 (`Justfile:37`): `rustc` resolved through the pixi and `.tools` directories first.
  Removed with R2's fix.
- R5 (`pyproject.toml`): no gate asserts the wheel holds no bytecode. Valid; the
  assertion belongs in `wheel-smoke`, outside this ticket's `Justfile` scope
  (`check-toolchain` only), so it is handed back (§14, "Scope guard").
- R6 (`version_check.py`): a member named like a fixed key could overwrite it. Valid;
  fixed in `cc8e96b` (`crate <name> version`).
- R7 (`version_check.py`): unguarded `json.loads`. No change: the script still exits
  non-zero, only with a traceback.
- R8 (`Justfile:37`): one long line. No change: it matches the recipe's existing
  one-line style.
- R9 (`pyproject.toml`): `PYTHONDONTWRITEBYTECODE=1` for the Python recipes would stop
  the bytecode at its source. Handed back with R5: a `Justfile` export outside
  `check-toolchain`.

#### Final gate

At `cc8e96b`, with these notes and the status cells uncommitted, `just check` ended
`exit 0` with:

```text
All checks passed and the worktree is unchanged.
```

The notes commit that follows is re-checked the same way, and `git status --short` is
empty after it. Not pushed; no pull request opened. Item 8's evidence, after a
separately authorised post-merge action and `ci.yml` run, follows in its own evidence
commit (step 13).

### Rebase onto `origin/main` (2026-10-30)

`git fetch origin` found `main` at `eb141cb` (T15 merged). The branch was rebased onto
it; the one conflict, the two `quality-gates.md` rows, kept T18's `check-toolchain` row
and T15's `lock-check` row. The SHAs quoted above are the commits the evidence ran at;
after the rebase they are `f476bd5` → `5a01a44`, `9da65ce` → `7ddfa28`, `e6ed03d` →
`b164dd4`, `cc8e96b` → `6b8fe7e`, `b02f420` → `343f6f4` and `25a2c2e` → `18af4dd`. T15
added `exclude = ["fuzz"]` to the workspace; `cargo metadata` leaves the fuzz crate out,
as review finding B1 intended. Requoted at `18af4dd`:

```text
$ just check            → exit 0, "All checks passed and the worktree is unchanged."
$ just version-check    → "version-check: all 7 versions agree: 3.6.1", exit 0
$ just check-toolchain  → "1.99.1-aarch64-apple-darwin (overridden by ...)", exit 0
$ RUSTUP_TOOLCHAIN=1.98.1 just check-toolchain
the active toolchain is 1.98.1-aarch64-apple-darwin, not the pinned 1.99.1   (exit 2)
$ # scratch copy, alliumpy-core version = "9.9.9"; just version-check
version-check: workspace version='3.6.1' differs from crate alliumpy-core version='9.9.9'   (exit 1)
$ git status --short    → 0 lines
```

## Open points

- Items 3, 4, 7, 9, 10 and 12 may close by a maintainer ruling instead of a run; the
  maintainer says which before the work starts.
- Item 12 changes the rules every ticket obeys. Whether the sentence goes in
  `CONVENTIONS.md` §14 or in `tickets/README.md`, "Ticket format", and its wording, are
  the maintainer's decision; T11 did not make it, and no line is written before it.
