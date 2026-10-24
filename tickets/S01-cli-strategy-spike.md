---
id: S01
title: "Spike: how the `allium` command gets into the wheel, with a parity harness"
status: open
depends_on: [T00]
parallel_with: [T01, T02, T03, T05, T07]
branch: ticket/s01-cli-strategy-spike
estimated_size: L
---

# S01: Spike: how the `allium` command gets into the wheel, with a parity harness

## Context

The wheel ships a console script `allium` whose behaviour is upstream's (`CONVENTIONS.md`
§7 invariant 1). Upstream exposes that behaviour only as a binary crate: `allium-cli` on
crates.io is `[[bin]] name = "allium"`, and the pieces `allium check` needs beyond the
parser (file discovery, the cross-module context builder, the line/col JSON conversion,
the per-file JSON envelope, the exit-code policy, `plan` and `model`) live in
`crates/allium/src/` with no library target (`CONVENTIONS.md` §1 fact 5; step 2 records
their names at `v3.6.1`). pyo3 bindings over `allium-parser` alone cannot reproduce
`allium check` on a multi-file specification. Three routes exist
and the maintainer asked for a spike to choose between them (`CONVENTIONS.md` §1
decision 3):

- **(a) Vendor.** Copy U `crates/allium/src/main.rs`, U `crates/allium/src/test_plan.rs`
  and U `crates/allium/src/domain_model.rs` at `v3.6.1` under
  `crates/alliumpy-core/src/cli/`, with the MIT header and attribution, turn `main` into
  `alliumpy_core::cli::run(args, stdout, stderr) -> i32`, and have `_cli.py` call it
  through the pyo3 module with `sys.argv`, flush both streams and exit with its code.
  Exact parity by construction at one version; a re-vendor diff on every upstream bump.
- **(b) Bundle.** Build `allium-cli@3.6.1` from crates.io per target in the release
  matrix and ship the binary as package data under
  `crates/alliumpy/python/alliumpy/_bin/`, behind an exec shim in `_cli.py` (`os.execv`
  on POSIX; `subprocess` with exit-code propagation on Windows). Zero drift; a second
  build per target, a bigger wheel, a musllinux cross-build, and no path from Python to
  the CLI's logic.
- **(c) Upstream.** A pull request to `juxt/allium-tools` adding a library target that
  exposes `run(args) -> ExitCode`, then a dependency on it. The cleanest, and blocked on a
  repository this project does not control: it is a T13 path only if the pull request is
  merged and released on crates.io by the day T13 opens.

Whatever the route, the claim "the wheel's `allium` behaves as upstream's" is proved by
a parity harness, not asserted. The harness is designed first and reviewed before any
prototype is built on it (`CONVENTIONS.md` §9 "The parity reference", §11 "Untrusted
material", §12 claims 12 and 18, §13 "CLI drift"). This spike lands nothing on `main`:
every prototype lives in `ai_tmp/`, and its output is a recommendation, a drafted
decision record and the route-specific steps T13 copies.

L's spikes are the format: L `tickets/S04-bindings-and-cli.md` (a spike that verified
facts against documentation and drafted the tickets that followed) and L
`tickets/S02-release-and-publishing.md` lines 640-700 (how a recommendation table and a
drafted ticket body end a spike). The upstream facts this spike starts from are
`CONVENTIONS.md` §1 fact 5; each is re-read from U on the day, never trusted from here.

Read first: `CONVENTIONS.md` §1 (decisions 2, 3, 4 and 7; facts 5, 9 and 11), §9 in
full, §11 ("Untrusted material", "Network", "Separately authorised actions"), §12
claims 12 and 18, §13, §14; `crates/alliumpy-core/src/lib.rs`,
`crates/alliumpy/python/alliumpy/_cli.py` and `tests/fixtures/smoke/` as T00 left them;
`Justfile` (`wheel-smoke`, `version-check`).

## Goal

A recommendation for how the `allium` command gets into the wheel, with parity evidence
for every prototype built, a ruling on the sdist, an answer to `CONVENTIONS.md` §12
claim 12, a list of behaviours T13 must test (broken pipe, flush order, SIGPIPE, exit
codes), a drafted decision record 0014 and the drafted route-specific steps for T13, all
in the hand-back notes. Nothing is committed outside this file; nothing is filed upstream.
The starting recommendation, to be confirmed or overturned by the evidence: **(a)
vendor**, because it keeps one build per target, keeps the CLI reachable from Python
later, and makes an upstream bump a reviewable diff; its cost, the re-vendor on each
bump, is paid by T17's runbook and caught by the parity corpus.

| Route | Parity | Per upstream bump | Release matrix | Wheel | Python can call the CLI logic | Blocked on |
| --- | --- | --- | --- | --- | --- | --- |
| (a) vendor | by construction at one version; proved by the harness | re-vendor three files, re-run parity | one build per target | one extension module | yes, later | nothing |
| (b) bundle | exact: it is upstream's binary | rebuild the binary | a second cargo build per target, musllinux included | extension plus a binary | no | nothing |
| (c) upstream | exact | bump the dependency | one build per target | one extension module | yes | a merge and a release upstream |

## Non-goals

- Landing any crate, module, fixture, recipe, workflow or page on `main`. T13 does that.
- Choosing the version mechanics (`CONVENTIONS.md` §1 decision 4, T14) or what Renovate
  bumps (T17). This spike only records what each route makes those tickets do.
- Filing the upstream pull request. Its text is drafted; filing is an authorisation stop
  the maintainer takes outside this spike.
- Windows. Parity is POSIX-only here (`CONVENTIONS.md` §1 fact 9); the exec shim's
  Windows half is designed, not run, and T14's rehearsal is the one Windows proof.
- A choice of pyo3 or maturin version, or any change on the ticket branch to
  `Cargo.toml`, `deny.toml` or the frozen files. The prototype worktrees under `ai_tmp/`
  may change anything (step 4 adds `serde` and `serde_json` there) because nothing in
  them lands; a
  need found for `main` is handed back.

## Files touched

| Path | Class | Change |
| --- | --- | --- |
| `tickets/S01-cli-strategy-spike.md` | ticket | the harness design and its full text, the evidence, the recommendation, the drafted record and the drafted T13 steps; `status: done` |

No other path. `ai_tmp/` holds the prototypes and is never committed.

## Steps

1. Create the worktree on `ticket/s01-cli-strategy-spike` from `origin/main` after a
   fetch, once T00 has merged (`README.md`, "How to pick up a ticket", step 1);
   `just initialize` (network, authorised); `just check` on the untouched worktree, last
   line quoted as the baseline.

2. **Re-read upstream, as data.** Into `ai_tmp/upstream/` (an empty directory, nothing
   run from inside it), with `gh api` (network, authorised; read-only):

   ```sh
   mkdir -p ai_tmp/upstream
   set -o pipefail   # bash and zsh: a failed gh api must not be hidden by base64 or the redirect
   gh api 'repos/juxt/allium-tools/git/trees/v3.6.1?recursive=1' --jq .truncated   # must print false; anything else stops the step
   gh api 'repos/juxt/allium-tools/git/trees/v3.6.1?recursive=1' --jq '.tree[] | select(.path | endswith(".allium")) | .path' > ai_tmp/upstream/allium-files.txt
   gh api 'repos/juxt/allium-tools/git/trees/v3.6.1?recursive=1' --jq '.tree[] | select(.path | startswith("crates/allium/")) | .path'
   gh api 'repos/juxt/allium-tools/contents/crates/allium/src/main.rs?ref=v3.6.1' --jq .content | base64 -d > ai_tmp/upstream/main.rs
   gh api 'repos/juxt/allium-tools/contents/crates/allium/src/test_plan.rs?ref=v3.6.1' --jq .content | base64 -d > ai_tmp/upstream/test_plan.rs
   gh api 'repos/juxt/allium-tools/contents/crates/allium/src/domain_model.rs?ref=v3.6.1' --jq .content | base64 -d > ai_tmp/upstream/domain_model.rs
   gh api 'repos/juxt/allium-tools/contents/crates/allium/Cargo.toml?ref=v3.6.1' --jq .content | base64 -d > ai_tmp/upstream/allium-cli.Cargo.toml
   gh api 'repos/juxt/allium-tools/contents/LICENSE?ref=v3.6.1' --jq .content | base64 -d > ai_tmp/upstream/LICENSE
   for f in allium-files.txt main.rs test_plan.rs domain_model.rs allium-cli.Cargo.toml LICENSE; do test -s "ai_tmp/upstream/$f" || { printf '%s\n' "fetch failed: $f" >&2; exit 1; }; done
   ```

   Endpoints are quoted because `?` globs under zsh; every line in this ticket's fences
   runs the same under `bash` and `zsh` unless it says `bash -c`. Quote each command's
   exit status; a 403 or any other error is a stop, never absence (`CONVENTIONS.md` §11
   "Checks fail closed").

   Quote the `.allium` list (this is the corpus candidate), the CLI crate's file list
   and the `[dependencies]` table of `ai_tmp/upstream/allium-cli.Cargo.toml`. Record,
   from `main.rs`: the command names, the exit-code policy, the `--version` string and
   how it is built (a literal, or something read from `allium-parser`), how stdout is
   written (locked handle, `println!`, buffered or not), and what happens on a write
   error. Then `cargo info allium-cli@3.6.1` and `cargo info allium-parser@3.6.1`
   (network), quoted. `allium-parser`'s source is already in cargo's registry cache
   after step 1 (`just check` builds against the `=3.6.1` pin), under
   `"${CARGO_HOME:-$HOME/.cargo}"/registry/src/*/allium-parser-3.6.1/src/`. Run, each
   quoted with its exit status: the path control
   `rg -n 'pub fn parse' "${CARGO_HOME:-$HOME/.cargo}"/registry/src/*/allium-parser-3.6.1/src/`
   (must match, or the path is wrong: stop); the positive control
   `rg -n 'language versions' ai_tmp/upstream/main.rs` (must hit the `--version` arm, or
   stop); then
   `rg -n -i 'language version|versions 1|SUPPORTED|1, 2, 3' "${CARGO_HOME:-$HOME/.cargo}"/registry/src/*/allium-parser-3.6.1/src/`
   over the whole `src/` tree, not `lib.rs` alone, which only re-exports its modules.
   Only after both controls hit does an exit 1 from the last search answer
   `CONVENTIONS.md` §12 claim 12 as "not exposed"; a hit is quoted with its file and line
   and judged. The claim is answered when the `main.rs` lines that build the suffix are
   quoted and every identifier they use is traced to a `pub` item of `allium-parser` or
   to a literal in `main.rs`.

3. **The parity harness, designed before anything is built.** Write the design into the
   hand-back notes and the harness into `ai_tmp/parity/` (it moves to `tests/parity/` in
   T13, so write it as it will land). The design, which T13 inherits:

   - **The reference.** `cargo install allium-cli@3.6.1 --locked --root
     ai_tmp/parity-reference` (network, authorised). Never a downloaded release asset
     (`CONVENTIONS.md` §9 "The parity reference", §11 "Untrusted material"). The root is
     never on `PATH`; the harness takes its absolute path as an argument. In T13 the root
     is `.tools/parity/`. Quote
     `ai_tmp/parity-reference/bin/allium --version; echo "exit $?"` beside
     `rg -n 'ALLIUM_VERSION_STRING' crates/alliumpy-core/src/lib.rs` and state whether
     the printed string and the literal are equal (`CONVENTIONS.md` §12 claim 12, first
     half).
   - **The corpus.** Every `.allium` file step 2 listed, fetched into
     `ai_tmp/parity-corpus/` preserving upstream's directory shape (network, authorised;
     read-only), one `gh api` read per path, each checked against upstream's blob sha,
     then counted:

     ```sh
     set -o pipefail   # a failed gh api must fail the pipeline, not leave an empty file behind
     gh api 'repos/juxt/allium-tools/git/trees/v3.6.1?recursive=1' --jq '.tree[] | select(.path | endswith(".allium")) | "\(.sha) \(.path)"' > ai_tmp/upstream/allium-shas.txt
     while read -r sha p; do mkdir -p "ai_tmp/parity-corpus/$(dirname "$p")" && gh api "repos/juxt/allium-tools/contents/$p?ref=v3.6.1" --jq .content | base64 -d > "ai_tmp/parity-corpus/$p" && test -s "ai_tmp/parity-corpus/$p" && [ "$(git hash-object "ai_tmp/parity-corpus/$p")" = "$sha" ] || { printf '%s\n' "fetch failed: $p" >&2; exit 1; }; done < ai_tmp/upstream/allium-shas.txt
     find ai_tmp/parity-corpus -name '*.allium' -empty   # must print nothing
     find ai_tmp/parity-corpus -name '*.allium' | wc -l   # must equal the next line
     wc -l < ai_tmp/upstream/allium-files.txt
     ```

     Without `pipefail` a failed read exits 0 through `base64 -d`, and the redirect
     creates the file either way, so the count alone proves nothing; quote the loop's exit
     status, the empty `-empty` listing and the count together.

     The loop runs from the worktree root, never from inside either directory. Shape
     matters because cross-module `use` resolution consults the filesystem; each file is
     kept with no edit. T13 repeats these reads into `tests/fixtures/parity/` and commits
     them with a `README.md` naming the origin, tag and licence. The corpus directory
     holds no Python and no harness file.
   - **The harness.** `tests/parity/run.py`, run as `python -I tests/parity/run.py
     --reference <abs path> --candidate <abs path> --corpus <dir>`. For each corpus file
     and for each of `check`, `analyse`, `parse`, `plan`, `model`: run both binaries with
     the same relative path from the same working directory, capture stdout bytes,
     stderr bytes and the exit status, and compare stdout bytes and exit status exactly.
     Then the directory form (`check <corpus dir>`, `analyse <corpus dir>`), `help`,
     `-h`, `--help`, `-V`, `--version`, no arguments (exit 2), an unknown command, a
     nonexistent path, and a path to an empty directory. stderr is compared as a
     reported difference, not a failure, unless the recommendation says otherwise, and
     the notes say why. Outside a `just` recipe nothing puts pixi's Python on `PATH`, so
     every harness run in this spike names `.pixi/envs/default/bin/python`.
   - **Fails closed.** An empty corpus and a nonexistent corpus directory (distinct
     messages), a missing binary, a binary that is not executable, or zero comparisons
     is a failure with a message, never a pass. Before the corpus runs, a **positive
     control**: one file whose reference exit status under `check` the harness has just
     observed to be exactly 1 (an error or warning, never 2, which is no inputs;
     `CONVENTIONS.md` §9) and which is named in the output, proving the reference does
     fail on something: the first corpus file that does or, if no upstream file does,
     this repository's own `tests/fixtures/smoke/broken.allium`, copied into the corpus
     under `ai_tmp/parity-corpus/alliumpy/` with a comment attributing it to this
     repository. The notes say the control came from it, T13 commits it under
     `tests/fixtures/parity/alliumpy/`, and Open points records "corpus thin on errors"
     (`CONVENTIONS.md` §13). After the corpus, a **negative control** that `run.py`
     performs itself on every invocation, with no flag to disable it: it writes two
     wrapper scripts into a temporary directory outside the corpus (one that runs the
     candidate and appends one byte to stdout; one that exits 0 regardless), reruns one
     comparison through each, and must report a difference for both; a control that
     does not fire is a harness error, never a pass. `just parity` (T13) runs `run.py`
     once and so inherits both controls.
   - **Determinism control.** `mkdir -p ai_tmp/parity-reference-copy && cp
     ai_tmp/parity-reference/bin/allium ai_tmp/parity-reference-copy/allium`, then the
     harness with the copy as the candidate must report `0 differ` (the harness refuses a
     candidate whose resolved path equals the reference's, so a copy, not the same path).
     A difference here is upstream nondeterminism (`read_dir` order, `HashMap`
     iteration), recorded in the notes before any prototype is judged.
   - **Output.** One line per comparison, then a summary (`N compared, M differ`), exit
     1 on any difference, and a unified diff of the first differing stdout pair.
   - **Isolation.** `-I` on every Python invocation; the harness imports nothing from the
     corpus directory; `TZ=UTC`, `LC_ALL=C` and a fixed `cwd` so paths print identically.
   - **Lint-clean as it lands.** Before the review, from the ticket worktree, each exits
     0, quoted: `.pixi/envs/default/bin/ruff check ai_tmp/parity/run.py`,
     `.pixi/envs/default/bin/ruff format --check ai_tmp/parity/run.py` and
     `.pixi/envs/default/bin/mypy --strict ai_tmp/parity/run.py`. The text T13 commits
     must already pass `py-lint` and `py-typecheck`; every `noqa` carries its reason.
     T03 may tighten the configuration after this spike; T13 then fixes the harness,
     never the configuration.

   **Adversarial review** (`CONVENTIONS.md` §14): the harness design and
   `ai_tmp/parity/run.py`, before step 4 builds a prototype on it. Ask: how the harness
   could print `0 differ` while the candidate is wrong (an exception swallowed, a
   comparison of `str` after decoding, a candidate that is the reference by path, a
   corpus of zero files, `cwd` differences baked into `spec_file`); whether the positive
   control is observed rather than assumed; whether anything from the corpus or from
   `ai_tmp/upstream/` can execute; which upstream subcommand or argument shape the matrix
   misses.

4. **Prototype (a), vendor.** In `ai_tmp/proto-a/`, a copy of the repository: from the
   ticket worktree, `git worktree add -b spike/proto-a ai_tmp/proto-a`, then
   `just initialize` inside it (network, authorised; P `scripts/initialize.sh` skips
   `install-hooks` in a secondary worktree). Then copy the three upstream modules step 2
   fetched into `ai_tmp/upstream/` (`main.rs`, `test_plan.rs`, `domain_model.rs`) under
   `crates/alliumpy-core/src/cli/` with the MIT header and a file-level comment naming
   the tag; replace `fn main() -> ExitCode` with `pub fn run(args: &[String], stdout:
   &mut dyn Write, stderr: &mut dyn Write) -> i32`, every `print!`, `println!` and
   `eprintln!` with writes to those handles, and every returned `ExitCode` with the
   `i32` it carries; the `--version` arm prints `ALLIUM_VERSION_STRING` (the copied
   literal, `CONVENTIONS.md` §9), never `env!("CARGO_PKG_VERSION")`; add `serde`
   (features `["derive"]`: `domain_model.rs` derives `Serialize`) and `serde_json`
   (`main.rs` writes JSON) to `[workspace.dependencies]` at full `x.y.z` caret ranges
   and to the core, each with the decision-0004 note (`CONVENTIONS.md` §2); then move
   `Cargo.lock`, which every recipe below reads with `--locked`, by
   `cargo update -p serde -p serde_json --offline` (both are already locked through
   `allium-parser`, `CONVENTIONS.md` §1 fact 5), or, if that does not resolve offline, by
   `just lock` inside `ai_tmp/proto-a` (network, authorised by this step alone); quote the
   lock diff; expose `run` through the pyo3 module as `_run_cli(args: list[str]) -> int`
   that writes to Python's `sys.stdout.buffer` and `sys.stderr.buffer`, or to the process
   file descriptors directly; `_cli.py` calls it with `sys.argv[1:]`, flushes, and
   `sys.exit`s with the code. `just clippy`, `just metrics`, `just test`, `just coverage`,
   `just wheel-smoke`, then the harness, run with the ticket worktree's
   `.pixi/envs/default/bin/python -I`, with the smoke venv's `allium` as the candidate.
   Record every lint `clippy` raises and every finding `metrics` raises under `src/cli/`
   (upstream has no clippy configuration; record whether `main.rs` uses `HashMap` or
   `HashSet`, which `clippy.toml` disallows, and the length of its longest function
   against the 60-line threshold), and the `coverage` report's figures for `src/cli/`
   and for the crate (record which of the three files carry unit tests; expect `main.rs`
   to carry none). Quote the summary line and the two control results. Record the size
   of the diff from upstream's previous tag to `v3.6.1` for these three files (the tag
   before `v3.6.1` in `gh api repos/juxt/allium-tools/tags --paginate --jq '.[].name'`;
   `gh api` that tag's three blobs into `ai_tmp/upstream/prev/` under `set -o pipefail`,
   `test -s` on each file, then `diff` them), as the per-bump cost.

5. **Prototype (b), bundle.** In `ai_tmp/proto-b/`, a second worktree created and
   initialised the same way (`git worktree add -b spike/proto-b ai_tmp/proto-b`, then
   `just initialize` in it; network, authorised): the binary from step 3's reference
   root copied to `crates/alliumpy/python/alliumpy/_bin/allium`; `_cli.py` resolves it
   with `importlib.resources`, on POSIX `os.execv`s it with `sys.argv`, and the Windows
   branch (designed, written, not run) uses `subprocess.run` and exits with its
   `returncode`. Confirm maturin includes `_bin/allium` with its executable bit in the
   wheel (`.pixi/envs/default/bin/python -I -m zipfile -l dist/*.whl` for the entry,
   then
   `.pixi/envs/default/bin/python -I -c 'import sys, zipfile; i = zipfile.ZipFile(sys.argv[1]).getinfo("alliumpy/_bin/allium"); print(oct(i.external_attr >> 16))' dist/*.whl`,
   which must print a mode with the execute bits, such as `0o100755`; `-l` lists names,
   dates and sizes only, not modes), `just wheel-smoke`, then the harness, run the same
   way. Record the wheel size against (a)'s, what the release matrix would have
   to add (a `cargo install allium-cli` per target before `maturin build`, the musllinux
   case under maturin-action's container), and that the parity result is trivially
   exact because candidate and reference are the same build, which is why it still runs.

6. **Route (c), upstream.** Draft, into the hand-back notes, the pull request text: a
   `src/lib.rs` for `allium-cli` exposing `pub fn run(args: &[String], out: &mut impl
   Write, err: &mut impl Write) -> i32`, `main.rs` reduced to calling it, no behaviour
   change, with the parity harness as the argument that none occurred. State that T13
   may take this route only if the pull request is merged and the release is on
   crates.io on the day T13 opens, and that the drafted T13 steps for (a) remain its
   fallback.

   Do not file. Filing upstream is the maintainer's separately authorised action
   (`CONVENTIONS.md` §11, "Separately authorised actions"), taken outside this spike;
   this step only records the draft, which step 8's review covers.

7. **Rulings T13 and T14 need.**
   - **The sdist** (`CONVENTIONS.md` §9 "The sdist"). Under (b) it is unbuildable;
     under (a) and (c) a user on a platform the matrix misses, or on Python 3.10, gets a
     silent Rust build. Recommend keeping or dropping it, with the reason, and if kept,
     what T14 must assert is inside it (`Cargo.lock`, the vendored sources, both licence
     texts).
   - **The `--version` suffix** (claim 12): what `(language versions: 1, 2, 3)` is built
     from in `main.rs`, whether `allium-parser` exposes it, and therefore whether
     `ALLIUM_VERSION_STRING` can be derived or stays a copied literal that
     `version-check` compares, as the whole string, against the smoke venv's
     `allium --version` (`CONVENTIONS.md` §9), while equality with the reference's
     output is `just parity`'s job.
   - **Pipes and flushing.** With the reference and with each prototype's candidate,
     first record `<binary> check <corpus dir> | wc -c`, quoted: the broken-pipe
     measurement is only meaningful when stdout exceeds the pipe buffer (64 KiB),
     because a writer whose whole output fits in the buffer never sees `EPIPE`. If it is
     under 65536, drive the pipe with an output that exceeds the buffer (`parse` of the
     largest corpus file, or the corpus copied N times under
     `ai_tmp/parity-corpus-wide/`, never edited) and say which in the notes and in the
     drafted T13 test. Then run
     `bash -c '<binary> <command> <that input> | head -c 1; echo "${PIPESTATUS[0]}"'`
     (always through `bash -c`: zsh has no `PIPESTATUS`) ten times and record every
     distinct pair of exit status and first stderr line seen; only a pair seen on every
     run is a behaviour T13 asserts, and if the runs disagree the drafted T13 test
     asserts only a nonzero exit and no Python traceback, with this note cited. Then, on
     Linux only, `allium check <corpus dir> > /dev/full; echo $?`, and record the exit
     status and stderr of each beside the output of `uname -s`. `/dev/full` does not
     exist on macOS: the shell's redirect fails before `allium` runs and `$?` is 1, which
     is not the reference's behaviour. On macOS record the `/dev/full` case as not
     measured here, and have the drafted T13 step mark that one test
     `@pytest.mark.skipif(sys.platform != "linux", reason=...)` with a stated reason, so
     that the `parity` CI job on its Linux runner is where it runs. Whatever the
     reference does (a SIGPIPE death, a `Broken pipe` message, exit 1) is the behaviour
     T13 must reproduce and test; a Python shim that turns SIGPIPE into a traceback is a
     parity failure.
   - **The gates under route (a)** (`CONVENTIONS.md` §4 gates 6, 7 and 10; §7
     invariants 5 and 6; §9 "The shape"). From step 4's record, rule on each. Coverage:
     either `src/cli/` is unit-tested in Rust to the floor, and the drafted T13 steps
     include those tests with the prototype's figure quoted; or it is excluded from the
     floor, and the drafted steps name the `coverage` line T13 edits as `shared, own
     lines` while this ruling states, for the maintainer, the change to `CONVENTIONS.md`
     §7 invariant 6 it needs, because no ticket lowers a floor the design states. Lints
     and metrics: which lints and rustqual findings upstream's code trips, and the
     `#[expect(lint, reason = "...")]` attributes or source fixes the drafted steps
     carry for each; never an `allow`, and never a change to the lint tables,
     `clippy.toml` or `rustqual.toml` that this ruling does not state with its reason.
   - **What T13 tests beyond the corpus:** the list above, plus flush order between
     stdout and stderr when both are written, and the exit codes 0, 1 and 2 by fixture.
     And, quoted from the harness output: the list of matrix items on which the
     reference's stdout is empty and its exit status is 2 (no arguments, and whichever
     of an unknown command, a nonexistent path and an empty directory behave so), plus
     `-V` and `--version`; each of these matches T00's `_cli.py` by accident, so T13's
     run before the command exists must expect exactly that recorded set of matches,
     never a guessed count.

8. **Recommend.** Complete the table in Goal with the measured columns, state the
   recommendation and its reason, write decision 0014's body and T13's route-specific
   steps (Hand-back notes). Then `just check` on the ticket worktree (nothing but this
   file changed), `status: done`, and one commit. Leave `ai_tmp/proto-a` and
   `ai_tmp/proto-b` in place: Verification runs the candidate from the chosen route's
   prototype (`ai_tmp/proto-a` for (a), `ai_tmp/proto-b` for (b)).

   **Adversarial review** (`CONVENTIONS.md` §14): the recommendation, the evidence and
   the two drafts, before the status is set. Ask: which prototype's parity result rests
   on a harness run whose controls did not fire; which cost in the table is asserted and
   not measured; whether the drafted T13 steps let T13 pick a different route; whether
   those steps reach `just check` green under the floor, the lint tables and
   `rustqual.toml` as they stand, or the gate ruling says what changes; whether the
   sdist ruling follows from the route chosen; whether anything in the drafts derives
   one version from another (`CONVENTIONS.md` §1 decision 4).

## Acceptance criteria

- The harness exists in `ai_tmp/parity/run.py` as it will land in `tests/parity/`, its
  full text is quoted in the hand-back notes, and its positive and negative controls
  fired, quoted, on every run the notes cite.
- The harness is green under the worktree's `ruff check`, `ruff format --check` and
  `mypy --strict`, quoted.
- Prototypes (a) and (b) each ran the full harness over the full corpus (count stated,
  equal to step 2's list plus any control file this repository added), with the summary
  line quoted and headed by the commit the prototype worktree was at
  (`git rev-parse --short HEAD` there) plus `with uncommitted changes`
  (`CONVENTIONS.md` §11); the stderr differences, if any, listed.
- Both halves of `CONVENTIONS.md` §12 claim 12 are answered: the
  `cargo install allium-cli@3.6.1 --locked` build's exit status, the reference's
  `--version` output quoted beside the `ALLIUM_VERSION_STRING` literal in
  `crates/alliumpy-core/src/lib.rs` with the equality stated, and the `main.rs` lines
  and the `allium-parser` search quoted.
- The pipe behaviour of the reference is recorded, and the `/dev/full` behaviour is
  recorded from a Linux run or marked as not measured here, each beside its `uname -s`.
- The sdist ruling is stated with its reason.
- The gate ruling for route (a) is stated: what the vendored code does to the floor, the
  lint tables and `rustqual.toml`, and what the drafted T13 steps do about each.
- The hand-back notes hold the recommendation, the completed table, the drafted decision
  0014 and the drafted route-specific steps for T13, each for the chosen route only, and
  the drafted upstream pull request text.
- `git status --porcelain` on the ticket branch lists only this file before the commit
  and nothing after it; `just check` is green on it.
- The adversarial reviews in Steps ran (`CONVENTIONS.md` §14), and every valid finding is
  fixed or handed back.

## Verification

```sh
PROTO=ai_tmp/proto-a   # the chosen route's prototype: proto-a for (a), proto-b for (b)
test -x "$PROTO/target/wheel-smoke/venv/bin/allium" || echo 'candidate missing: rebuild the prototype before quoting'
wc -l ai_tmp/upstream/allium-files.txt
ls ai_tmp/parity-reference/bin/
ai_tmp/parity-reference/bin/allium --version; echo "exit $?"
.pixi/envs/default/bin/python -I ai_tmp/parity/run.py --reference "$PWD/ai_tmp/parity-reference/bin/allium" --candidate "$PWD/ai_tmp/parity-reference-copy/allium" --corpus ai_tmp/parity-corpus; echo "exit $?"   # must be 0 differ
.pixi/envs/default/bin/python -I ai_tmp/parity/run.py --reference "$PWD/ai_tmp/parity-reference/bin/allium" --candidate "$PWD/$PROTO/target/wheel-smoke/venv/bin/allium" --corpus ai_tmp/parity-corpus; echo "exit $?"
mkdir -p ai_tmp/parity-corpus-empty && .pixi/envs/default/bin/python -I ai_tmp/parity/run.py --reference "$PWD/ai_tmp/parity-reference/bin/allium" --candidate "$PWD/$PROTO/target/wheel-smoke/venv/bin/allium" --corpus ai_tmp/parity-corpus-empty; echo "exit $?"   # must be nonzero, and the message must name an empty corpus
just --evaluate PATH > ai_tmp/path.txt && grep -c . ai_tmp/path.txt && ! grep -q parity-reference ai_tmp/path.txt; echo "exit $?"   # must be 0: PATH was read and the reference root is not on it
git status --porcelain
just check
```

The harness lines name the ticket worktree's pixi interpreter by path because they run
from the agent's shell, where nothing puts `python` on `PATH`; inside `just parity` (T13)
the bare `python` is the same interpreter.

Expected: the corpus count; one `allium` binary; the upstream version string; `0 differ`
for the reference against its copy; a summary with `0 differ` for the recommended
route's prototype (`$PROTO`), exit 0; a failure whose message names an empty corpus (not
a missing path, not a same-path refusal); a positive entry count and exit 0, so the
reference root is not on the Justfile's `PATH`; one line naming this file; the runner's
success line.

After this block has been run and quoted before the final commit (the quote headed by
its commit, "with uncommitted changes", `CONVENTIONS.md` §11), and again after the rebase
(`README.md`, "How to pick up a ticket", step 6), remove `ai_tmp/proto-a` and
`ai_tmp/proto-b` with `git worktree remove --force` (both are dirty: vendored sources and
`target/`), then delete the branches `spike/proto-a` and `spike/proto-b` with
`git branch -D` (they are unmerged by design).

**Authorisation required: push and open a pull request.** Stop and ask (`CONVENTIONS.md`
§11, "Separately authorised actions").

## Hand-back notes

To be written by the executing agent, in this order:

- **What was verified, and how.** One subsection per step 2, 3, 4, 5 and 7 item: the
  command, its output, its date, and what it shows. Every network use named with the
  authorisation that covered it.
- **The harness design**, as T13 will inherit it, with the control results of each run.
- **The harness, verbatim.** The full text of `ai_tmp/parity/run.py` as it ran for the
  recommended route, in a fenced `python` block, and the argument matrix as a table with
  its row count stated; T13 commits the text unchanged except for what the T03-final
  lint configuration demands, each change recorded in T13's notes, as
  `tests/parity/run.py`, and the table into `tests/parity/README.md`.
- **Prototype results**, (a) and (b): the summary line, the stderr differences, the
  coverage effect, the lint and rustqual findings, the wheel size, the per-bump cost.
- **Recommendation.** The completed table and the paragraph that chooses.
- **Drafted decision 0014**, in `CONVENTIONS.md` §8's format, ready for T13 to land as
  `docs/decisions/0014-cli-strategy.md`.
- **Drafted T13 route-specific steps**, for the chosen route only, numbered, each with
  the file it touches and the proof it ends in; T13 copies them verbatim.
- **Drafted upstream pull request**, title and body.
- **Review records** for both checkpoints (`CONVENTIONS.md` §14).
- **Handed back.** To the maintainer (every `CONVENTIONS.md` change the rulings need,
  §7 invariant 6 included), to T13, T14 and T17, each item with the file it touches.
- **Deviations**, and why. **Open points settled.**

## Open points

- Whether stderr parity should be required. Upstream writes read errors to stderr; if
  the candidate's stderr differs only in a Python traceback shape on a path that
  upstream never reaches, the recommendation says so and T13 compares stderr too.
- Whether the corpus should include files that exercise cross-module `use` resolution
  across directories; if upstream's tree holds none, T13 writes one pair, attributed to
  this repository, and the notes say the corpus is thin there (`CONVENTIONS.md` §13).
- If `allium-parser` does not expose the language-version list and the recommendation is
  (a), whether the vendored `main.rs` carries the literal (then in T13 `version-check`
  compares it against the smoke venv's output and `just parity` against the reference)
  or the core derives it from the vendored code; say which.
