---
id: S01
title: "Spike: how the `allium` command gets into the wheel, with a parity harness"
status: done
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
   `returncode`. Run `just wheel-smoke` after these edits, rebuilding the wheel and
   installing it into the smoke venv before inspecting its archive. Confirm maturin
   includes `_bin/allium` with its executable bit in the freshly built
   wheel (`.pixi/envs/default/bin/python -I -m zipfile -l dist/*.whl` for the entry,
   then
   `.pixi/envs/default/bin/python -I -c 'import sys, zipfile; i = zipfile.ZipFile(sys.argv[1]).getinfo("alliumpy/_bin/allium"); print(oct(i.external_attr >> 16))' dist/*.whl`,
   which must print a mode with the execute bits, such as `0o100755`; `-l` lists names,
   dates and sizes only, not modes), then the harness against that smoke venv's
   installed command, run the same way. Record the wheel size against (a)'s, what the
   release matrix would have to add (a `cargo install allium-cli` per target before
   `maturin build`, the musllinux
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
- Prototype (b)'s archive listing and execute-mode check inspect the wheel rebuilt by
  `just wheel-smoke` after the bundle edits; its harness uses that installed wheel.
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

### What was verified, and how

All of it on 2026-10-24, macOS (`uname -s` prints `Darwin`), Rust 1.99.1, from the
ticket worktree unless a prototype worktree is named. Network uses, each authorised by
the step named: `git fetch origin` (step 1, and again before the commit); `just
initialize` in the ticket worktree (step 1), in `ai_tmp/proto-a` (step 4) and in
`ai_tmp/proto-b` (step 5); read-only `gh api` reads of `juxt/allium-tools` (steps 2, 3
and 4); `cargo info` (step 2); `cargo install allium-cli@3.6.1 --locked` (step 3); the
reviewers' model API calls (§14, each checkpoint). `cargo update` ran `--offline`;
`just lock` never ran. Raw logs stay in `ai_tmp/logs/`.

#### Step 1: baseline

At `e0d2201`: `git fetch origin` exit 0; `git rev-parse HEAD origin/main` printed
`e0d2201d33b8a0c69fe834ce28a3e13a69350dee` twice; `just initialize` exit 0
(`Secondary worktree: skipping install-hooks.`); `just check` exit 0, last line:

```text
All checks passed and the worktree is unchanged.
```

#### Step 2: upstream, re-read as data

At `e0d2201`, the step's fence run as one `bash` invocation under `set -o pipefail`:

```text
false
truncated exit 0
allium-files exit 0
crates/allium/Cargo.toml
crates/allium/src
crates/allium/src/domain_model.rs
crates/allium/src/main.rs
crates/allium/src/test_plan.rs
crates/allium/tests
crates/allium/tests/ambiguous_imports.rs
crates/allium/tests/cli_help.rs
crates/allium/tests/cli_smoke.rs
crates/allium/tests/cross_module_lifecycle.rs
crates/allium/tests/cross_module_unused.rs
crates/allium/tests/properties.rs
crates/allium/tests/witness_matrix.rs
crate list exit 0
main.rs exit 0
test_plan.rs exit 0
domain_model.rs exit 0
Cargo.toml exit 0
LICENSE exit 0
test -s loop exit 0
```

The `.allium` list (the corpus), 27 lines:

```text
crates/allium-parser/tests/fixtures/comprehensive-edge-cases.allium
crates/allium-parser/tests/fixtures/language-reference-constructs.allium
crates/allium-parser/tests/fixtures/v3-lifecycle.allium
docs/project/specs/allium-analyse-tool-behaviour.allium
docs/project/specs/allium-check-reporting-behaviour.allium
docs/project/specs/allium-check-tool-behaviour.allium
docs/project/specs/allium-cli-help-behaviour.allium
docs/project/specs/allium-development-workflow-behaviour.allium
docs/project/specs/allium-diagram-ergonomics-behaviour.allium
docs/project/specs/allium-diagram-tool-behaviour.allium
docs/project/specs/allium-drift-tool-behaviour.allium
docs/project/specs/allium-extension-behaviour.allium
docs/project/specs/allium-extension-diagram-preview-behaviour.allium
docs/project/specs/allium-extension-productivity-presets-behaviour.allium
docs/project/specs/allium-format-tool-behaviour.allium
docs/project/specs/allium-language-qol-behaviour.allium
docs/project/specs/allium-release-artifacts-behaviour.allium
docs/project/specs/allium-semantic-strengthening-behaviour.allium
docs/project/specs/allium-single-file-tool-behaviour.allium
docs/project/specs/allium-snippets-behaviour.allium
docs/project/specs/allium-trace-tool-behaviour.allium
extensions/allium/test/fixtures/format/basic.expected.allium
extensions/allium/test/fixtures/format/basic.input.allium
extensions/allium/test/fixtures/refactor/extract-inline-enum.expected.allium
extensions/allium/test/fixtures/refactor/extract-inline-enum.input.allium
extensions/allium/test/fixtures/refactor/extract-literal.expected.allium
extensions/allium/test/fixtures/refactor/extract-literal.input.allium
```

The `[dependencies]` table of `allium-cli`'s `Cargo.toml` at `v3.6.1`:

```toml
[dependencies]
allium-parser = { path = "../allium-parser", version = "3.0.0" }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

From U `crates/allium/src/main.rs` at `v3.6.1` (801 lines):

- **Commands.** `check`, `analyse`, `parse`, `plan`, `model`, `help [<command>]`;
  `-h`/`--help` and `-V`/`--version` are matched on the first argument only, so
  `--version extra` still prints the version; `--help` or `-h` anywhere after a
  command prints that command's help (lines 127-131). `check` and `analyse` take
  `<path>...` (files or directories, searched recursively with an unsorted
  `read_dir`); `parse`, `plan` and `model` take exactly one file.
- **Exit codes.** 0 on success. `check`: 1 when any diagnostic is an error or warning;
  `analyse`: 1 when any finding is produced; both also 1 when a named file cannot be
  read (the read error goes to stderr and the file list was non-empty, so a nonexistent
  path is 1, not 2). `parse`, `plan`, `model`: 1 on an error-severity diagnostic or a
  read error. 2 on no arguments, an unknown command, `help <unknown>`, no `.allium`
  file resolved (`check`, `analyse`), or the wrong number of files (`parse`, `plan`,
  `model`).
- **`--version`.** Lines 113-116:
  `println!("allium {} (language versions: 1, 2, 3)", env!("CARGO_PKG_VERSION"));`.
  The version is `allium-cli`'s own package version; the suffix is a literal in
  `main.rs`.
- **How stdout is written.** `print!` and `println!` on the process's global stdout
  (std's line-buffered handle, locked per call); each file's result is one
  `println!("{}", serde_json::to_string_pretty(&output).unwrap())`. stderr through
  `eprintln!`.
- **A write error.** `println!` panics with `failed printing to stdout: <error>`. The
  Rust runtime ignores SIGPIPE, so a closed pipe is an `EPIPE` write error, a panic and
  exit 101 (measured under step 7).
- **`HashMap`/`HashSet`.** Yes: `main.rs` throughout (`CrossModuleContext`, 107
  `disallowed_types` hits) and `test_plan.rs` line 208, iterated to emit obligations.
- **Longest function.** `build_cross_module_context`, lines 306-604 (299 lines; clippy
  counts 212 against the 60-line threshold).

`cargo info allium-cli@3.6.1` (exit 0) and `cargo info allium-parser@3.6.1` (exit 0):

```text
allium-cli
CLI for checking Allium specification files
version: 3.6.1
license: MIT
rust-version: unknown
documentation: https://docs.rs/allium-cli/3.6.1
crates.io: https://crates.io/crates/allium-cli/3.6.1
allium-parser
Parser and structural validator for the Allium specification language
version: 3.6.1
license: MIT
rust-version: unknown
documentation: https://docs.rs/allium-parser/3.6.1
crates.io: https://crates.io/crates/allium-parser/3.6.1
```

Claim 12's searches (`~` for the home directory; registry directory
`index.crates.io-1949cf8c6b5b557f`):

```text
$ rg -n 'pub fn parse' ~/.cargo/registry/src/*/allium-parser-3.6.1/src/
…/allium-parser-3.6.1/src/parser.rs:25:pub fn parse(source: &str) -> ParseResult {
…/allium-parser-3.6.1/src/parser.rs:1748:    pub fn parse_expr(&mut self, min_bp: u8) -> Option<Expr> {
path control exit 0
$ rg -n 'language versions' ai_tmp/upstream/main.rs
114:                "allium {} (language versions: 1, 2, 3)",
positive control exit 0
$ rg -n -i 'language version|versions 1|SUPPORTED|1, 2, 3' ~/.cargo/registry/src/*/allium-parser-3.6.1/src/
…/src/parser.rs:329:                    format!("unsupported allium version {v}; this parser supports versions 1, 2 and 3"),
…/src/parser.rs:2629:    fn version_unsupported_errors() {
…/src/parser.rs:2633:            d.severity == Severity::Error && d.message.contains("unsupported allium version 99")
…/src/parser.rs:2634:        ), "expected unsupported version error, got: {:?}", r.diagnostics);
…/src/parser.rs:3274:        let l = [1, 2, 3]
…/src/parser.rs:3283:        let r = parse_ok("default E e = { items: [1, 2, 3] }");
…/src/parser.rs:5533:            d.severity == Severity::Error && d.message.contains("unsupported")
…/src/parser.rs:6245:            && d.message.contains("unsupported")));
…/src/ast.rs:593:    /// not a supported pattern.
…/src/analysis.rs:5888:                                "Rule '{rule_name}' uses an unsupported trigger form in 'when:'.",
…/src/analysis.rs:8665:        // not be rejected as an unsupported trigger form (issue #19).
search exit 0
$ rg -n 'pub (const|static|fn) .*[Vv]ersion' ~/.cargo/registry/src/*/allium-parser-3.6.1/src/
pub version items exit 1
```

Judged: the only non-test hit, `parser.rs:329`, is the text of a diagnostic inside the
private `Parser::parse_module`, whose supported set is the private match arm
`Some(1) | Some(2) | Some(3)` at line 323; the others are tests or unrelated uses of
"supported". No `pub` item names the language versions. The suffix's identifiers are
`env!("CARGO_PKG_VERSION")` (the CLI crate's own version, a Cargo build-time value) and
the literal `(language versions: 1, 2, 3)` in `main.rs`: **not exposed by
`allium-parser`**.

#### Step 3: the reference, the corpus and the harness

At `e0d2201`: `cargo install allium-cli@3.6.1 --locked --root ai_tmp/parity-reference`
exit 0, 14 crates compiled from upstream's published lock (`serde_json 1.0.149`,
`serde 1.0.228`, `regex-lite 0.1.9`, `allium-parser 3.6.1`), toolchain `rustc 1.99.1`.

```text
$ ls ai_tmp/parity-reference/bin/
allium
$ ai_tmp/parity-reference/bin/allium --version; echo "exit $?"
allium 3.6.1 (language versions: 1, 2, 3)
exit 0
$ rg -n 'ALLIUM_VERSION_STRING' crates/alliumpy-core/src/lib.rs
31:pub const ALLIUM_VERSION_STRING: &str = "allium 3.6.1 (language versions: 1, 2, 3)";
97:            super::ALLIUM_VERSION_STRING.starts_with(&format!("allium {} ", super::ALLIUM_VERSION))
```

The printed string and the literal are **equal** (claim 12, first half).

The corpus fetch (the step's loop under `set -o pipefail`, each file checked with
`git hash-object` against upstream's blob sha):

```text
shas exit 0
loop exit 0
empty-listing exit 0
      27
      27
```

The `-empty` listing printed nothing; 27 files, equal to step 2's list. No control file
was added: an upstream file is the positive control (below).

The harness was built test-first against fake binaries: 24 self-tests in
`ai_tmp/parity-selftest/test_run.py` (scratch, never lands), each written red before
the code that made it green: nonexistent and empty corpus (distinct messages), missing,
non-executable and relative binaries, a candidate symlinked or hard-linked to the
reference, identical binaries, a one-byte stdout difference with its diff, an
exit-status-only difference, a stderr-only difference (reported, passing), a candidate
that cannot `exec`, the positive control named, no positive control, exit 2 not a
positive control, a reference that cannot run, both negative controls firing, each
negative control not firing (a harness error with no summary line), each row's
reference outcome, a local import pair compared named together in both orders, the same
with the `use` split from its string by a comment and a newline, and a symlinked corpus
file and a symlinked corpus directory (each a harness error). Last run: `24 passed`.

Lint, from the ticket worktree on the final text (sha-256 `db22c87f…`):

```text
$ .pixi/envs/default/bin/ruff check ai_tmp/parity/run.py; echo "exit $?"
All checks passed!
exit 0
$ .pixi/envs/default/bin/ruff format --check ai_tmp/parity/run.py; echo "exit $?"
1 file already formatted
exit 0
$ .pixi/envs/default/bin/mypy --strict ai_tmp/parity/run.py; echo "exit $?"
Success: no issues found in 1 source file
exit 0
```

Determinism control, at `e0d2201` with uncommitted changes (only `ai_tmp/`), run twice,
the two outputs byte-identical (`diff` exit 0):

```text
positive control: check <corpus>/crates/allium-parser/tests/fixtures/comprehensive-edge-cases.allium exits 1 under the reference
188 compared, 0 differ
negative control: candidate plus one byte, check <corpus>/crates/allium-parser/tests/fixtures/comprehensive-edge-cases.allium: fired (stdout differs)
negative control: candidate forced to exit 0, check <corpus>/crates/allium-parser/tests/fixtures/comprehensive-edge-cases.allium: fired (exit status: reference 1, candidate 0)
```

Separately, the reference's `check`, `analyse`, `plan` and `model` were run ten times on
every corpus file and the stdout hashes compared: no variation. Upstream is
deterministic on this corpus. The `HashMap` in `test_plan.rs` line 208 matters only for
a module with two or more entities carrying `when`-qualified fields, which no corpus
file has (Open points).

#### Step 4: prototype (a), vendor

`ai_tmp/proto-a` at `e0d2201` with uncommitted changes, created by
`git worktree add -b spike/proto-a ai_tmp/proto-a`; `just initialize` exit 0. What it
holds, in the form the drafted T13 steps below carry: the three files under
`crates/alliumpy-core/src/cli/` (produced by `vendor_cli.py`, whose output was checked
byte-identical to them with `cmp`), `cli.rs`, `pub mod cli;`, `serde` and `serde_json`,
`_run_cli`, the stub line, `_cli.py`, `test_run_cli.py`, the `rustqual.toml` key, the
`.editorconfig` section, `run_os`, and `tests/fixtures/parity/` (a copy of the sha-checked corpus, as T13 commits it).

The lock moved by `cargo update -p serde -p serde_json --offline` (exit 0,
`Locking 0 packages`), so `just lock` was not needed:

```diff
@@ -26,6 +26,8 @@ name = "alliumpy-core"
 version = "3.6.1"
 dependencies = [
  "allium-parser",
+ "serde",
+ "serde_json",
 ]
```

The diff of each vendored file from upstream's, in lines (header, attribute block and
transform): `main.rs` +79 −65, `test_plan.rs` +28 −7, `domain_model.rs` +18 −0.

**clippy**, before any `#[expect]` (unique sites; lib build, and where the test build
adds sites, `all`):

| File | Lints (sites) |
| --- | --- |
| `main.rs` | `disallowed_types` 107, `iter_over_hash_type` 11, `excessive_nesting` 8, `unwrap_used` 5, `str_to_string` 4, `bool_to_int_with_if` 2, `cognitive_complexity` 1 (32/15), `manual_let_else` 1, `redundant_closure_for_method_calls` 1, `too_many_lines` 1 (212/60), `unnested_or_patterns` 1, `unreachable` 1 |
| `test_plan.rs` | `uninlined_format_args` 43 (all 45), `collapsible_if` 14, `excessive_nesting` 13, `str_to_string` 8 (all 53), `unreachable_pub` 8, `cognitive_complexity` 3, `doc_markdown` 4, `map_unwrap_or` 4, `redundant_closure_for_method_calls` 4, `too_many_lines` 4, `disallowed_types` 2, `too_many_arguments` 2 (8/5, 6/5), `if_not_else` 1, `missing_const_for_fn` 1, `wildcard_imports` 1 (lib only), `assert_is_empty` 0 (all 11) |
| `domain_model.rs` | `unreachable_pub` 17, `collapsible_if` 4, `uninlined_format_args` 3 (all 5), `missing_const_for_fn` 3, `str_to_string` 3, `doc_markdown` 2, `excessive_nesting` 2, `cognitive_complexity` 1, `map_unwrap_or` 1, `redundant_closure_for_method_calls` 1, `too_many_lines` 1 (118/60), `wildcard_imports` 1 (lib only), `assert_is_empty` 0 (all 1) |

Each became one file-level `#![expect(lint, reason = "...")]` line, `cfg_attr(test, …)`
for a lint only the test build raises and `cfg_attr(not(test), …)` for one only the lib
build raises, so that every expectation is fulfilled in both builds. `cli.rs` carries
one more, `#[expect(clippy::unnecessary_debug_formatting, …)]` on `run_os`, whose
message prints the argument with `Debug` as upstream's panic does. clippy's `panic`
lint does not see the `panic!` inside `cli.rs`'s three local output macros (it fires on
the outermost macro call); those panics are deliberate, upstream's own behaviour on a
failed write, and each macro's doc comment says so. `just clippy` then exit 0. `cargo fmt --all --check` rewrote about 200
hunks of upstream's formatting, so the three `mod` declarations carry
`#[rustfmt::skip]`; `just fmt-check` then exit 0.

**rustqual** (`just metrics`) on the vendored code: exit 1, `59 finding(s) (25 IOSP
violation(s)), 60.7% quality score`. Its annotations, which number 70 and which S01
did not reconcile with the summary's 59: 19 IOSP errors, 4 IOSP warnings
and 2 IOSP notices; 4 SRP warnings (module length: `main.rs` 596 lines in 3 clusters,
`test_plan.rs` 1515 lines in 2; parameters: `walk_rule_items_inner` 6,
`extract_deps_from_items` 8); and 41 complexity notices (15 cognitive, 11 cyclomatic, 8
function length, 7 nesting depth). Of the 43 notices, 34 are in `test_plan.rs`, 5 in
`main.rs` and 4 in `domain_model.rs`. `max_suppression_ratio = 0.05` rules out a
`qual:allow` per finding under either count. With `exclude_files` naming the three files: exit 0, both
crates `Quality score: 100.0%`.

**Tests and coverage.** `test_plan.rs` carries 100 upstream unit tests and
`domain_model.rs` 40; `main.rs` carries none (upstream tests it through
`crates/allium/tests/`, not vendored). Seven `test_plan.rs` tests read
`../allium-parser/tests/fixtures/v3-lifecycle.allium`, upstream's workspace path, and
failed with `NotFound` until the transform pointed them at the parity corpus's copy.
With upstream's tests alone, `just coverage` exit 1 at 78.31% of lines (`main.rs` 0%).
With the eleven tests in `cli.rs` (expected values observed from the reference): `just
test` 157 passed; `just coverage` exit 0:

| File | Lines | Missed | Cover |
| --- | --- | --- | --- |
| `cli.rs` | 136 | 3 | 97.79% |
| `cli/domain_model.rs` | 639 | 43 | 93.27% |
| `cli/main.rs` | 485 | 67 | 86.19% |
| `cli/test_plan.rs` | 2134 | 185 | 91.33% |
| `lib.rs` | 56 | 0 | 100.00% |
| total over the core | 3450 | 298 | 91.36% |

The three vendored files alone: 3258 lines, 295 missed, 90.95%. `main.rs`'s misses include the
successful local `use` resolution branch, which the 27-file corpus never reaches.

**EditorConfig.** The hooks read only tracked files, so while the vendored files were
untracked they were never checked (checkpoint 2, breakage F1). With every change staged
(`git -C ai_tmp/proto-a add -A`), `just lint` exit 1, one hook failing (its tabs shown as spaces):

```text
EditorConfig.............................................................Failed
  crates/alliumpy-core/src/cli/domain_model.rs:
    976-982: Wrong amount of left-padding spaces(want multiple of 4)
    985: Wrong amount of left-padding spaces(want multiple of 4)
  crates/alliumpy-core/src/cli/test_plan.rs:
    2344-2346: Wrong amount of left-padding spaces(want multiple of 4)
    2349-2350: Wrong amount of left-padding spaces(want multiple of 4)
  crates/alliumpy-core/src/cli/main.rs:
    30: Wrong amount of left-padding spaces(want multiple of 4)
    33-38: Wrong amount of left-padding spaces(want multiple of 4)
    41-42: Wrong amount of left-padding spaces(want multiple of 4)
    57-59: Wrong amount of left-padding spaces(want multiple of 4)
    73-75: Wrong amount of left-padding spaces(want multiple of 4)
```

`main.rs`'s lines are the help text inside `HELP`, `CHECK_HELP` and `ANALYSE_HELP`
(what `allium --help` prints), the others Allium sources inside upstream's test
strings, so reindenting would change stdout or upstream's tests. A section
`[crates/alliumpy-core/src/cli/{main,test_plan,domain_model}.rs]` with
`indent_size = unset` (the mechanism
`[LICENSE]` already uses for verbatim text) lifts that one rule; every other hook,
typos included, passed over the staged vendored files and corpus.

**Edges the corpus cannot reach** (found by the code review before the commit;
`ai_tmp/notes/measure_edges.sh`, `measure_sigint.py` and `measure_closed.sh`, run
from this worktree). Before the fixes, proto-a differed from the reference three ways:
`check $'\xff.allium'` (an argument that is not UTF-8) exited 1 with a Python
`UnicodeEncodeError` traceback where the reference panics in `std::env::args` and
exits 101; with stdout closed (`>&-`) it printed an `AttributeError` traceback where
the reference prints nothing (Rust's runtime points a closed standard descriptor at
the null device); and SIGINT during a blocked read (a FIFO named as the file) left it
running until the read returned, then printed a `KeyboardInterrupt` traceback, where
the reference dies at once (status −2, nothing on stderr). proto-b matched on the
first and third and printed the same `AttributeError` on the second. The fixes:
`cli::run_os`, taking the arguments as OS strings and writing upstream's panic message
and returning 101 for one that is not UTF-8, called by `_run_cli` (now
`Vec<OsString>`); and in `_cli.py`, SIGINT's default action restored and a closed fd 0,
1 or 2 pointed at `os.devnull` before the call, and only an existing stream flushed.
After them, at proto-a `e0d2201` with uncommitted changes:

```text
reference: non-utf8 exit 101: |thread 'main' (<tid>) panicked at /rustc/…/library/std/src/env.rs:878:51:|called `Result::unwrap()` on an `Err` value: "\xFF.allium"|…
proto-a:   non-utf8 exit 101: called `Result::unwrap()` on an `Err` value: "\xFF.allium"|
reference: check <v3-lifecycle.allium> with stdout closed: exit 1, stderr empty
proto-a:   check <v3-lifecycle.allium> with stdout closed: exit 1, stderr empty
reference: -V with stdout closed: exit 0, stderr bytes 0
proto-a:   -V with stdout closed: exit 0, stderr bytes 0
reference: SIGINT while reading a FIFO: returncode -2; stderr empty
proto-a:   SIGINT while reading a FIFO: returncode -2; stderr empty
```

**Full gate.** `just check` in `ai_tmp/proto-a` with all 41 changes staged, exit 0:
`All checks passed and the worktree is unchanged.` (`EditorConfig` `Passed`, `just
test` 157 passed, coverage 91.36%, pytest `19 passed`, stubtest, `wheel-smoke` printing
`allium 3.6.1 (language versions: 1, 2, 3)`, `version-check`).

**Parity**, at proto-a `e0d2201` with uncommitted changes, candidate
`ai_tmp/proto-a/target/wheel-smoke/venv/bin/allium`, exit 0:

```text
positive control: check <corpus>/crates/allium-parser/tests/fixtures/comprehensive-edge-cases.allium exits 1 under the reference
188 compared, 0 differ
negative control: candidate plus one byte, check <corpus>/crates/allium-parser/tests/fixtures/comprehensive-edge-cases.allium: fired (stdout differs)
negative control: candidate forced to exit 0, check <corpus>/crates/allium-parser/tests/fixtures/comprehensive-edge-cases.allium: fired (exit status: reference 1, candidate 0)
```

No row reported a stderr difference. A supplementary run over
`ai_tmp/parity-corpus-plus/` (the 27 files plus three written here under
`alliumpy/xmod/`: `core.allium`, `app/orders.allium` using `../core.allium` as `core`,
and `app/broken_import.allium` using a nonexistent `../missing.allium`) exercises local
resolution in the set (the directory form, and the pair named together in both orders,
which the harness found: `check <corpus>/alliumpy/xmod/app/orders.allium
<corpus>/alliumpy/xmod/core.allium` and the reverse, and the same under `analyse`), out
of the set but on disk (`orders.allium` alone), and broken. Reference against its copy
and against proto-a, both exit 0:

```text
positive control: check <corpus>/alliumpy/xmod/app/broken_import.allium exits 1 under the reference
207 compared, 0 differ
negative control: candidate plus one byte, check <corpus>/alliumpy/xmod/app/broken_import.allium: fired (stdout differs)
negative control: candidate forced to exit 0, check <corpus>/alliumpy/xmod/app/broken_import.allium: fired (exit status: reference 1, candidate 0)
```

**Wheel**: `alliumpy-3.6.1-cp311-abi3-macosx_11_0_arm64.whl`, 649,048 bytes (T00's at
`e0d2201`: 280,203 bytes).

**Per-bump cost.** The tag before `v3.6.1` is `v3.6.0` (`gh api
repos/juxt/allium-tools/tags --paginate --jq '.[].name'`, exit 0, 32 tags). Its three
blobs fetched into `ai_tmp/upstream/prev/` under `set -o pipefail` (each exit 0,
`test -s` passed). Upstream's own diff: `main.rs` +34 −7 (the broken-import
`missing_use_paths` plumbing, which changes two `run_multi_file(...)` lines the
transform rewrites), `test_plan.rs` and `domain_model.rs` unchanged. `vendor_cli.py`
ran unedited on both tags (exit 0 each), so that bump would have been: fetch, run the
script, review a 41-line upstream diff, run `just check` and `just parity`.

#### Step 5: prototype (b), bundle

`ai_tmp/proto-b` at `e0d2201` with uncommitted changes
(`M crates/alliumpy/python/alliumpy/_cli.py`, `?? crates/alliumpy/python/alliumpy/_bin/`);
`just initialize` exit 0; the reference binary copied to
`crates/alliumpy/python/alliumpy/_bin/allium`; `_cli.py`:

```python
# Copyright 2026 Steven Cutting
"""Console entry point: upstream's allium binary, shipped as package data."""

import os
import subprocess
import sys
from importlib.resources import as_file, files


def main() -> int:
    """Become upstream's binary on POSIX; on Windows, run it and return its exit status."""
    name = "allium.exe" if sys.platform == "win32" else "allium"
    with as_file(files("alliumpy") / "_bin" / name) as binary:
        args = [str(binary), *sys.argv[1:]]
        if sys.platform == "win32":
            # Windows has no exec that keeps the console's exit status; designed, not run (S01).
            return subprocess.run(args, check=False).returncode  # noqa: S603  The packaged binary, no shell.
        sys.stdout.flush()
        sys.stderr.flush()
        return os.execv(binary, args)  # noqa: S606  Replaces this process with the packaged binary.
```

`just check` in proto-b exit 0 (`All checks passed and the worktree is unchanged.`);
then `just wheel-smoke` exit 0 rebuilt the wheel, and that wheel was inspected:

```text
$ .pixi/envs/default/bin/python -I -m zipfile -l dist/*.whl | grep -E '_bin|File Name'
File Name                                             Modified             Size
alliumpy/_bin/allium                           1980-01-01 00:00:00      1649616
$ .pixi/envs/default/bin/python -I -c 'import sys, zipfile; i = zipfile.ZipFile(sys.argv[1]).getinfo("alliumpy/_bin/allium"); print(oct(i.external_attr >> 16))' dist/*.whl
0o100755
```

Wheel 909,891 bytes. Parity, candidate `ai_tmp/proto-b/target/wheel-smoke/venv/bin/allium`,
exit 0, with the same four lines as (a): `188 compared, 0 differ`, positive control
`comprehensive-edge-cases.allium`, both negative controls fired, no stderr difference.
The result is trivially exact (candidate and reference are one build behind an `exec`);
it still runs because it proves the shim (argument passing, exit status, the
executable bit surviving the wheel).

The release matrix would add, per target, a `cargo install allium-cli@<pin> --locked`
into the package's `_bin/` before `maturin build`: natively on the macOS and Windows
runners (`allium.exe`), and for musllinux inside maturin-action's container with a musl
target, a second cross-build. This cost is designed, not measured: no matrix was run.

#### Step 7: the measurements behind the rulings

Each binary as its parity run used it: the reference built at step 3, proto-a `e0d2201`
with uncommitted changes (the build its final `just check` left), proto-b `e0d2201` with
uncommitted changes; run from this worktree at `e0d2201` with uncommitted changes (only
`ai_tmp/`), all after checkpoint 2's fixes, in one sitting.

**Pipes.** `uname -s` prints `Darwin`. stdout size of `check <corpus dir>`, quoted per
binary, larger than the 65536-byte pipe buffer, so the corpus itself drives the test
(no widened corpus needed):

```text
ai_tmp/parity-reference/bin/allium   164908
ai_tmp/proto-a/target/wheel-smoke/venv/bin/allium   164908
ai_tmp/proto-b/target/wheel-smoke/venv/bin/allium   164908
```

`bash -c '"$1" check ai_tmp/parity-corpus 2>"$2" | head -c 1 >/dev/null; echo "${PIPESTATUS[0]}"'`,
ten runs per binary; distinct pairs of (exit status, first stderr line):

```text
== parity-reference
  10 101|
== proto-a
  10 101|
== proto-b
  10 101|
```

The first stderr line is empty on every run: the panic message opens with a newline.
Lines 2 and 3, the thread id masked as `<tid>` (it changes on every run):

```text
== parity-reference
  10 thread 'main' (<tid>) panicked at /rustc/58cf8f9c35b355199727627d07ae34a4e2846d67/library/std/src/io/stdio.rs:1168:9:|failed printing to stdout: Broken pipe (os error 32)|
== proto-a
  10 thread '<unnamed>' (<tid>) panicked at crates/alliumpy-core/src/cli/main.rs:311:9:|failed printing to stdout: Broken pipe (os error 32)|
== proto-b
  10 thread 'main' (<tid>) panicked at /rustc/58cf8f9c35b355199727627d07ae34a4e2846d67/library/std/src/io/stdio.rs:1168:9:|failed printing to stdout: Broken pipe (os error 32)|
```

No run printed a Python traceback (`grep -c Traceback` 0 on all 30 stderr files).
`/dev/full`: **not measured here** (Darwin has no `/dev/full`).

**Flush order.** `check does-not-exist.allium <v3-lifecycle.allium>` writes a read
error to stderr and a JSON object to stdout. With both on one file (`>file 2>&1`) the
three outputs were byte-identical (sha-1 `a00675004eac…`, exit 1 each), and on a
pseudo-terminal (`script -q <file> <binary> … </dev/null`, exit 1 each, the command's
own status; 11,648 bytes) byte-identical again (`5035ec2b6b00…`): stderr's line first,
then the JSON. (A first pseudo-terminal rerun inside a loop wrote empty files, sha-1
`da39a3ee…`, because `script` read the loop's stdin; that run is discarded, not
quoted as a match.)

**Exit 2 with empty stdout**, quoted from the final proto-a harness run's row lines:

```text
same    check [reference: exit 2, stdout 0 bytes]
same    analyse [reference: exit 2, stdout 0 bytes]
same    check <empty directory> [reference: exit 2, stdout 0 bytes]
same    analyse <empty directory> [reference: exit 2, stdout 0 bytes]
same    (no arguments) [reference: exit 2, stdout 0 bytes]
same    frobnicate [reference: exit 2, stdout 0 bytes]
same    help frobnicate [reference: exit 2, stdout 0 bytes]
same    parse [reference: exit 2, stdout 0 bytes]
same    parse <corpus>/crates/allium-parser/tests/fixtures/comprehensive-edge-cases.allium <corpus>/extensions/allium/test/fixtures/refactor/extract-literal.input.allium [reference: exit 2, stdout 0 bytes]
same    plan [reference: exit 2, stdout 0 bytes]
same    plan <corpus>/crates/allium-parser/tests/fixtures/comprehensive-edge-cases.allium <corpus>/extensions/allium/test/fixtures/refactor/extract-literal.input.allium [reference: exit 2, stdout 0 bytes]
same    model [reference: exit 2, stdout 0 bytes]
same    model <corpus>/crates/allium-parser/tests/fixtures/comprehensive-edge-cases.allium <corpus>/extensions/allium/test/fixtures/refactor/extract-literal.input.allium [reference: exit 2, stdout 0 bytes]
same    -V [reference: exit 0, stdout 42 bytes]
same    --version [reference: exit 0, stdout 42 bytes]
```

A nonexistent path is not in that set: `check`, `analyse`, `parse`, `plan` and `model`
of a nonexistent file all exit **1** with empty stdout. The harness run against T00's
own console script (this worktree's `target/wheel-smoke/venv/bin/allium`, exit 1)
printed `188 compared, 173 differ`, and its `same` rows were exactly these fifteen:
the thirteen exit-2 rows and `-V`, `--version` (`--version extra` differs: T00
compares the whole argument list). T13's run before the command exists must expect
exactly this set of rows by name; the count of differing rows moves with the corpus,
the set does not.

### Rulings

- **The sdist: keep it.** Under (a) it is complete and builds: `maturin sdist` in
  proto-a (exit 0, 26 entries) holds `alliumpy-3.6.1/Cargo.lock`,
  `alliumpy-3.6.1/crates/alliumpy-core/src/cli.rs`, `…/src/cli/main.rs`,
  `…/src/cli/test_plan.rs`, `…/src/cli/domain_model.rs`, `alliumpy-3.6.1/LICENSE`,
  `alliumpy-3.6.1/LICENSE-allium-tools` and both texts again under
  `crates/alliumpy/`; extracted into a fresh directory, `maturin build --release`
  from it exit 0 (with cargo's registry cache warm, so not an offline proof). Dropping
  it would turn a platform the matrix misses into "no matching distribution" with no
  way in at all; keeping it gives that user a source build that needs a Rust toolchain
  and the network, which T12 documents. Python 3.10 is refused either way
  (`requires-python`). T14 asserts those seven paths, asserts no `_bin/` entry, and
  notes that the sdist omits `tests/fixtures/parity/`, so `cargo test` from it is not
  expected to pass. Under (b) the sdist would carry one platform's binary (proto-b's
  sdist holds `python/alliumpy/_bin/allium`, an arm64 Mach-O, mode `0644`), so (b)
  would have had to drop it.
- **The `--version` suffix (claim 12).** Built from `env!("CARGO_PKG_VERSION")` and the
  literal `(language versions: 1, 2, 3)` in `main.rs`; `allium-parser` exposes neither.
  `ALLIUM_VERSION_STRING` stays a copied literal in `crates/alliumpy-core/src/lib.rs`,
  and the vendored `main.rs` prints that constant, so there is one copy, not two.
  `version-check` compares it, whole, with the smoke venv's `allium --version` (T13
  step 6); `just parity` compares the command with the reference. The transform matches
  upstream's `println!` block exactly, so an upstream change to the suffix stops
  `vendor_cli.py` and cannot be re-vendored silently. Nothing derives one version from
  another (`CONVENTIONS.md` §1 decision 4).
- **Pipes and flushing.** The reference dies by a panic on `EPIPE`: exit 101 and the
  line `failed printing to stdout: Broken pipe (os error 32)` on stderr, on every one of
  ten runs, and the same for both prototypes. Under (a), Python ignores SIGPIPE as Rust
  does, so the vendored write fails with `EPIPE`, the vendored macro panics, `cli::run`
  catches it and returns 101, and the console script exits 101 with no traceback; under
  (b), `execv` keeps the ignored disposition. T13 asserts exit 101, that stderr contains
  that line, and that it contains no `Traceback`; it never asserts the `thread …
  panicked at …` line, whose thread name, location and id differ (stderr, reported
  only). `/dev/full` is not measured here: T13's test carries
  `@pytest.mark.skipif(sys.platform != "linux", reason="/dev/full exists only on Linux; S01 measured on macOS, so the parity CI job on Linux is where this runs")`
  and asserts what the reference does there, recorded by T13 from the first Linux run.
  Flush order, on a file and on a pseudo-terminal, is the reference's byte for byte.
- **The gates under route (a).** Coverage: `src/cli/` is unit-tested to the floor
  (91.36% over the core; 90.95% over the three vendored files alone) by upstream's 140
  tests and the eleven in `cli.rs`; the `coverage` line is unchanged and `CONVENTIONS.md` §7 invariant 6 needs
  no change. The margin is thin (§13 "The small denominator"), under one point for the
  vendored files themselves: one upstream bump that
  adds untested lines to `main.rs` can breach it, and T13's cross-module pair lifts
  `main.rs` above 86.19%. Lints: the lint tables and `clippy.toml` are unchanged; each
  vendored file carries the file-level `#![expect]` block `vendor_cli.py` writes (the
  table above), and `run_os` one `#[expect(clippy::unnecessary_debug_formatting, …)]`;
  the deliberate panics in `cli.rs`'s output macros are invisible to clippy's `panic`
  lint and documented on each macro.
  rustqual: `rustqual.toml` gains one key, `exclude_files` naming the three vendored
  files, because their 59 findings are upstream's shape, refactoring them would end
  the plain re-vendor, and per-finding `qual:allow` exceeds `max_suppression_ratio`.
  `cli.rs` stays measured. Decision 0014 records it, as `rustqual.toml`'s own header
  ("every key that can fail the gate is written here") requires. Formatting:
  `#[rustfmt::skip]` on the three `mod` declarations; `fmt-check` still covers
  `cli.rs`. EditorConfig: `.editorconfig` gains
  `[crates/alliumpy-core/src/cli/{main,test_plan,domain_model}.rs]` with
  `indent_size = unset`, because upstream indents its help text and its tests'
  Allium sources inside string literals by two and seven spaces, and reindenting would
  change the command's stdout; charset, LF, final newline, trailing whitespace and
  spaces-not-tabs stay checked, and `cli.rs`, like any file later added under
  `src/cli/`, stays fully checked. Every other hook,
  typos included, passed over the vendored files and the corpus once staged.
- **What T13 tests beyond the corpus** (each in T13's `test_cli.py`, through
  `ALLIUMPY_SMOKE_BIN`): exit 0 on `tests/fixtures/smoke/ok.allium`, 1 on
  `broken.allium`, 2 with no arguments and on an empty directory; `-V` and `--version`;
  `check <corpus dir> | head -c 1`: exit 101, the `failed printing to stdout: Broken
  pipe (os error 32)` line, no `Traceback`; `/dev/full` on Linux only, as above; flush
  order, `check does-not-exist.allium <file>` on a pseudo-terminal byte-equal to the
  reference's; an argument that is not UTF-8: exit 101, no `Traceback`; stdout closed
  (`>&-`): the reference's exit status (0 for `-V`) and no `Traceback`; SIGINT during a
  blocked read (a FIFO named as the file): killed by the signal at once, no
  `Traceback`; and the fifteen-row set above for the run before the command exists.

### The harness design

T13 inherits this design unchanged; `tests/parity/run.py` is its implementation.

- **Invocation.** `python -I tests/parity/run.py --reference <abs path> --candidate <abs path> --corpus <dir>`.
  Both binaries must be absolute paths (a relative one is refused: `cwd` is the corpus's
  parent, so a relative executable would resolve against the wrong directory), regular
  files, and executable. The candidate is refused if it is the reference by resolved path
  or by inode (`Path.samefile`), so a symlink or a hard link to the reference cannot pass.
- **The reference.** `allium-cli` built from crates.io with `cargo install allium-cli@<pin> --locked --root <root>`,
  the root off `PATH` (`ai_tmp/parity-reference/` here, `.tools/parity/` in T13). Never a
  downloaded release asset.
- **The corpus.** Every `.allium` file in upstream's tree at the pinned tag, fetched one
  `gh api` read per path, each checked against upstream's blob sha with `git hash-object`,
  kept in upstream's directory shape with no edit. The harness discovers files with
  `rglob("*.allium")`, sorted, as POSIX paths relative to the corpus root; any entry
  under the corpus that is not a regular file or directory (a symlink, to a file or to
  a directory, a FIFO, a device) is a harness error, because upstream's directory walk
  would follow it out of the corpus or a read would block with no timeout. The harness never
  imports from, and no Python runs from, the corpus directory. Upstream's tree at `v3.6.1`
  holds no local cross-module import: its three `use` declarations
  (`comprehensive-edge-cases.allium` lines 3 and 4, `language-reference-constructs.allium`
  line 82) are registry coordinates, which upstream keeps out of the check set. The corpus
  is therefore thin on cross-module `use` resolution (`CONVENTIONS.md` §13); T13 adds one
  attributed importing pair under `tests/fixtures/parity/alliumpy/` (the importer in a
  subdirectory, `use`-ing its target by a relative `.allium` path with an alias it
  references). The harness finds such pairs itself (below), so the pair is then compared
  in the directory form, named together in both orders, and as the importer alone.
- **Each run.** One binary, one argument list, `cwd` = the corpus's parent directory,
  never the corpus itself (`CONVENTIONS.md` §11: fetched material is read with tools run
  from outside it), every corpus path relative to that `cwd` and so prefixed with the
  corpus directory's name (`parity-corpus/...` here, `parity/...` in T13); an environment
  built from scratch (`PATH=/usr/bin:/bin`, `TZ=UTC`, `LC_ALL=C`, nothing else); `stdin`
  from `/dev/null`; a 120-second timeout. stdout and stderr are captured as bytes. No row
  passes `.`, so what else sits beside the corpus (`tests/fixtures/smoke/` in T13) is
  never read. The harness reads corpus files as text in one place only: to find each
  `use` declaration of a `"<path>.allium"` string (whitespace, newlines and `--`
  comments may separate the two, as upstream's lexer allows) whose path, resolved
  against the importing file's directory as upstream resolves it, is another corpus
  file; nothing in the corpus is executed or imported.
- **Comparison.** stdout **bytes** and the exit status, exactly. Decoding happens only for
  the displayed diff (`errors="replace"`). stderr bytes are compared and a difference is
  reported on the row (`stderr differs, reported only`) without failing it. Why: invariant
  1 and `CONVENTIONS.md` §9 define parity as stdout and exit status; upstream's stderr
  carries only usage lines, `No .allium files found.`, read errors as `<path>: <OS error>`
  (text from the platform, not from upstream's logic) and, on a failed write, the Rust
  panic message, which names a thread id that changes on every run of the same binary
  (step 7 quotes it), so byte equality of stderr is not a property even the reference
  has. Every stderr difference is still printed on its row, so none is hidden. Any
  exception while running either binary (a timeout, an `OSError` from `exec`) makes the
  row a difference with `could not run: <error>`; nothing is skipped.
- **The matrix**, 5N + 53 + 4P rows for N corpus files and P importing pairs: 188 on the
  27-file corpus, which has no pair. Each file under each of `check`, `analyse`, `parse`,
  `plan`, `model` (5N); under each of `check` and `analyse`, each importing pair named
  together in both orders (4P); then 53 fixed rows: under each of `check` and `analyse`,
  the directory form, the first and last corpus files named together, the directory
  plus an overlapping file, and an absolute file path (8); `check` and `analyse`
  with no path, nonexistent `.allium` paths under `check` and `analyse`, a nonexistent
  non-`.allium` path, an empty directory (a temporary directory outside the corpus,
  passed by absolute path) under `check` and `analyse`, no arguments, `help`, `-h`,
  `--help`, `-V`, `--version`, `--version extra`, an unknown command, `help` of an unknown
  command (16); `help <command>` for each command (5); `<command> --help` and
  `<command> -h` for each (10); `<command> <file> --help` for each, because upstream
  honours `--help` anywhere after the command (5); and for each of `parse`, `plan`,
  `model`: no file, two files, and a nonexistent file (9). Row labels print the corpus
  directory as `<corpus>`, absolute corpus paths as `<absolute corpus>/...` and the empty
  directory as `<empty directory>`, so the output is stable across runs and machines.
- **Positive control,** before any comparison: the reference's `check` on each corpus
  file in sorted order, under the same `cwd` and environment as the matrix, until one
  exits exactly 1 (an error or warning; 2 is "no inputs" and proves nothing). It is named
  in the output. If none does, or the reference cannot run, the harness stops with a
  harness error before comparing anything. The harness never supplies a control itself:
  if no upstream file exits 1, the operator copies this repository's
  `tests/fixtures/smoke/broken.allium` into `<corpus>/alliumpy/broken.allium` with a
  comment attributing it to this repository and reruns (`rglob` finds it, so it joins
  the matrix too); the notes then say the control came from it, T13 commits it under
  `tests/fixtures/parity/alliumpy/`, and Open points records "corpus thin on errors"
  (`CONVENTIONS.md` §13). Here the control is an upstream file
  (`crates/allium-parser/tests/fixtures/comprehensive-edge-cases.allium`), so the
  fallback was not used.
- **Negative control,** after the matrix and before any row, summary or diff is printed,
  on every invocation, with no flag to disable it: two wrapper scripts in a fresh
  temporary directory outside the corpus, one running the candidate and appending one
  byte to its stdout while keeping its exit status, one running the candidate and
  exiting 0. Each reruns `check <positive-control file>` against the reference through
  the same `compare` the matrix uses. The first must be reported as a stdout difference
  and the second as an exit-status difference (the reference exits 1 there); a control
  not reported by the comparator it targets is a harness error, and then no
  `N compared, M differ` line is printed at all.
- **Determinism control,** run by the operator, not by `run.py`: the reference against a
  byte copy of itself at another path must report `0 differ`.
- **Output.** `positive control: ...`, one line per row (`same` or `DIFFER`, the label,
  and in parentheses what differed), `N compared, M differ`, a unified diff of the first
  differing stdout pair, then the two `negative control: ...: fired (...)` lines.
- **Exit status.** 0 when nothing differs and both controls fired; 1 when a row differs;
  2 for a harness error (argument error, missing or non-executable binary, relative path,
  candidate is the reference, nonexistent corpus directory, empty corpus, no positive
  control, a negative control that did not fire, an entry that is not a regular file
  or directory; zero comparisons too, which cannot happen once the corpus is non-empty
  and the fixed rows exist, and is kept because the ticket names it). Distinct messages
  for the nonexistent and the empty corpus. A harness error takes precedence over
  differences.
- **Isolation.** `-I` on every Python invocation; wrapper scripts and the empty directory
  live in `tempfile` directories outside the corpus and are removed afterwards.
- **Lint.** The text passes `ruff check` (`select = ["ALL"]`), `ruff format --check` and
  `mypy --strict` as it stands; each suppression is one rule with its reason on its line
  (`INP001` file-level, `S603`, `BLE001`). T13 adds `tests/parity` to `files =` in
  `mypy.ini` so that `just py-typecheck` checks it routinely (`ruff check .` already
  reaches it).

Control results of every run these notes cite (all with the final `run.py`):

| Run | Commit | Summary | Positive control | Negative controls |
| --- | --- | --- | --- | --- |
| reference vs its copy, twice | `e0d2201` with uncommitted changes | `188 compared, 0 differ` | `comprehensive-edge-cases.allium` exits 1 | both fired |
| reference vs proto-a | proto-a `e0d2201` with uncommitted changes | `188 compared, 0 differ` | same | both fired |
| reference vs proto-b | proto-b `e0d2201` with uncommitted changes | `188 compared, 0 differ` | same | both fired |
| reference vs T00's console script | `e0d2201` | `188 compared, 173 differ` | same | both fired |
| supplementary corpus, reference vs its copy | `e0d2201` with uncommitted changes | `207 compared, 0 differ` | `alliumpy/xmod/app/broken_import.allium` exits 1 | both fired |
| supplementary corpus, reference vs proto-a | proto-a `e0d2201` with uncommitted changes | `207 compared, 0 differ` | same | both fired |

### The harness, verbatim

`ai_tmp/parity/run.py` as it ran for every row above (355 lines, sha-256
`db22c87f84f2aa202eb794e47f7f5afc65e86ffe4af4151baac880de205ae8ae`):

```python
# Copyright 2026 Steven Cutting
# ruff: noqa: INP001  A standalone script run by path with -I, never imported as a package.
"""Compare the wheel's allium command with upstream's, byte for byte."""

import argparse
import difflib
import os
import re
import shlex
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

DIFFERENCES = 1
HARNESS_ERROR = 2
# Upstream's check exits 1 on an error or warning; 2 means no inputs and proves nothing.
REJECTED = 1
TIMEOUT_SECONDS = 120
COMMANDS = ("check", "analyse", "parse", "plan", "model")
SINGLE_FILE_COMMANDS = ("parse", "plan", "model")
# Built from scratch so nothing in the caller's environment reaches either binary.
ENVIRONMENT = {"PATH": "/usr/bin:/bin", "TZ": "UTC", "LC_ALL": "C"}
# A `use` of a local file: the path upstream resolves against the importer's directory.
# Upstream's lexer skips whitespace, newlines and `--` comments between `use` and its string.
LOCAL_USE = re.compile(r'\buse(?:\s|--[^\n]*)*"([^"]+\.allium)"')


class HarnessError(Exception):
    """The harness cannot produce a trustworthy verdict."""


@dataclass(frozen=True)
class Outcome:
    """What one binary did with one argument list."""

    status: int
    stdout: bytes
    stderr: bytes


@dataclass(frozen=True)
class Comparison:
    """The reference's and the candidate's outcomes for one row of the matrix."""

    label: str
    reference: Outcome | None
    candidate: Outcome | None
    error: str | None

    @property
    def differs(self) -> bool:
        """Whether stdout bytes or the exit status differ, or the run failed."""
        if self.reference is None or self.candidate is None:
            return True
        return (
            self.reference.stdout != self.candidate.stdout
            or self.reference.status != self.candidate.status
        )


def check_binary(role: str, path: Path) -> Path:
    """Return a binary's resolved path, or fail closed naming its role."""
    if not path.is_absolute():
        msg = f"{role} must be an absolute path: {path}"
        raise HarnessError(msg)
    if not path.is_file() or not os.access(path, os.X_OK):
        msg = f"{role} is not an executable file: {path}"
        raise HarnessError(msg)
    return path.resolve()


def check_distinct(reference: Path, candidate: Path) -> None:
    """Refuse a candidate that is the reference by resolved path or by inode."""
    if reference == candidate or reference.samefile(candidate):
        msg = f"candidate is the reference: {candidate}"
        raise HarnessError(msg)


def corpus_files(corpus: Path) -> list[str]:
    """Return the corpus's specification files, relative and sorted; fail closed."""
    if not corpus.is_dir():
        msg = f"corpus directory does not exist: {corpus}"
        raise HarnessError(msg)
    files = []
    for path in corpus.rglob("*"):
        relative = path.relative_to(corpus).as_posix()
        # A symlink leads outside the corpus (rglob does not follow one, upstream's walk
        # does); a FIFO or a device blocks with no timeout.
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            msg = f"not a regular file or directory inside the corpus: {relative}"
            raise HarnessError(msg)
        if path.is_file() and path.suffix == ".allium":
            files.append(relative)
    if not files:
        msg = f"empty corpus: no .allium file under {corpus}"
        raise HarnessError(msg)
    return sorted(files)


def import_pairs(corpus: Path, files: list[str]) -> list[tuple[str, str]]:
    """Each (importer, target) where a corpus file `use`s another corpus file, read as text."""
    root = corpus.resolve()
    pairs = set()
    for name in files:
        text = (corpus / name).read_text(encoding="utf-8", errors="replace")
        for use in LOCAL_USE.findall(text):
            target = ((corpus / name).parent / use).resolve()
            if target.is_file() and target.is_relative_to(root) and target != root / name:
                pairs.add((name, target.relative_to(root).as_posix()))
    return sorted(pairs)


def matrix(
    files: list[str], pairs: list[tuple[str, str]], corpus: Path, empty: Path
) -> list[list[str]]:
    """Every argument list both binaries run, in order; T13's README tabulates it."""
    first, last = files[0], files[-1]
    rows = [[command, name] for name in files for command in COMMANDS]
    for command in ("check", "analyse"):
        rows += [
            [command, corpus.name],
            [command, first, last],
            [command, corpus.name, first],
            [command, str(corpus.parent / first)],
        ]
        for importer, target in pairs:
            rows += [[command, importer, target], [command, target, importer]]
    rows += [
        ["check"],
        ["analyse"],
        ["check", "does-not-exist.allium"],
        ["analyse", "does-not-exist.allium"],
        ["check", "does-not-exist.txt"],
        ["check", str(empty)],
        ["analyse", str(empty)],
        [],
        ["help"],
        ["-h"],
        ["--help"],
        ["-V"],
        ["--version"],
        ["--version", "extra"],
        ["frobnicate"],
        ["help", "frobnicate"],
    ]
    rows += [["help", command] for command in COMMANDS]
    rows += [[command, flag] for command in COMMANDS for flag in ("--help", "-h")]
    rows += [[command, first, "--help"] for command in COMMANDS]
    for command in SINGLE_FILE_COMMANDS:
        rows += [[command], [command, first, last], [command, "does-not-exist.allium"]]
    return rows


def placeholder(arg: str, corpus: Path, empty: Path) -> str:
    """One argument as a label shows it, independent of where the corpus lives."""
    if arg == str(empty):
        return "<empty directory>"
    if arg.startswith(f"{corpus}/"):
        return "<absolute corpus>/" + arg.removeprefix(f"{corpus}/")
    if arg == corpus.name:
        return "<corpus>"
    if arg.startswith(f"{corpus.name}/"):
        return "<corpus>/" + arg.removeprefix(f"{corpus.name}/")
    return arg


def label(args: list[str], corpus: Path, empty: Path) -> str:
    """How a row is named in the output, with the corpus and the empty directory as placeholders."""
    shown = [placeholder(arg, corpus, empty) for arg in args]
    return " ".join(shown) if shown else "(no arguments)"


def execute(binary: Path, args: list[str], workdir: Path) -> Outcome:
    """Run one binary from the corpus's parent, never inside it, with no input and a fixed env."""
    completed = subprocess.run(  # noqa: S603  The binary is a validated absolute path; no shell.
        [str(binary), *args],
        cwd=workdir,
        env=ENVIRONMENT,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        timeout=TIMEOUT_SECONDS,
        check=False,
    )
    return Outcome(completed.returncode, completed.stdout, completed.stderr)


def compare(
    reference: Path, candidate: Path, args: list[str], workdir: Path, name: str
) -> Comparison:
    """Run both binaries on one row; any failure to run counts as a difference."""
    try:
        return Comparison(
            name,
            execute(reference, args, workdir),
            execute(candidate, args, workdir),
            None,
        )
    except Exception as error:  # noqa: BLE001  Any failure is reported as a difference, never skipped.
        return Comparison(name, None, None, f"{type(error).__name__}: {error}")


def notes(comparison: Comparison) -> list[str]:
    """What differed in one comparison, in the order the line prints it."""
    ref, cand = comparison.reference, comparison.candidate
    if ref is None or cand is None:
        return [f"could not run: {comparison.error}"]
    found = []
    if ref.stdout != cand.stdout:
        found.append("stdout differs")
    if ref.status != cand.status:
        found.append(f"exit status: reference {ref.status}, candidate {cand.status}")
    if ref.stderr != cand.stderr:
        found.append("stderr differs, reported only")
    return found


def report(comparison: Comparison) -> None:
    """Print one line for one comparison."""
    verdict = "DIFFER" if comparison.differs else "same"
    ref = comparison.reference
    observed = f" [reference: exit {ref.status}, stdout {len(ref.stdout)} bytes]" if ref else ""
    found = notes(comparison)
    suffix = f" ({'; '.join(found)})" if found else ""
    sys.stdout.write(f"{verdict:<8}{comparison.label}{observed}{suffix}\n")


def positive_control(reference: Path, files: list[str], workdir: Path) -> str:
    """The first corpus file the reference's check rejects, observed now; fail closed."""
    for name in files:
        try:
            status = execute(reference, ["check", name], workdir).status
        except (OSError, subprocess.SubprocessError) as error:
            msg = f"positive control: the reference could not run: {error}"
            raise HarnessError(msg) from error
        if status == REJECTED:
            return name
    msg = (
        "positive control: the reference's check exits 1 on no corpus file;"
        " copy tests/fixtures/smoke/broken.allium into <corpus>/alliumpy/ and rerun"
    )
    raise HarnessError(msg)


def show_first_difference(comparisons: list[Comparison]) -> None:
    """Print a unified diff of the first differing stdout pair, decoded for display only."""
    for comparison in comparisons:
        ref, cand = comparison.reference, comparison.candidate
        if ref is None or cand is None or ref.stdout == cand.stdout:
            continue
        diff = difflib.unified_diff(
            ref.stdout.decode(errors="replace").splitlines(keepends=True),
            cand.stdout.decode(errors="replace").splitlines(keepends=True),
            fromfile=f"reference: {comparison.label}",
            tofile=f"candidate: {comparison.label}",
        )
        sys.stdout.writelines(diff)
        return


def wrapper(directory: Path, name: str, candidate: Path, tail: str) -> Path:
    """Write an executable script that runs the candidate, then the given shell lines."""
    path = directory / name
    path.write_text(f'#!/bin/sh\n{shlex.quote(str(candidate))} "$@"\n{tail}', encoding="utf-8")
    path.chmod(0o755)
    return path


def negative_controls(
    reference: Path, candidate: Path, control: str, workdir: Path, name: str
) -> list[str]:
    """Prove the comparison sees a wrong stdout and a wrong exit status; fail closed.

    Returns the lines to print, so that nothing else is printed before both fired.
    """
    fired_lines = []
    with tempfile.TemporaryDirectory() as scratch:
        directory = Path(scratch)
        controls = (
            (
                "candidate plus one byte",
                wrapper(
                    directory, "plus-one-byte", candidate, 'status=$?\nprintf x\nexit "$status"\n'
                ),
                "stdout differs",
            ),
            (
                "candidate forced to exit 0",
                wrapper(directory, "exit-zero", candidate, "exit 0\n"),
                "exit status: ",
            ),
        )
        for title, script, expected in controls:
            comparison = compare(reference, script, ["check", control], workdir, name)
            found = notes(comparison)
            heading = f"negative control: {title}, {comparison.label}"
            if not comparison.differs or not any(note.startswith(expected) for note in found):
                msg = f"{heading}: did not fire ({'; '.join(found) or 'no difference'})"
                raise HarnessError(msg)
            fired = next(note for note in found if note.startswith(expected))
            fired_lines.append(f"{heading}: fired ({fired})\n")
    return fired_lines


def run(reference: Path, candidate: Path, corpus: Path) -> int:
    """Run the matrix, print the result and return the exit status."""
    names = corpus_files(corpus)
    files = [f"{corpus.name}/{name}" for name in names]
    pairs = [
        (f"{corpus.name}/{importer}", f"{corpus.name}/{target}")
        for importer, target in import_pairs(corpus, names)
    ]
    workdir = corpus.parent
    with tempfile.TemporaryDirectory() as scratch:
        empty = Path(scratch)
        control = positive_control(reference, files, workdir)
        control_label = label(["check", control], corpus, empty)
        sys.stdout.write(f"positive control: {control_label} exits 1 under the reference\n")
        comparisons = [
            compare(reference, candidate, args, workdir, label(args, corpus, empty))
            for args in matrix(files, pairs, corpus, empty)
        ]
    if not comparisons:
        msg = "zero comparisons: nothing was compared"
        raise HarnessError(msg)
    fired = negative_controls(reference, candidate, control, workdir, control_label)
    for comparison in comparisons:
        report(comparison)
    differ = sum(comparison.differs for comparison in comparisons)
    sys.stdout.write(f"{len(comparisons)} compared, {differ} differ\n")
    show_first_difference(comparisons)
    sys.stdout.writelines(fired)
    return DIFFERENCES if differ else 0


def main(argv: list[str]) -> int:
    """Run the parity comparison and return the process exit status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--corpus", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        reference = check_binary("reference", args.reference)
        candidate = check_binary("candidate", args.candidate)
        check_distinct(reference, candidate)
        return run(reference, candidate, args.corpus.resolve())
    except HarnessError as error:
        sys.stderr.write(f"parity: {error}\n")
        return HARNESS_ERROR


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

The argument matrix: 5N + 53 + 4P rows for an N-file corpus with P importing pairs,
188 rows here (N = 27, P = 0), 207 on the supplementary corpus (N = 30, P = 1). `F` is
each corpus file, `first` and `last` the first and last in sorted order, `<corpus>` the
corpus directory as a path relative to its parent (the working directory).

| # | Rows | Arguments |
| --- | --- | --- |
| 1 | 5N | `<command> F` for `<command>` in `check`, `analyse`, `parse`, `plan`, `model` |
| 2 | 2 | `check <corpus>`, `analyse <corpus>` |
| 3 | 2 | `check first last`, `analyse first last` |
| 4 | 2 | `check <corpus> first`, `analyse <corpus> first` |
| 5 | 2 | `check <absolute path of first>`, `analyse <absolute path of first>` |
| 5a | 4P | for each corpus file `I` that `use`s another corpus file `T` by a relative `.allium` path: `check I T`, `check T I`, `analyse I T`, `analyse T I` |
| 6 | 2 | `check`, `analyse` (no path) |
| 7 | 3 | `check does-not-exist.allium`, `analyse does-not-exist.allium`, `check does-not-exist.txt` |
| 8 | 2 | `check <empty directory>`, `analyse <empty directory>` (a temporary directory outside the corpus) |
| 9 | 1 | no arguments |
| 10 | 3 | `help`, `-h`, `--help` |
| 11 | 3 | `-V`, `--version`, `--version extra` |
| 12 | 2 | `frobnicate`, `help frobnicate` |
| 13 | 5 | `help <command>` for each command |
| 14 | 10 | `<command> --help`, `<command> -h` for each command |
| 15 | 5 | `<command> first --help` for each command |
| 16 | 9 | `parse`, `plan`, `model`: no file; `first last`; `does-not-exist.allium` |

### Prototype results

| | (a) vendor | (b) bundle |
| --- | --- | --- |
| Summary line | `188 compared, 0 differ` (proto-a `e0d2201` with uncommitted changes); `207 compared, 0 differ` on the supplementary corpus | `188 compared, 0 differ` (proto-b `e0d2201` with uncommitted changes) |
| Controls | both fired on every run | both fired |
| stderr differences | none over the matrix; under `EPIPE` or a non-UTF-8 argument, the panic's thread line | none over the matrix; under `EPIPE`, only the thread id; a traceback with stdout closed |
| Coverage effect | 91.36% over the core with the eleven `cli.rs` tests (78.31% without); 90.95% over the vendored files | none (no Rust) |
| Lint findings | 294 lib sites across 21 lints before `#[expect]`; 41 file-level `#[expect]` lines and one on `run_os` after; EditorConfig's indent size on 28 string-literal lines, lifted for the three files | none |
| rustqual findings | 59 on the vendored files; 0 after `exclude_files` | none |
| Wheel (macOS arm64) | 649,048 bytes | 909,891 bytes |
| Per-bump cost | fetch three files, run `vendor_cli.py` (unedited across `v3.6.0`→`v3.6.1`), review upstream's diff (41 lines that bump), `just check`, `just parity` | rebuild the binary per target; nothing to review |
| `just check` | green in proto-a | green in proto-b |

### Recommendation

| Route | Parity | Per upstream bump | Release matrix | Wheel | Python can call the CLI logic | Blocked on |
| --- | --- | --- | --- | --- | --- | --- |
| (a) vendor | measured: `188 compared, 0 differ` and `207 compared, 0 differ`, controls fired, stderr identical on every row | measured: run `vendor_cli.py` (ran unedited on `v3.6.0` and `v3.6.1`), review upstream's diff (+34 −7 that bump), re-run parity | one build per target, unchanged | measured: one extension module, 649,048 bytes | yes: `alliumpy_core::cli::run`; `_run_cli` in Python, private | nothing |
| (b) bundle | measured: `188 compared, 0 differ`, trivially (one build) | rebuild the binary | asserted, not measured: a second `cargo install` per target, musllinux cross-built in maturin-action's container | measured: extension plus a 1,649,616-byte binary, 909,891 bytes | no | nothing; and the sdist would carry the wrong binary |
| (c) upstream | not built: exact by construction if merged | bump the dependency | one build per target | estimated as (a) | yes | a merge and a release upstream |

**Recommendation: (a) vendor**, confirmed by the evidence. It reached exact parity over
the whole corpus and a cross-module supplement with every control firing and no stderr
difference; it passed this repository's full gate with no change to the floor, the lint
tables or `clippy.toml`, and one stated `rustqual.toml` key; it keeps one build per
target and the smallest wheel; it puts the CLI's logic in the tested core where Python
can reach it later; and a bump is a scripted copy plus a reviewable upstream diff, with
parity as the alarm. (b) proved its shim, but its parity is trivially upstream's, its
release cost is a second cross-build per target, and it cannot keep an sdist. (c) is the
cleanest end state and is drafted below, but it waits on a repository this project does
not control. T13 builds (a); if (c) is merged and released on crates.io on the day T13
opens, it is a separate decision that amends 0014, and the steps below remain the
fallback.

### Drafted decision 0014

````markdown
---
title: "Decision 0014: How the `allium` command gets into the wheel"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_cli_strategy"]
requires: []
---

# Decision 0014: How the `allium` command gets into the wheel

## Context

The wheel's `allium` command must behave exactly as upstream's `allium-cli` at the
pinned version (invariant 1). Upstream ships that behaviour only as a binary crate:
file discovery, the cross-module context, the JSON output, the exit-code policy, `plan`
and `model` live in `crates/allium/src/` with no library target, so bindings over
`allium-parser` alone cannot reproduce `allium check`. Three routes were open: vendor
upstream's CLI modules into the core, bundle upstream's binary as package data behind an
exec shim, or ask upstream to expose a `run` function. S01 built the first two and
measured both with a parity harness against `allium-cli` built from crates.io.

## Decision

Vendor. Upstream's `crates/allium/src/main.rs`, `test_plan.rs` and `domain_model.rs` at
the pinned tag live in `crates/alliumpy-core/src/cli/`, each with a provenance header
and a block of file-level `#[expect]` attributes, transformed mechanically so that
`main` becomes `alliumpy_core::cli::run(args, stdout, stderr) -> i32`: output goes to
the handles, a failed write still panics as upstream's does, and `run` returns 101 for a
panic as upstream's binary exits; `run_os` takes the arguments as the operating system
passed them and returns 101 for one that is not UTF-8, as upstream's `std::env::args`
panics. `--version` prints `ALLIUM_VERSION_STRING`. The bindings expose `_run_cli`,
which writes to the process's own streams; `_cli.py` restores SIGINT's default action
and points a closed standard descriptor at the null device, as Rust's runtime does for
upstream's binary, then passes `sys.argv[1:]` and exits with the status. `serde` and `serde_json` join the core's
dependencies under [decision 0004](0004-dependency-policy.md).

The vendored files keep upstream's formatting (`#[rustfmt::skip]` on their `mod`
declarations), are excluded from rustqual by `exclude_files` in `rustqual.toml`, and
are exempt from EditorConfig's indent-size rule by an `.editorconfig` section, which
also keeps upstream's help text byte for byte: their shape is upstream's, and parity, not the metrics gate, is what holds them. They
stay under the coverage floor and the lint tables; `cli.rs` carries the tests that keep
the floor. The sdist is kept and carries the vendored sources.

## Consequences

The wheel stays one extension module built once per target, and `just parity` proves the
command against the reference over upstream's fixture corpus. Every upstream bump re-runs
the vendoring transform, reviews upstream's diff to the three files and re-runs parity
(T17's runbook); a transform that no longer matches stops rather than producing a partial
copy. The vendored code can drift from upstream only between bumps, and the corpus is the
alarm, so it is only as good as the corpus (`tests/fixtures/parity/README.md` says what it
covers). The coverage margin is thin, and a bump that adds untested upstream lines can
breach the floor. Python can call the CLI's logic through the core later without a second
build.

## What would reopen this

Upstream releasing a library target that exposes `run` on crates.io (then a dependency
replaces the vendored copy); a vendored transform that can no longer be applied
mechanically; or a parity difference that the vendored build cannot reproduce.

## Related pages

- [Dependency policy](0004-dependency-policy.md)
- [The metrics gate](0007-metrics-gate.md)
- [Version tracks upstream](0010-version-tracks-upstream.md)
- [An exact pin on `allium-parser`](0011-exact-pin-on-allium-parser.md)
- [Architecture](../explanation/architecture.md)
````

### Drafted T13 route-specific steps (route (a))

T13 copies these under `### Route-specific steps (from S01, route (a))`. They run after
T13's step 3, so `tests/fixtures/parity/` already holds the corpus.

1. **Dependencies** (`Cargo.toml`, `crates/alliumpy-core/Cargo.toml`, `Cargo.lock`). In
   `[workspace.dependencies]`, after `pyo3`:

   ```toml
   # Caret range; Cargo.lock is the pin (decision 0004). The vendored CLI's
   # test_plan and domain_model derive Serialize (decision 0014).
   serde = { version = "1.0.229", features = ["derive"] }
   # Caret range; Cargo.lock is the pin (decision 0004). The vendored CLI writes
   # its JSON output with it (decision 0014).
   serde_json = "1.0.154"
   ```

   (the versions `Cargo.lock` already holds through `allium-parser`; if they have moved
   by the day, write the locked ones), and under the core's `[dependencies]`:
   `serde = { workspace = true }` and `serde_json = { workspace = true }`. Run
   `cargo update -p serde -p serde_json --offline`. Proof: `git diff Cargo.lock` adds
   exactly `"serde",` and `"serde_json",` to `alliumpy-core`'s dependency list and moves
   no version; `just deny` exit 0.

2. **Vendor** (`crates/alliumpy-core/src/cli/main.rs`, `test_plan.rs`,
   `domain_model.rs`). Fetch the three files at the pin's tag into an empty
   `ai_tmp/upstream/` with S01 step 2's `gh api` lines (network, authorised; under
   `set -o pipefail`, each exit status quoted, `test -s` on each), and check each
   against the tag's tree with `git hash-object`. Save the script below as
   `ai_tmp/vendor_cli.py` and run, from the worktree root,
   `mkdir -p crates/alliumpy-core/src/cli && .pixi/envs/default/bin/python -I ai_tmp/vendor_cli.py v3.6.1 ai_tmp/upstream crates/alliumpy-core/src/cli`
   (the pixi interpreter by path: this runs from the agent's shell, where nothing puts
   `python` on `PATH`).
   Proof: exit 0; `diff ai_tmp/upstream/<file> crates/alliumpy-core/src/cli/<file>`
   counts +79 −65 for `main.rs`, +28 −7 for `test_plan.rs` and +18 −0 for
   `domain_model.rs`, as S01 measured. If the script stops on a count, upstream changed
   a line the transform rewrites: stop and hand back.

   ```python
   # Copyright 2026 Steven Cutting
   """Vendor upstream's allium CLI modules into crates/alliumpy-core/src/cli/ (decision 0014).

   Usage: python -I vendor_cli.py <tag> <dir holding upstream's three files> <dest cli dir>

   Every substitution asserts how many times it matched, so an upstream change to a line
   the transform rewrites stops the script instead of producing a silent partial copy.
   """

   import re
   import sys
   from pathlib import Path

   HEADER = """\
   // Vendored from juxt/allium-tools at {tag}: crates/allium/src/{name}
   // (https://github.com/juxt/allium-tools/blob/{tag}/crates/allium/src/{name}).
   // MIT License, Copyright (c) 2026, as upstream's LICENSE reads at that tag; the full
   // text ships as crates/alliumpy/LICENSE-allium-tools. Changes from upstream are listed in
   // crates/alliumpy-core/src/cli.rs; nothing else differs.
   """
   SAME = "upstream's code, vendored unchanged (decision 0014)"
   HASH = (
       "upstream's hash iteration, vendored unchanged; its output order is proved only as far"
       " as the parity corpus exercises it (decision 0014)"
   )
   PANIC = (
       "upstream panics here, vendored unchanged; cli::run returns 101 for it, as upstream's"
       " binary exits (decision 0014)"
   )
   PUB = "upstream's pub items, vendored unchanged inside a private module (decision 0014)"
   # Per file: (lint, reason, cfg) in order; cfg is "", "test" or "not(test)".
   LINTS = {
       "main.rs": [
           ("clippy::bool_to_int_with_if", SAME, ""),
           ("clippy::cognitive_complexity", SAME, ""),
           ("clippy::disallowed_types", HASH, ""),
           ("clippy::excessive_nesting", SAME, ""),
           ("clippy::iter_over_hash_type", HASH, ""),
           ("clippy::manual_let_else", SAME, ""),
           ("clippy::redundant_closure_for_method_calls", SAME, ""),
           ("clippy::str_to_string", SAME, ""),
           ("clippy::too_many_lines", SAME, ""),
           ("clippy::unnested_or_patterns", SAME, ""),
           ("clippy::unreachable", PANIC, ""),
           ("clippy::unwrap_used", PANIC, ""),
       ],
       "test_plan.rs": [
           ("unreachable_pub", PUB, ""),
           ("clippy::cognitive_complexity", SAME, ""),
           ("clippy::collapsible_if", SAME, ""),
           ("clippy::disallowed_types", HASH, ""),
           ("clippy::doc_markdown", SAME, ""),
           ("clippy::excessive_nesting", SAME, ""),
           ("clippy::if_not_else", SAME, ""),
           ("clippy::map_unwrap_or", SAME, ""),
           ("clippy::missing_const_for_fn", SAME, ""),
           ("clippy::redundant_closure_for_method_calls", SAME, ""),
           ("clippy::str_to_string", SAME, ""),
           ("clippy::too_many_arguments", SAME, ""),
           ("clippy::too_many_lines", SAME, ""),
           ("clippy::uninlined_format_args", SAME, ""),
           ("clippy::wildcard_imports", SAME, "not(test)"),
           ("clippy::assert_is_empty", SAME, "test"),
       ],
       "domain_model.rs": [
           ("unreachable_pub", PUB, ""),
           ("clippy::cognitive_complexity", SAME, ""),
           ("clippy::collapsible_if", SAME, ""),
           ("clippy::doc_markdown", SAME, ""),
           ("clippy::excessive_nesting", SAME, ""),
           ("clippy::map_unwrap_or", SAME, ""),
           ("clippy::missing_const_for_fn", SAME, ""),
           ("clippy::redundant_closure_for_method_calls", SAME, ""),
           ("clippy::str_to_string", SAME, ""),
           ("clippy::too_many_lines", SAME, ""),
           ("clippy::uninlined_format_args", SAME, ""),
           ("clippy::wildcard_imports", SAME, "not(test)"),
           ("clippy::assert_is_empty", SAME, "test"),
       ],
   }
   COMMANDS = ("check", "analyse", "parse", "plan", "model")
   HANDLES = "stdout: &mut dyn Write, stderr: &mut dyn Write"


   def replace(text: str, old: str, new: str, count: int = 1) -> str:
       """Replace exactly `count` occurrences, or stop."""
       found = text.count(old)
       if found != count:
           sys.exit(f"vendor_cli: expected {count} of {old!r}, found {found}")
       return text.replace(old, new)


   def substitute(text: str, pattern: str, new: str, count: int) -> str:
       """Regex-replace exactly `count` matches, or stop."""
       result, found = re.subn(pattern, new, text)
       if found != count:
           sys.exit(f"vendor_cli: expected {count} matches of {pattern!r}, found {found}")
       return result


   def transform_main(s: str) -> str:
       """Upstream's main.rs as alliumpy_core::cli's main module (cli.rs lists each change)."""
       s = replace(
           s, "mod domain_model;\nmod test_plan;\n\n", "use super::{domain_model, test_plan};\n"
       )
       s = replace(s, "use std::process::ExitCode;\n", "use std::io::Write;\n")
       s = replace(
           s,
           "fn main() -> ExitCode {\n    let args: Vec<String> = std::env::args().skip(1).collect();\n\n",
           f"pub(super) fn main(args: &[String], {HANDLES}) -> i32 {{\n",
       )
       s = replace(
           s,
           '            println!(\n                "allium {} (language versions: 1, 2, 3)",\n'
           '                env!("CARGO_PKG_VERSION")\n            );',
           '            println_to!(stdout, "{}", crate::ALLIUM_VERSION_STRING);',
       )
       s = substitute(s, r"\beprintln!\(", "eprintln_to!(stderr, ", 12)
       s = substitute(s, r"\bprintln!\(", "println_to!(stdout, ", 3)
       s = substitute(s, r"\bprint!\(", "print_to!(stdout, ", 4)
       s = substitute(s, r"ExitCode::SUCCESS", "0", 7)
       s = substitute(s, r"ExitCode::from\((\d)\)", r"\1", 10)
       s = substitute(s, r"-> ExitCode", "-> i32", 9)
       s = replace(
           s,
           '"help" => return cmd_help(&args[1..]),',
           '"help" => return cmd_help(&args[1..], stdout, stderr),',
       )
       for name in COMMANDS:
           s = replace(
               s, f'"{name}" => cmd_{name}(rest),', f'"{name}" => cmd_{name}(rest, stdout, stderr),'
           )
           s = replace(
               s,
               f"fn cmd_{name}(args: &[String]) -> i32 {{",
               f"fn cmd_{name}(args: &[String], {HANDLES}) -> i32 {{",
           )
       s = replace(
           s,
           "fn cmd_help(args: &[String]) -> i32 {",
           f"fn cmd_help(args: &[String], {HANDLES}) -> i32 {{",
       )
       for name in ("check", "analyse"):
           s = replace(
               s,
               f'run_multi_file("{name}", args, |',
               f'run_multi_file("{name}", args, stdout, stderr, |',
           )
       for name in ("plan", "model"):
           old = f'run_single_file("allium {name} <file.allium>", args, |'
           s = replace(s, old, old.replace("args, |", "args, stdout, stderr, |"))
       for first in ("command: &str,", "usage: &str,"):
           old = f"    {first}\n    args: &[String],\n"
           s = replace(s, old, old + "    stdout: &mut dyn Write,\n    stderr: &mut dyn Write,\n")
       return s


   def transform_test_plan(s: str) -> str:
       """Upstream's tests read a fixture by its workspace path; read the parity corpus's copy."""
       return replace(
           s,
           '"../allium-parser/tests/fixtures/v3-lifecycle.allium"',
           '"../../tests/fixtures/parity/crates/allium-parser/tests/fixtures/v3-lifecycle.allium"',
           7,
       )


   def attributes(name: str) -> str:
       """The file-level expectations for one vendored file, one lint per line."""
       lines = []
       for lint, reason, cfg in LINTS[name]:
           body = f'expect({lint}, reason = "{reason}")'
           lines.append(f"#![cfg_attr({cfg}, {body})]" if cfg else f"#![{body}]")
       return "\n".join(lines) + "\n"


   def main() -> None:
       """Write the three vendored files."""
       tag, source, dest = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
       transforms = {"main.rs": transform_main, "test_plan.rs": transform_test_plan}
       for name in LINTS:
           text = (source / name).read_text(encoding="utf-8")
           text = transforms.get(name, lambda s: s)(text)
           out = HEADER.format(tag=tag, name=name) + attributes(name) + text
           (dest / name).write_text(out, encoding="utf-8")


   if __name__ == "__main__":
       main()
   ```

3. **The module** (`crates/alliumpy-core/src/cli.rs`, `crates/alliumpy-core/src/lib.rs`).
   In `lib.rs`, after the crate doc line and a blank line, `pub mod cli;`. `cli.rs`,
   whole:

   ```rust
   //! Upstream's `allium` command, vendored from `juxt/allium-tools` at v3.6.1.
   //!
   //! `cli/main.rs`, `cli/test_plan.rs` and `cli/domain_model.rs` are upstream's
   //! `crates/allium/src/` files with a provenance header and a block of file-level
   //! `#![expect]` attributes. `domain_model.rs` is otherwise unchanged;
   //! `test_plan.rs`'s tests read upstream's `v3-lifecycle.allium` from the parity
   //! corpus (`tests/fixtures/parity/`) instead of upstream's workspace path; and
   //! `main.rs` differs only in these ways:
   //!
   //! - `mod domain_model; mod test_plan;` became `use super::{domain_model, test_plan};`.
   //! - `fn main() -> ExitCode` became `main(args, stdout, stderr) -> i32`, and every
   //!   function that prints takes the two handles; `ExitCode::SUCCESS` and
   //!   `ExitCode::from(n)` became `0` and `n`.
   //! - `print!`, `println!` and `eprintln!` became the macros below, which write to
   //!   the handles and panic on a failed write, as upstream's do.
   //! - `--version` prints [`crate::ALLIUM_VERSION_STRING`] instead of building the
   //!   string from `CARGO_PKG_VERSION`.

   use std::ffi::OsString;
   use std::io::Write;
   use std::panic::{self, AssertUnwindSafe};

   /// Upstream's `print!`, on a handle: a failed write panics, as upstream's does.
   macro_rules! print_to {
       ($w:expr, $($arg:tt)*) => {
           if let Err(error) = write!($w, $($arg)*) {
               panic!("failed printing to stdout: {error}")
           }
       };
   }

   /// Upstream's `println!`, on a handle: a failed write panics, as upstream's does.
   macro_rules! println_to {
       ($w:expr, $($arg:tt)*) => {
           if let Err(error) = writeln!($w, $($arg)*) {
               panic!("failed printing to stdout: {error}")
           }
       };
   }

   /// Upstream's `eprintln!`, on a handle: a failed write panics, as upstream's does.
   macro_rules! eprintln_to {
       ($w:expr, $($arg:tt)*) => {
           if let Err(error) = writeln!($w, $($arg)*) {
               panic!("failed printing to stderr: {error}")
           }
       };
   }

   // Upstream's formatting is kept, so that a re-vendor is a plain copy.
   #[rustfmt::skip]
   mod domain_model;
   #[rustfmt::skip]
   mod main;
   #[rustfmt::skip]
   mod test_plan;

   /// The exit status of a Rust program whose `main` panicked, as upstream's does on a
   /// failed write to a closed pipe.
   const PANIC_EXIT_STATUS: i32 = 101;

   /// Run upstream's `allium` command on `args` (without the program name), writing
   /// to `stdout` and `stderr`, and return its exit status.
   ///
   /// A panic in upstream's code, a failed write included, returns 101 as upstream's
   /// binary exits, after the panic hook has reported it.
   ///
   /// ```
   /// let mut out = Vec::new();
   /// let mut err = Vec::new();
   /// let status = alliumpy_core::cli::run(&["--version".into()], &mut out, &mut err);
   /// assert_eq!((status, out), (0, format!("{}\n", alliumpy_core::ALLIUM_VERSION_STRING).into_bytes()));
   /// ```
   pub fn run(args: &[String], stdout: &mut dyn Write, stderr: &mut dyn Write) -> i32 {
       panic::catch_unwind(AssertUnwindSafe(|| main::main(args, stdout, stderr)))
           .unwrap_or(PANIC_EXIT_STATUS)
   }

   /// [`run`] on arguments as the operating system passed them.
   ///
   /// Upstream reads its arguments with `std::env::args`, which panics on one that is
   /// not UTF-8; this writes that panic's message and returns 101, as upstream's binary
   /// exits.
   ///
   /// ```
   /// let mut out = Vec::new();
   /// let status = alliumpy_core::cli::run_os(vec!["-V".into()], &mut out, &mut Vec::new());
   /// assert_eq!(status, 0);
   /// ```
   #[expect(
       clippy::unnecessary_debug_formatting,
       reason = "upstream's panic message prints the argument with Debug"
   )]
   pub fn run_os(args: Vec<OsString>, stdout: &mut dyn Write, stderr: &mut dyn Write) -> i32 {
       match args
           .into_iter()
           .map(OsString::into_string)
           .collect::<Result<Vec<_>, _>>()
       {
           Ok(args) => run(&args, stdout, stderr),
           Err(arg) => {
               // The message is upstream's panic's; a failure to write it changes nothing.
               let _ = writeln!(
                   stderr,
                   "called `Result::unwrap()` on an `Err` value: {arg:?}"
               );
               PANIC_EXIT_STATUS
           }
       }
   }

   #[cfg(test)]
   mod tests {
       use std::io::{self, Write};

       // Expected statuses are the reference `allium-cli` 3.6.1's, observed on the
       // parity corpus (`tests/fixtures/parity/`, upstream's files unedited).
       const CORPUS: &str = "../../tests/fixtures/parity";
       const LIFECYCLE: &str =
           "../../tests/fixtures/parity/crates/allium-parser/tests/fixtures/v3-lifecycle.allium";
       const EDGE_CASES: &str = "../../tests/fixtures/parity/crates/allium-parser/tests/fixtures/comprehensive-edge-cases.allium";

       fn run(args: &[&str]) -> (i32, String, String) {
           let args: Vec<String> = args.iter().map(|&arg| arg.to_owned()).collect();
           let (mut out, mut err) = (Vec::new(), Vec::new());
           let status = super::run(&args, &mut out, &mut err);
           (
               status,
               String::from_utf8(out).unwrap(),
               String::from_utf8(err).unwrap(),
           )
       }

       #[test]
       fn version_prints_the_copied_literal_and_exits_0() {
           for flag in ["-V", "--version"] {
               let expected = format!("{}\n", crate::ALLIUM_VERSION_STRING);
               assert_eq!(run(&[flag]), (0, expected, String::new()));
           }
       }

       #[test]
       fn no_arguments_exit_2_with_usage_on_stderr() {
           let expected = "allium: missing command\nRun `allium --help` for usage.\n";
           assert_eq!(run(&[]), (2, String::new(), expected.to_owned()));
       }

       #[test]
       fn unknown_commands_exit_2_with_nothing_on_stdout() {
           for args in [&["frobnicate"][..], &["help", "frobnicate"]] {
               let (status, out, err) = run(args);
               assert_eq!((status, out.as_str()), (2, ""));
               assert!(err.starts_with("allium: unknown command `frobnicate`\n"));
           }
       }

       #[test]
       fn help_forms_print_help_on_stdout_and_exit_0() {
           for args in [&["help"][..], &["-h"], &["--help"]] {
               let (status, out, _) = run(args);
               assert_eq!(status, 0);
               assert!(out.starts_with("allium - validate, parse and analyse"));
           }
           for command in ["check", "analyse", "parse", "plan", "model"] {
               for args in [
                   &["help", command][..],
                   &[command, "--help"],
                   &[command, "-h"],
               ] {
                   let (status, out, _) = run(args);
                   assert_eq!(status, 0);
                   assert!(out.starts_with(&format!("allium {command} - ")));
               }
           }
       }

       /// The number of `.allium` files under the corpus, walked with an explicit stack.
       fn corpus_files() -> usize {
           let mut pending = vec![std::path::PathBuf::from(CORPUS)];
           let mut count = 0;
           while let Some(dir) = pending.pop() {
               let paths = std::fs::read_dir(dir)
                   .unwrap()
                   .map(|entry| entry.unwrap().path());
               let (dirs, files): (Vec<_>, Vec<_>) = paths.partition(|path| path.is_dir());
               count += files
                   .iter()
                   .filter(|path| path.extension().is_some_and(|ext| ext == "allium"))
                   .count();
               pending.extend(dirs);
           }
           count
       }

       #[test]
       fn check_and_analyse_of_the_corpus_report_every_file_and_exit_1() {
           let files = corpus_files();
           assert!(files > 0);
           for command in ["check", "analyse"] {
               let (status, out, _) = run(&[command, CORPUS]);
               assert_eq!(status, 1);
               let reported = out.matches(&format!("\"command\": \"{command}\"")).count();
               assert_eq!(reported, files);
           }
       }

       #[test]
       fn check_exits_1_on_a_file_with_an_error_or_warning() {
           let (status, out, _) = run(&["check", EDGE_CASES]);
           assert_eq!(status, 1);
           assert!(
               out.contains("\"severity\": \"error\"") || out.contains("\"severity\": \"warning\"")
           );
       }

       #[test]
       fn single_file_commands_exit_0_on_a_file_that_parses() {
           for command in ["parse", "plan", "model"] {
               let (status, out, _) = run(&[command, LIFECYCLE]);
               assert_eq!(status, 0);
               assert!(out.contains("\"diagnostics\""));
           }
       }

       #[test]
       fn missing_inputs_exit_2_and_unreadable_files_exit_1() {
           for command in ["parse", "plan", "model"] {
               assert_eq!(run(&[command]).0, 2);
               assert_eq!(run(&[command, LIFECYCLE, LIFECYCLE]).0, 2);
               assert_eq!(run(&[command, "does-not-exist.allium"]).0, 1);
           }
           assert_eq!(
               run(&["check"]),
               (2, String::new(), "No .allium files found.\n".to_owned())
           );
           assert_eq!(run(&["check", "does-not-exist.allium"]).0, 1);
       }

       struct ClosedPipe;

       impl Write for ClosedPipe {
           fn write(&mut self, _: &[u8]) -> io::Result<usize> {
               Err(io::ErrorKind::BrokenPipe.into())
           }

           fn flush(&mut self) -> io::Result<()> {
               Ok(())
           }
       }

       #[cfg(unix)]
       #[test]
       fn an_argument_that_is_not_utf8_exits_101_as_upstreams_panic_does() {
           use std::os::unix::ffi::OsStringExt;
           let args = vec![
               "check".into(),
               std::ffi::OsString::from_vec(b"\xff.allium".to_vec()),
           ];
           let (mut out, mut err) = (Vec::new(), Vec::new());
           assert_eq!(super::run_os(args, &mut out, &mut err), 101);
           assert_eq!(
               (out, String::from_utf8(err).unwrap()),
               (
                   Vec::new(),
                   "called `Result::unwrap()` on an `Err` value: \"\\xFF.allium\"\n".to_owned()
               )
           );
       }

       #[test]
       fn utf8_arguments_run_the_command() {
           let (mut out, mut err) = (Vec::new(), Vec::new());
           assert_eq!(super::run_os(vec!["-V".into()], &mut out, &mut err), 0);
           assert_eq!(
               out,
               format!("{}\n", crate::ALLIUM_VERSION_STRING).into_bytes()
           );
       }

       #[test]
       fn a_failed_write_exits_101_as_upstreams_panic_does() {
           assert_eq!(
               super::run(&["--version".to_owned()], &mut ClosedPipe, &mut Vec::new()),
               101
           );
       }
   }
   ```

   Proof: `just fmt-check`, `just clippy` (exit 0 with no change to the lint tables or
   `clippy.toml`), `just test` (157 tests at S01: 146 upstream and existing plus eleven in
   `cli.rs`; the corpus count is walked, not written, so T13's added files need no edit),
   `just doc`.

4. **rustqual and EditorConfig** (`rustqual.toml`, `.editorconfig`, both `shared, own
   lines`). In `rustqual.toml`, before `allow_recursion`:

   ```toml
   # Upstream's CLI, vendored unchanged under the core's src/cli/ (decision 0014), is
   # upstream's code, not this repository's: its shape is upstream's to change, and
   # parity, not these metrics, is its gate. cli.rs, this repository's own glue, stays
   # measured. Globs resolve against the target directory, as noted above.
   exclude_files = ["src/cli/main.rs", "src/cli/test_plan.rs", "src/cli/domain_model.rs"]
   ```

   Proof: `just metrics` exit 0, both crates `Quality score: 100.0%`. In
   `.editorconfig`, after the `[*.rs]` section:

   ```ini
   # Upstream's CLI, vendored unchanged under the core's src/cli/ (decision 0014),
   # indents its help text and its tests' Allium sources inside string literals by
   # upstream's amounts; reindenting would change the command's output. Only the
   # indent-size rule is lifted; cli.rs and any other file under src/cli/ stay checked.
   [crates/alliumpy-core/src/cli/{main,test_plan,domain_model}.rs]
   indent_size = unset
   ```

   Proof: with the vendored files staged (`git add`), `just lint` exit 0 with
   `EditorConfig` `Passed`; without the section it fails on the 28 lines S01 quoted.

5. **The binding, the stub and the shim** (`crates/alliumpy/src/lib.rs`,
   `crates/alliumpy/python/alliumpy/_alliumpy.pyi`, `_cli.py`,
   `crates/alliumpy/tests/test_run_cli.py`). In `lib.rs`, `use std::ffi::OsString;` and
   `use std::io::Write;` after the `pyo3` imports, and before the `#[pymodule]`:

   ```rust
   /// Run upstream's `allium` command on the process's own stdout and stderr.
   #[pyfunction(name = "_run_cli")]
   fn run_cli(args: Vec<OsString>) -> i32 {
       let mut stdout = std::io::stdout();
       let status = alliumpy_core::cli::run_os(args, &mut stdout, &mut std::io::stderr());
       // Upstream's binary flushes stdout as it exits and ignores a failure there.
       let _ = stdout.flush();
       status
   }
   ```

   and `module.add_function(wrap_pyfunction!(run_cli, module)?)?;` after `parse`'s. In
   the stub, `"_run_cli"` in `__all__` between `"Diagnostic"` and `"parse"` (pyo3 puts
   it in the runtime `__all__`, so stubtest requires it; ruff's formatter then wraps the
   list one name per line), and at the end:

   ```python
   def _run_cli(args: list[str]) -> int:
       """Run upstream's allium command on the process's stdout and stderr; return its status."""
   ```

   `_cli.py`, whole:

   ```python
   # Copyright 2026 Steven Cutting
   """Console entry point: upstream's allium command, vendored into the extension."""

   import os
   import signal
   import sys

   from ._alliumpy import _run_cli


   def main() -> int:
       """Run upstream's command on this process's arguments and return its exit status."""
       # Upstream's binary dies on SIGINT at once; Python's handler would wait for the
       # command to finish, then print a KeyboardInterrupt traceback.
       signal.signal(signal.SIGINT, signal.SIG_DFL)
       # Rust's runtime points a closed standard descriptor at the null device before
       # upstream's main runs, so its output goes nowhere rather than into a file it opens.
       for fd in (0, 1, 2):
           try:
               os.fstat(fd)
           except OSError:
               null = os.open(os.devnull, os.O_RDWR)
               if null != fd:
                   os.dup2(null, fd)
                   os.close(null)
       status = _run_cli(sys.argv[1:])
       for stream in (sys.stdout, sys.stderr):
           if stream is not None:
               stream.flush()
       return status
   ```

   There is no Windows branch to write under (a): the extension runs in-process on every
   platform, and `signal.SIG_DFL`, `os.fstat`, `os.devnull` and `os.dup2` exist on
   Windows too (designed, not run there). `test_run_cli.py`, whole (the binding's own case; T13's `test_cli.py` stays
   subprocess-only):

   ```python
   # Copyright 2026 Steven Cutting
   """Verify the vendored allium command through the extension, on the process's streams."""

   import pytest
   from alliumpy._alliumpy import ALLIUM_VERSION_STRING, _run_cli


   def test_version_prints_upstreams_string_on_the_process_stdout(
       capfd: pytest.CaptureFixture[str],
   ) -> None:
       """Upstream's --version line reaches file descriptor 1, and the status is 0."""
       assert _run_cli(["--version"]) == 0
       assert capfd.readouterr() == (ALLIUM_VERSION_STRING + "\n", "")


   def test_no_arguments_exit_2_with_upstreams_message_on_stderr(
       capfd: pytest.CaptureFixture[str],
   ) -> None:
       """Upstream's missing-command lines reach file descriptor 2, and the status is 2."""
       assert _run_cli([]) == 2
       assert capfd.readouterr() == ("", "allium: missing command\nRun `allium --help` for usage.\n")
   ```

   Proof: `just py-lint`, `just py-typecheck`, `just py-test` (19 passed at S01),
   `just py-stubtest`, `just wheel-smoke` printing `allium 3.6.1 (language versions: 1, 2, 3)`.

6. **Coverage** (no file). The `coverage` recipe and its floor are unchanged. Proof:
   `just coverage` exit 0, quoted with the per-file table; S01 measured 91.36% over the
   core (`cli/main.rs` 86.19%; the three vendored files 90.95%).

7. **The licence sentence** (`crates/alliumpy/LICENSE-allium-tools`, `shared, own
   lines`): the route sentence reads "The wheel carries upstream's `allium` command
   logic from allium-tools v3.6.1, vendored into the `alliumpy-core` crate
   (`crates/alliumpy-core/src/cli/`), and the source distribution carries the same
   files; the parity fixtures under `tests/fixtures/parity/` are upstream's files at
   the same tag." Proof: `just check-docs` unaffected, `just wheel-smoke` (the text
   ships in `.dist-info/licenses/`).

8. **The gate.** `just check` ends with `All checks passed and the worktree is
   unchanged.`; then T13's step 7 runs `just parity`, which must print `0 differ` with
   both controls fired.

### Drafted upstream pull request

Title: `allium-cli: expose the command as a library function, allium_cli::run`

Body:

```markdown
## What

Adds a library target to `allium-cli` exposing the whole command as one function:

    pub fn run(args: &[String], out: &mut impl Write, err: &mut impl Write) -> i32

`src/main.rs` becomes a call to it:

    fn main() -> std::process::ExitCode {
        let args: Vec<String> = std::env::args().skip(1).collect();
        let code = allium_cli::run(&args, &mut std::io::stdout(), &mut std::io::stderr());
        std::process::ExitCode::from(code as u8)
    }

`src/lib.rs` holds what `main.rs` holds today (the commands, the cross-module context,
the JSON output and the exit-code policy) with `print!`, `println!` and `eprintln!`
writing to `out` and `err`, and each returned `ExitCode` replaced by the `i32` it
carries. `test_plan` and `domain_model` move under the library unchanged. The
`--version` line keeps `env!("CARGO_PKG_VERSION")`, which in a library target is still
`allium-cli`'s version.

## Why

Tools that embed the checker (editor integrations, a Python package that ships the
command in a wheel) today have to copy `main.rs` to reproduce `allium check` on a
multi-file specification, because file discovery and the cross-module context exist
only in the binary. A library target lets them depend on the crate instead.

## No behaviour change

The binary's stdout, stderr and exit codes are unchanged. Evidence: a parity harness
that runs the binary built from this branch against the one built from crates.io at
3.6.1, from the same working directory with a scrubbed environment, over every
`.allium` file in this repository under `check`, `analyse`, `parse`, `plan` and
`model`, the directory forms, help and version flags, no arguments, unknown commands,
missing paths and an empty directory (188 comparisons), comparing stdout byte for
byte and exit codes exactly, with a positive and a negative control on every run.
Result: `188 compared, 0 differ`. A write to a closed pipe still panics and exits 101,
as today.

## Not included

No new dependency, no change to `allium-parser`, no MSRV. A failed write still panics;
returning an error instead would be a behaviour change and is left for a separate
discussion.
```

The harness result line in that body is to be measured on the branch before filing;
nothing is filed by this spike. T13 may take route (c) only if this pull request is
merged and the release is on crates.io on the day T13 opens; the drafted steps for (a)
remain its fallback.

### Review records

#### Checkpoint 1: the harness design and `run.py`, before step 4

Reviewers: Codex CLI 0.163.0, `codex exec -m gpt-6-astra -s read-only -C <worktree> -o ai_tmp/review/S01-1/findings-<lens>.md "<brief>" < /dev/null`, two runs in parallel (conformance, breakage), each exit 0; the model answered a trial prompt first. The brief named the ticket, `CONVENTIONS.md` §9, §11, §12, §13 and §14, the design note, `run.py`, the scratch self-tests, upstream's `main.rs` and the corpus as untrusted data, and the checkpoint's four questions; it carried no conclusion. Triage: two fresh-context Claude Opus 5.5 subagents, one per findings file, writing `ai_tmp/review/S01-1/verdicts-<lens>.md`.

| Finding | Severity (reviewer → triage) | Verdict | Reason | Applied |
| --- | --- | --- | --- | --- |
| conformance F1 = breakage F2: `analyse` never gets two paths, a directory plus a file, or an absolute path | medium → medium (breakage: low) | valid | upstream's `analyse` takes `<path>...` through the same `run_multi_file` | three `analyse` rows; 185 → 188 rows |
| conformance F2: binaries run with `cwd` inside the corpus | medium → low | valid | §11: fetched material is read with tools run from outside it | `cwd` is the corpus's parent; paths carry the corpus name; labels use `<corpus>` |
| conformance F3: the design omits the operator's fallback positive control | low → low | valid | step 3 makes the fallback part of the inherited design | design note gains the procedure; the harness error names it |
| conformance F4: the stderr policy has no stated reason | low → low | valid | step 3: "the notes say why" | design note states why |
| breakage F1: no corpus file resolves a local `use` | high → medium | valid | the Open point gives the pair to T13; neither prototype can drop the logic | design note records the gap and T13's pair; supplementary corpus run (`203 compared, 0 differ` then; 207 on the final harness) |
| breakage F3: `N compared, 0 differ` printed before the negative controls ran | low → low | valid | a quoted summary could look like a pass on a harness error | controls run before any row is printed; two self-tests assert no summary when a control fails |
| conformance note: `mypy.ini` does not list `tests/parity` | not counted | handed back | outside this ticket's files | T13 (already in its Files touched) |

Seven valid, none invalid. With breakage F1 at medium after triage, no valid finding was high and no second round ran (Deviations). Re-run after the fixes, at `e0d2201` with uncommitted changes: the self-tests (`19 passed`, then `20 passed` after the later row annotation), `ruff check`, `ruff format --check` and `mypy --strict` on `run.py` (exit 0 each), and the determinism control twice (`188 compared, 0 differ`, both controls fired, outputs byte-identical).

#### Checkpoint 2: the recommendation, the evidence and the two drafts, before the status

Reviewers: Codex CLI 0.163.0 with `-m gpt-6-astra -s read-only`, two runs in parallel (conformance, breakage), each exit 0. The brief named the ticket and its hand-back notes as the artefact, `CONVENTIONS.md` §1, §4, §7, §8, §9, §11, §12, §13 and §14, T13's ticket, the gate configuration files, the stub record, the raw logs, both prototype worktrees, the harness and the vendoring script, with upstream's files as untrusted data, and step 8's six questions. Triage: two fresh-context Claude Opus 5.5 subagents, one per findings file, writing `ai_tmp/review/S01-2/verdicts-<lens>.md`; the breakage triage reproduced F1 in proto-a (staged its files, ran `just lint`, exit 1, then `git reset -q`).

| Finding | Severity (reviewer → triage) | Verdict | Reason | Applied |
| --- | --- | --- | --- | --- |
| breakage F1: EditorConfig fails on the vendored files once tracked; the hook pass had read them untracked | high → high | valid | `editorconfig-checker` reads tracked files only; 28 lines indented inside string literals fail the 4-space rule | `.editorconfig` section in route step 4, the gate ruling and decision 0014; proto-a re-run staged, `just check` green |
| conformance F1 = breakage F2: route step 2 calls a bare `python` | medium → medium | valid | outside a recipe nothing puts `python` on `PATH` | `.pixi/envs/default/bin/python` |
| breakage F3: no row names an importer with its target | medium → medium | valid | the two-file rows take the first and last corpus files | `run.py` finds local import pairs and compares them named together in both orders (test-first); every run rerun; supplementary corpus 207 rows. Triage proposed T13 adding the rows by hand; a harness change keeps T13's copy verbatim |
| conformance F2: T13's Files touched lacks `rustqual.toml` and `test_run_cli.py` | medium → low | valid | §11 requires each shared file listed; T13 cannot edit its own table | handed back to the maintainer as rows amending T13, with `.editorconfig` and 0007 |
| conformance F3: step 7's measurements carry no commit heading, and proto-a's ran before its final build | low → medium | valid | §11: a stale quote is rerun and replaced | pipes, flush and pseudo-terminal rerun on the final builds; results unchanged; heading added |

Five distinct findings (six reported), all valid. Re-run after the fixes, at `e0d2201` with uncommitted changes: self-tests `21 passed` (23 after the second round); `ruff check`, `ruff format --check`, `mypy --strict` on `run.py`, exit 0 each; every harness run in the control table; step 7's measurements; `just check` in proto-a with its files staged, exit 0. Because F1 was valid and high, a second round reviewed the fix diff (below).

#### Checkpoint 2, second round: the fix diff

Reviewers: the same harness and model, two runs in parallel (conformance, breakage) over `ai_tmp/review/S01-2/fix-diff.txt` (the ticket before and after the first round's fixes), proto-a's staged diff, the self-tests and the rerun logs, each exit 0, writing `findings-<lens>-2.md`. Triage: one fresh-context Claude Opus 5.5 subagent, `verdicts-2.md`.

| Finding | Severity (reviewer → triage) | Verdict | Reason | Applied |
| --- | --- | --- | --- | --- |
| conformance R1 = breakage R3: `[crates/alliumpy-core/src/cli/*.rs]` exempts any later file there, while the ruling names three | low → low | valid | a helper added under `src/cli/` would lose the indent check silently | the section names the three files with a brace list; proto-a `just check` green again |
| conformance R2 = breakage R2: import discovery reads a symlinked or special corpus entry before any check | medium → low | valid | it reads outside the corpus or blocks with no timeout | `corpus_files` fails closed on any entry that is not a regular file inside the corpus (test-first) |
| breakage R1: a `use` split from its string by a comment or newline is missed | medium → low | valid | upstream's lexer skips whitespace, newlines and `--` comments between tokens | `LOCAL_USE` follows that rule (test-first; the first version of the test passed for the wrong reason and was corrected to assert the reverse-order row) |

Three distinct findings, all valid, none high. §14 allows two rounds, so this was the last; nothing is left open from it. Re-run after the fixes, at `e0d2201` with uncommitted changes (`run.py` sha-256 `f81b2f78…`): self-tests `23 passed`; `ruff check`, `ruff format --check`, `mypy --strict` exit 0 each; proto-a `just check` with its 41 changes staged, exit 0 (`EditorConfig` `Passed`); every harness run in the control table (the same summaries: 188 and 207 rows, both controls fired on each, no stderr difference, the T00 set unchanged); step 7's measurements (the same results).

#### Code review before the commit

The `code-review` skill at medium effort over the diff (this file), after checkpoint 2. Each finding checked by the executing agent against the code or by measurement:

| Finding | Verdict | Applied |
| --- | --- | --- |
| A non-UTF-8 argument: upstream exits 101 (a panic in `std::env::args`), proto-a printed a `UnicodeEncodeError` traceback and exited 1 | valid, measured | `cli::run_os` and `_run_cli(Vec<OsString>)`, test-first (two `cli.rs` tests); re-measured: 101 |
| A closed stdout: `sys.stdout` is `None`, so `_cli.py`'s flush raised `AttributeError` | valid, measured (proto-b too) | closed fd 0–2 pointed at the null device, as Rust's runtime does; only existing streams flushed; re-measured: the reference's status, empty stderr |
| SIGINT: the in-process command ran on, then a `KeyboardInterrupt` traceback | valid, measured | `signal.SIG_DFL` before the call; re-measured: −2, empty stderr |
| `rglob` does not enter a symlinked directory, which upstream's walk follows | valid | every entry under the corpus must be a regular file or directory (test-first) |
| The design counted 17 fixed rows where there are 16 | valid | corrected; 8 + 16 + 5 + 10 + 5 + 9 = 53 |
| "`src/cli/` alone" included `cli.rs` | valid | the vendored files alone: 90.95% |
| The `panic!` in `cli.rs`'s output macros is invisible to clippy's `panic` lint, so no `#[expect]` records it | valid in fact; an `#[expect]` would be unfulfilled | stated in the gate ruling; each macro's doc comment already says it panics as upstream does |
| `vendor_cli.py` lives in `ai_tmp/`, so the committed files have no committed generator | a choice, not a defect | handed to the maintainer and T17 |
| rustqual's 70 annotations against its summary's 59 findings | valid | both figures stated, unreconciled; the suppression-ratio argument holds under either |
| The zero-comparisons guard cannot fire; `second` against the docs' `last` | valid | guard kept (the ticket names that failure) and the design says it cannot fire; `second` renamed `last` |

Re-run after the fixes: self-tests `24 passed`; `ruff check`, `ruff format --check`, `mypy --strict` on `run.py` (sha-256 `db22c87f…`) exit 0 each; proto-a `just check` with its changes staged, exit 0 (157 tests, 91.36%); every harness run and step 7 measurement (same results); the three edges (above).

### Handed back

- **To the maintainer.** No `CONVENTIONS.md` change is needed: the floor stays as §7
  invariant 6 states it, because the core is unit-tested to 91.36% (the vendored files to
  90.95%); the lint
  tables and `clippy.toml` are unchanged. Two gate configuration changes are stated by
  the gate ruling with their reasons: `rustqual.toml` gains `exclude_files` for the
  three vendored files, and `.editorconfig` lifts `indent_size` for the same three.
  T13's own agent may change only its ticket's `status:` and hand-back notes, so, at the
  maintainer's direction, this ticket's pull request amends
  `tickets/T13-cli-in-the-wheel.md`'s Files touched with these rows:

  | Path | Class | Content |
  | --- | --- | --- |
  | `rustqual.toml` | shared, own lines | `exclude_files` for the three vendored files (S01 route step 4; decision 0014) |
  | `.editorconfig` | shared, own lines | `indent_size = unset` for the three vendored files (S01 route step 4; decision 0014) |
  | `crates/alliumpy/tests/test_run_cli.py` | new | the `_run_cli` binding's own pytest case (S01 route step 5) |
  | `docs/decisions/0007-metrics-gate.md` | shared, own lines | one line pointing to 0014's `exclude_files` |

  The same amendment names that content in T13's steps 4 (the two configuration sections
  and `test_run_cli.py` among what the route's steps end with), 5 (the three edges under
  "Rulings", with the SIGINT case's timing as S01 measured it) and 9 (0007's line), adds
  the three edges to the `test_cli.py` row, names the new `src/cli.rs` and `src/cli/`
  files in the `crates/alliumpy-core/**` row, and fixes two lines in T13's Verification
  block that called bare `python` from the agent's shell (the empty-corpus harness run
  and the `env -u ALLIUMPY_SMOKE_BIN` pytest line): they now name
  `.pixi/envs/default/bin/python`, as S01's Verification block does. One question is the
  maintainer's: whether `vendor_cli.py`, which generates the committed `src/cli/` files,
  is committed by T13 (as `scripts/vendor_cli.py`, which `ruff` and `mypy` would then
  gate) rather than left to T17's runbook; S01 drafts it as a scratch script in
  `ai_tmp/` and hands the choice to T17.
- **To T13.** The drafted steps above. Its Files touched holds the rows under "To the
  maintainer" (`test_run_cli.py` is separate from `test_cli.py` because T13's
  `test_cli.py` imports nothing from `alliumpy`). Its corpus gains the attributed
  cross-module pair the design names; if T13 also adds a broken-import file there,
  `alliumpy/` sorts before `crates/` and becomes the named positive control (S01's
  supplementary run named `alliumpy/xmod/app/broken_import.allium`), so T13's quoted
  control line changes with it. `mypy.ini` gains `tests/parity` (already in T13's
  Files touched). The fifteen-row set for its step 3 run is quoted under step 7 above.
  The harness finds the pair itself and compares it named together in both orders,
  so `tests/parity/run.py` stays a verbatim copy; T13's row count becomes 5N + 53 + 4P.
  The pipe expectations are exit 101 and the `failed printing…` line, never the
  `thread …` line. Its `test_cli.py` adds the three edges under "Rulings": an argument
  that is not UTF-8, a closed stdout, SIGINT during a blocked read.
- **To T14.** Keep the sdist; assert the seven paths under "Rulings", no `_bin/`
  entry, and that `tests/fixtures/parity/` is absent by design. Windows needs no shim
  branch under (a); the rehearsal smoke still proves the `.exe` launcher's exit-code
  propagation (§12 claim 18).
- **To T17.** The upstream-bump runbook under (a): fetch the three files at the new
  tag, run `vendor_cli.py` (its counts encode the pinned tag's shape; a stop means
  upstream changed a rewritten line and the transform must be updated by hand and
  reviewed), review upstream's diff, run `just check` and `just parity`. The script's
  text is in route step 2; committing it as `scripts/vendor_cli.py` with a recipe is
  T17's call. The reference builds with upstream's `Cargo.lock` (`serde_json 1.0.149`)
  and the wheel with this repository's (`1.0.154`): parity held, but a `serde` or
  `serde_json` bump in this repository's lock changes the vendored command's
  dependencies and is a reason to run `just parity`.

### Deviations

- The branch is `ticket/S01-cli-strategy-spike`, Supacode's name for the worktree; the
  ticket's `branch:` field says `ticket/s01-cli-strategy-spike`. Kept rather than
  renaming a branch a tool created.
- §14 Phase 2 asks for separate triage subagents per finding; checkpoint 1 used two
  (one per reviewer's findings file), each a fresh-context Claude Opus 5.5 subagent.
  Phase 3 asks the triage subagents to apply the fixes; the executing agent applied
  them, one at a time, after both verdict files were written.
- Checkpoint 2's second round used one triage subagent for its three distinct findings.
- Breakage F1 at checkpoint 1 was rated high by the reviewer and medium by triage (the
  ticket's Open points already give the cross-module pair to T13, and neither prototype
  can drop upstream's resolution logic); the executing agent confirmed medium, so no
  second round ran for it. The supplementary corpus run was added in response.
- After checkpoint 1, `run.py` gained the reference's exit status and stdout size on
  each row line (test-first, one self-test), so that step 7's exit-2 set could be quoted
  from harness output; after checkpoint 2 it gained the importing-pair rows, and after
  the second round the regular-file check and the lexer-aware `use` pattern (each
  test-first), none of which adds a row on the 27-file corpus. Every harness run and every
  step 7 measurement these notes cite was rerun on that final text and the final
  prototype builds, in one sitting.
- In proto-a, `cargo clippy … --message-format=json` and `cargo fmt --all` were run
  directly, the first to tabulate lints per file, the second to format `cli.rs`; every
  gate result quoted is the `just` recipe's.
- After checkpoint 2's two rounds, a code review of the diff (the `code-review` skill,
  medium effort) found three behaviours outside the corpus where proto-a differed from
  the reference (an argument that is not UTF-8, a closed stdout, SIGINT) and a harness
  gap (a symlinked corpus directory), all fixed test-first and measured, plus wording
  errors fixed in these notes. §14 allows two adversarial rounds, so these fixes were
  not reviewed adversarially again; the review record lists them.
- proto-a's changes were staged (`git add -A`) on its scratch branch so that the hooks
  read the vendored files; nothing was committed there.
- One `cat`/`wc` read ran with `ai_tmp/upstream/` as the working directory; nothing was
  executed from it.
- The `/dev/full` case is not measured (macOS).
- After the pull request opened, the maintainer directed that it also amend
  `tickets/T13-cli-in-the-wheel.md` (the four Files touched rows and the edits under
  "Handed back"), rather than a separate pull request to `main`; this ticket's Files
  touched, Goal and `git status --porcelain` criterion name only this file. The
  amendment changes ticket text only, so the Verification block below was not rerun (the
  prototype worktrees were already removed); `just check` was rerun on the amended tree
  and is quoted at the end of Verification, headed by that state. A two-lens review of
  the amendment (one finder per lens, two skeptics per finding) found two valid
  findings, one medium and one low, both fixed: this bullet claimed a quote that did not
  yet exist, and T13 step 5 did not say how S01 timed the SIGINT case.

### Open points settled

- **stderr parity.** Not required. No row of any run showed a stderr difference for
  either prototype; the one known difference, under `EPIPE`, is the panic's thread
  name, location and id, which change between runs of the reference itself. T13
  compares stderr as reported, not failing.
- **Cross-module `use` across directories.** Upstream's tree at `v3.6.1` holds none
  (its three `use` lines are registry coordinates), so the corpus is thin there. S01's
  supplementary pair passed (`207 compared, 0 differ`, the pair named together in both
  orders among the rows); T13 commits one attributed pair under
  `tests/fixtures/parity/alliumpy/`.
- **The `--version` literal.** `allium-parser` does not expose the language-version
  list. The core's `ALLIUM_VERSION_STRING` is the one copy; the vendored `main.rs`
  prints it. `version-check` compares it with the smoke venv's output and `just parity`
  with the reference.

### Open points remaining

- The corpus is thin on modules with two or more entities carrying `when`-qualified
  fields, the one path where `test_plan.rs` iterates a `HashMap` into its output; the
  determinism control cannot see an order dependence there until the corpus has one.

### Verification

The ticket's Verification block, at `e0d2201` with uncommitted changes (this file only),
run under `bash` from the worktree root after every fix above; the two harness runs'
output went to logs, whose summary and control lines follow:

```text
      27 ai_tmp/upstream/allium-files.txt
allium
allium 3.6.1 (language versions: 1, 2, 3)
exit 0
exit 0
exit 0
parity: empty corpus: no .allium file under /Users/scutting/.supacode/repos/alliumpy/ticket/S01-cli-strategy-spike/ai_tmp/parity-corpus-empty
exit 2
1
exit 0
 M tickets/S01-cli-strategy-spike.md
```

The candidate test printed nothing (proto-a's `allium` exists). Reference against its
copy, exit 0, and against proto-a (`$PROTO=ai_tmp/proto-a`), exit 0, each:

```text
positive control: check <corpus>/crates/allium-parser/tests/fixtures/comprehensive-edge-cases.allium exits 1 under the reference
188 compared, 0 differ
negative control: candidate plus one byte, check <corpus>/crates/allium-parser/tests/fixtures/comprehensive-edge-cases.allium: fired (stdout differs)
negative control: candidate forced to exit 0, check <corpus>/crates/allium-parser/tests/fixtures/comprehensive-edge-cases.allium: fired (exit status: reference 1, candidate 0)
```

`just --evaluate PATH` is one line (`grep -c .` printed 1) and does not name
`parity-reference`. `just check`, last line:

```text
All checks passed and the worktree is unchanged.
```

After the T13 amendment (Deviations), at `fdf12f4` with uncommitted changes (this file
and `tickets/T13-cli-in-the-wheel.md`), `git status --short`, then `just check`'s last
line:

```text
 M tickets/S01-cli-strategy-spike.md
 M tickets/T13-cli-in-the-wheel.md
All checks passed and the worktree is unchanged.
```

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
