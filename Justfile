set positional-arguments := true
set shell := ["sh", "-eu", "-c"]

# The dev shell flake.nix defines, pinned by flake.lock, owns the compiler, Python and
# every tool a recipe or hook calls (decision 0018); this file adds nothing to PATH.
# Outside that shell a recipe would run whatever the machine happens to have, so every
# run refuses first. From a shell that is not inside it, run
# `nix develop --command just <recipe>`. The shell also exports PYO3_PYTHON, so every
# cargo invocation compiles the bindings against the flake's Python.
export ALLIUMPY_DEV_SHELL := if env("ALLIUMPY_DEV_SHELL", "") == "" { error("not in the dev shell: run `nix develop`, or `nix develop --command just <recipe>` (docs/how-to/develop-locally.md)") } else { "1" }

# Every tool a gate or hook calls by name, beside the four the toolchain provides.
# check-toolchain refuses any of them that resolves outside the Nix store.
gate_tools := "just prek git python uv maturin ruff mypy pytest taplo rustqual nixfmt cargo-nextest cargo-llvm-cov cargo-deny cargo-insta cargo-hack cargo-shear typos lychee shellcheck actionlint markdownlint-cli2 editorconfig-checker ripsecrets bg-project-check bg-validate-docs bg-validate-agents bg-ripsecrets"

# The throwaway venv py-develop builds the extension into, on the shell's interpreter.
py_env := justfile_directory() / "target" / "py-env"

# Line-coverage floor over crates/alliumpy-core/src/**. Lower the complexity, not the
# number.
coverage_floor := "90"

default:
    @just --list

# ------------------------------------------------------------------ setup ---

# One explicit first-run command. Never stages, commits, tags, or pushes.
initialize:
    sh scripts/initialize.sh

# Gate 1. Nothing outside the dev shell honours rust-toolchain.toml or flake.lock, so
# before anything builds this proves three things. The shell is the one the committed
# flake.nix, flake.lock, nix/ and rust-toolchain.toml produce: the shell exports a
# digest of those files and the recipe recomputes it from the worktree, so a shell
# entered before a pull, a lock or an edit is refused. cargo, rustc, rustfmt and clippy
# resolve inside the flake's toolchain, and every other tool a gate calls resolves in one
# of the shell's own packages, so a rustup proxy in ~/.cargo/bin, a Homebrew cargo, a uv
# in ~/.local/bin or a tool from another Nix shell is refused by path, wherever it sits
# on PATH. And rustc and cargo report
# exactly the channel rust-toolchain.toml pins.
check-toolchain:
    #!/bin/sh
    set -eu
    fail() { printf 'check-toolchain: %s\n' "$1" >&2; exit 2; }
    [ -n "${ALLIUMPY_ENV_FILES:-}" ] && [ -n "${ALLIUMPY_TOOL_PATH:-}" ] || fail 'not in the dev shell: ALLIUMPY_DEV_SHELL is set, but the variables the shell exports are not; run nix develop'
    for f in $ALLIUMPY_ENV_FILES; do [ -f "$f" ] || fail "$f is missing; the dev shell was built from it"; done
    have=$(for f in $ALLIUMPY_ENV_FILES; do sha256sum "$f" | cut -d' ' -f1; done | tr -d '\n' | sha256sum | cut -d' ' -f1)
    [ "$have" = "${ALLIUMPY_ENV_FINGERPRINT:-}" ] || fail 'the dev shell is stale: flake.nix, flake.lock, nix/ or rust-toolchain.toml changed since it was entered; leave it and run nix develop again'
    for tool in cargo rustc rustfmt cargo-clippy; do
        at=$(command -v "$tool") || fail "$tool is not on PATH"
        case "$at" in "$ALLIUMPY_RUST_TOOLCHAIN"/bin/*) ;; *) fail "$tool resolves to $at, not the flake's toolchain";; esac
    done
    for tool in {{ gate_tools }}; do
        at=$(command -v "$tool") || fail "$tool is not on PATH"
        case ":$ALLIUMPY_TOOL_PATH:" in *":${at%/*}:"*) ;; *) fail "$tool resolves to $at, not the dev shell";; esac
    done
    pin=$(sed -n 's/^channel = "\(.*\)"$/\1/p' rust-toolchain.toml)
    [ -n "$pin" ] || fail 'rust-toolchain.toml names no channel'
    for tool in rustc cargo; do
        got=$("$tool" --version | cut -d' ' -f2)
        [ "$got" = "$pin" ] || fail "$tool is $got, not the pinned $pin"
    done
    rustc --version --verbose | sed -n -e '1p' -e '/^host:/p'

# What Cargo.lock and fuzz/Cargo.lock name into the cargo cache, and the dev shell as a
# GC root under the gitignored .nix/, so that a store garbage collection keeps it and
# the flake's inputs, and re-entering the shell stays offline. Network on a cold cache.
# Never rewrites a lockfile.
sync:
    cargo fetch --locked
    cargo fetch --locked --manifest-path fuzz/Cargo.toml
    nix build --no-update-lock-file --out-link .nix/dev-shell .#dev-shell

# nix flake lock adds an input flake.nix newly names and moves no other. Leave the shell
# and enter it again afterwards: check-toolchain refuses the stale one.
lock:
    cargo update --workspace
    cargo update --workspace --manifest-path fuzz/Cargo.toml
    nix flake lock

# Every input to the head of the ref flake.nix names: nixpkgs and rust-overlay move,
# and with nixpkgs every tool; the checkers stay on their tag.
lock-upgrade:
    cargo update
    cargo update --manifest-path fuzz/Cargo.toml
    nix flake update

# Offline, like every gate recipe: a cold Cargo cache fails rather than fetching the
# registry index (`just sync` fills it). --no-update-lock-file makes a flake.lock that
# disagrees with flake.nix (an input added, removed or pointed elsewhere) an error
# instead of a rewrite; --offline keeps it from fetching. It checks the lock's shape, not
# its hashes: those are checked when the shell is built from it.
lock-check:
    cargo update --workspace --locked --offline
    cargo update --workspace --locked --offline --manifest-path fuzz/Cargo.toml
    nix flake metadata --no-update-lock-file --offline . >/dev/null

# The pre-commit hook: a committed shim that names no store path, so that a moved
# flake.lock never leaves a dangling hook behind. It runs prek in the dev shell, entering
# it when the commit comes from outside. Every hook runs a tool the shell provides, so
# nothing is cloned or built here and the recipe is offline.
install-hooks:
    git rev-parse --is-inside-work-tree >/dev/null
    install -m 0755 scripts/pre-commit-hook.sh "$(git rev-parse --git-path hooks/pre-commit)"

# ---------------------------------------------------------------- develop ---

# Benchmarks, by hand: timings measure the machine and its load as much as the
# code, so never a gate and never in CI. Bench targets only: without --bench '*'
# cargo also runs every unit test in bench mode, as ignored. just clippy already
# compiles the benches, so a bench that stops building fails the gate.
bench *args:
    cargo bench --workspace --all-features --locked --bench '*' "$@"

# Fuzzing, by hand: nondeterministic, so never a gate. On the pinned stable
# toolchain without a sanitizer: AddressSanitizer needs nightly, and every crate
# forbids unsafe code. cargo-fuzz takes no --locked and would rewrite a stale
# fuzz/Cargo.lock, so the first line refuses one offline; `cargo fetch` would be
# a network command, and this is not a network recipe (`just sync` fills the
# cache). CARGO_NET_OFFLINE keeps cargo-fuzz's own build offline too. --target
# because cargo-fuzz defaults to the triple it was built for, which need not be
# the host's. seconds bounds the fuzzing, not the build.
fuzz target seconds="300":
    cargo update --workspace --locked --offline --manifest-path fuzz/Cargo.toml
    CARGO_NET_OFFLINE=true cargo fuzz run --sanitizer none --target "$(rustc -vV | sed -n 's/^host: //p')" "$1" -- -max_total_time="$2"

# The fuzz crate compiles on the pinned stable, without running it. The weekly
# job would otherwise be the only thing that notices a fuzz target that no
# longer builds, and weekly jobs rot. Not in check's recipe list: clippy
# already lints the crate every run; this is the one line ci.yml runs so a
# broken target names itself in the step list. cargo-fuzz takes no --locked
# and would rewrite a stale fuzz/Cargo.lock, so the offline lock guard runs first,
# and CARGO_NET_OFFLINE keeps the build itself offline, as in fuzz.
fuzz-build:
    cargo update --workspace --locked --offline --manifest-path fuzz/Cargo.toml
    CARGO_NET_OFFLINE=true cargo fuzz build --sanitizer none --target "$(rustc -vV | sed -n 's/^host: //p')"

build:
    cargo build --workspace --all-features --locked

# The cdylib test binary needs libpython; its behaviour tests are Python tests.
# nextest runs the unit and integration tests; it cannot run doctests, so those
# follow through cargo test. INSTA_UPDATE=no makes a mismatch fail without a
# pending file, which would trip the gate's worktree check.
test:
    INSTA_UPDATE=no cargo nextest run --workspace --exclude alliumpy --all-features --locked
    cargo test --doc --workspace --exclude alliumpy --all-features --locked

test-doc:
    cargo test --doc --workspace --exclude alliumpy --all-features --locked

# Gate 22: snapshots match, and every .snap file is referenced by a test.
# Run the whole suite so the orphan check sees every reference. --check and
# INSTA_UPDATE=no fail mismatches without writing pending files.
# cargo-insta forwards trailing options as test arguments, so nextest
# rejects --locked. Check the locks first, offline, before cargo-insta runs.
# Doctests already have their own gate; disabling its extra run avoids a warning.
snapshots-check: lock-check
    INSTA_UPDATE=no CARGO_NET_OFFLINE=true cargo insta test --check --unreferenced reject --test-runner nextest --disable-nextest-doctest --workspace --exclude alliumpy --all-features

# Interactive review for a person at a terminal.
snapshots-review:
    cargo insta review --workspace

# The snapshot recipe that writes: rerun and accept without a terminal.
# Read the diff before committing, and explain each intended change. A .snap
# file no test refers to, left by a renamed or removed test, is deleted, so the
# deletion shows in the diff instead of blocking the accept.
snapshots-accept: lock-check
    INSTA_UPDATE=new CARGO_NET_OFFLINE=true cargo insta test --accept --unreferenced delete --test-runner nextest --disable-nextest-doctest --workspace --exclude alliumpy --all-features

# ----------------------------------------------------------------- format ---

format:
    cargo fmt --all
    cargo fmt --manifest-path fuzz/Cargo.toml
    taplo fmt
    nixfmt flake.nix nix/*.nix

# Automatic repairs. The fix config is run twice because a
# fixer's first pass may itself fail on what another fixer then repairs.
fix:
    -prek run --all-files --config .pre-commit-fix.yaml
    prek run --all-files --config .pre-commit-fix.yaml
    cargo fmt --manifest-path fuzz/Cargo.toml
    cargo clippy --workspace --all-targets --all-features --locked --fix --allow-dirty --allow-staged
    cargo clippy --manifest-path fuzz/Cargo.toml --all-targets --locked --fix --allow-dirty --allow-staged
    just lint

# ------------------------------------------------------------------ check ---

lint:
    prek run --all-files

# cargo fmt --all skips the fuzz crate, which is outside the workspace. The flake's
# Nix files are formatted too, by the nixfmt the shell pins.
fmt-check:
    cargo fmt --all --check
    cargo fmt --manifest-path fuzz/Cargo.toml --check
    nixfmt --check flake.nix nix/*.nix

toml-check:
    taplo fmt --check
    taplo lint

# Every lint the manifests declare, as errors. The manifests say `warn` so a
# local build never breaks mid-edit; this is where warnings become failures.
# The fuzz crate is outside the workspace, so --workspace skips it, and its own
# lint tables (invariants 4 and 5) hold only if something compiles it.
# libfuzzer-sys's build script compiles libFuzzer's C++ through cc, so this line
# makes a C++ compiler a prerequisite of the gate.
clippy:
    cargo clippy --workspace --all-targets --all-features --locked -- -D warnings
    cargo clippy --manifest-path fuzz/Cargo.toml --all-targets --locked -- -D warnings

# Gate 7: complexity, cohesion and coupling, through rustqual against
# rustqual.toml, once per crate. rustqual's version decides what the gate reports;
# nix/rustqual.nix pins it, and check-toolchain has already refused a rustqual from
# outside the Nix store.
metrics:
    rustqual crates/alliumpy-core --config rustqual.toml --fail-on-warnings --format github
    rustqual crates/alliumpy --config rustqual.toml --fail-on-warnings --format github

# Every feature combination compiles. Not --no-dev-deps: that rewrites Cargo.toml
# while it runs and would trip the worktree snapshot on a crash.
features:
    cargo hack check --workspace --feature-powerset --locked

# Measures the core; pytest exercises the bindings outside llvm-cov.
# Runs every nextest test under instrumentation and enforces the floor. Doctests
# are not measured (nightly-only in llvm-cov); test-doc runs them uncovered.
# llvm-cov does not create the lcov file's directory, so the recipe does.
# INSTA_UPDATE=no fails a mismatch without a pending file that would trip the
# gate's worktree check.
coverage:
    INSTA_UPDATE=no cargo llvm-cov nextest -p alliumpy-core --all-features --locked --no-report
    cargo llvm-cov report --fail-under-lines {{coverage_floor}}
    mkdir -p target/llvm-cov
    cargo llvm-cov report --lcov --output-path target/llvm-cov/lcov.info

doc:
    RUSTDOCFLAGS="-D warnings --cfg docsrs" cargo doc --workspace --no-deps --all-features --locked

# What GitHub Pages serves: the API reference `doc` builds, from an empty
# target/doc so that nothing stale is published, and a root index.html that
# links to both crates' pages, because stable rustdoc writes none. Not a
# gate and outside `just check`: `doc` is the gate, and this adds one file
# to what it built. The flags are `doc`'s own, through the recipe, so the
# hosted reference is the one the gate proved.
site:
    rm -rf target/doc
    just doc
    printf '%s\n' '<!doctype html>' '<html lang="en">' '<meta charset="utf-8">' '<title>alliumpy: API reference</title>' '<p><a href="alliumpy_core/index.html">The alliumpy_core API reference</a></p>' '<p><a href="alliumpy/index.html">The alliumpy API reference</a></p>' '</html>' > target/doc/index.html

# Licences, bans and sources are answerable offline once `just sync` has run.
deny:
    cargo deny --locked check licenses bans sources

# Advisories need the RustSec database over the network, so this sits outside
# `just check` for the same reason check-links-online does.
audit:
    cargo deny --locked check advisories

# Mutation testing, a report and never a gate: it grows with the core towards
# hours, and a mutant that survives asks for a judgement. It mutates a copy of the
# tree, so the worktree gains only mutants.out/, which Git ignores; the copy leaves
# out what Git ignores, or it would carry target/ and .tools/ into every build.
# `cargo test`, not nextest, because nextest skips doctests and a mutant only a
# doc example catches would be reported missed. The core alone: the pyo3 crate's
# tests are Python's, so every mutant there would be missed, and its test binary
# needs libpython. The first line is the positive control over the same selection
# the run uses, the caller's filters included: a filter that matched nothing would
# otherwise print a green summary over zero mutants. Exit 2
# means a mutant survived, 3 a timeout, 4 a failing baseline. lock-check runs
# first: the listing pass's `cargo metadata` takes no --locked and would rewrite a
# stale Cargo.lock.
mutants *args: lock-check
    [ "$(cargo mutants --list --package alliumpy-core --all-features "$@" | grep -c .)" -gt 0 ] || { printf '%s\n' 'mutants: no mutants found; the filters select nothing' >&2; exit 1; }
    cargo mutants --package alliumpy-core --all-features --gitignore=true --cargo-arg=--locked "$@"

deps-unused:
    cargo shear

# --------------------------------------------------------------- documents ---

check-docs:
    prek run --all-files markdownlint-cli2 typos lychee
    bg-validate-docs

check-agents:
    bg-validate-agents

check-links-online:
    prek run --all-files --hook-stage manual lychee-online

# ------------------------------------------------------------------ python ---

# Builds the extension in place (the .so beside __init__.py, gitignored) and installs
# it, editable, into target/py-env. The shell's Python is read-only, so maturin needs a
# venv to install into: made on the shell's interpreter, offline, and recreated on every
# run so it never outlives that interpreter. --system-site-packages is how it sees
# pytest, mypy and the checkers, which live in the shell's Python. `locked = true` in
# crates/alliumpy/pyproject.toml makes maturin honour Cargo.lock. Not a gate: py-test,
# py-stubtest and parity depend on it.
py-develop:
    uv venv --clear --offline --no-python-downloads --system-site-packages --python "$PYO3_PYTHON" --quiet "{{ py_env }}"
    UV_OFFLINE=1 VIRTUAL_ENV="{{ py_env }}" maturin develop --uv --manifest-path crates/alliumpy/Cargo.toml

# Gate: ruff over every Python file ruff.toml names; --show-files must list
# the package, or an exclude has emptied the gate (ruff exits 0 on no files);
# then the positive control: the fixture must fail with exit status 1
# (violations found) and the output must name F401 and E501, the fixture's
# own violations: under select = ALL the file also trips INP001, D100 and
# the copyright-notice rule, so the exit status alone would fire with F and
# E dropped. Exit 2
# is a tool or usage error, not a fired control; a missing fixture is E902
# with exit 1, so it is tested first.
py-lint:
    ruff check .
    ruff format --check .
    ruff check --show-files . | grep -q 'crates/alliumpy/python/alliumpy/__init__\.py$' || { printf '%s\n' 'py-lint: ruff did not see the package' >&2; exit 1; }
    test -f tests/fixtures/py-lint-violation/ruff.py || { printf '%s\n' 'py-lint: the positive control fixture is missing' >&2; exit 1; }
    status=0; out=$(ruff check --quiet --output-format concise tests/fixtures/py-lint-violation/ruff.py) || status=$?; [ "$status" -eq 1 ] && printf '%s\n' "$out" | grep -q ': F401 ' && printf '%s\n' "$out" | grep -q ': E501 ' || { printf '%s\n' "$out" 'py-lint: the positive control did not fire (exit 1 naming F401 and E501)' >&2; exit 1; }

# Gate: mypy over the files mypy.ini names (the stub, the package, the tests,
# scripts/), then the positive control: the fixture must fail with exit status
# 1 (type errors). Exit 2 is a usage or I/O error, not a fired control, and the
# one error line stays visible for the hand-back (CONVENTIONS.md §11). stubtest,
# which imports the built module, is py-stubtest.
py-typecheck:
    mypy
    status=0; mypy --no-error-summary tests/fixtures/py-lint-violation/mypy.py || status=$?; [ "$status" -eq 1 ] || { printf '%s\n' 'py-typecheck: the positive control did not fire' >&2; exit 1; }

# Gate: the binding's behaviour tests, against the extension py-develop built.
py-test: py-develop
    "{{ py_env }}/bin/python" -m pytest crates/alliumpy/tests

# Gate: the stub file describes the built module exactly. The allowlist is
# reviewed in T03 and must stay short; an entry hides a discrepancy.
py-stubtest: py-develop
    "{{ py_env }}/bin/python" -m mypy.stubtest alliumpy._alliumpy --allowlist crates/alliumpy/tests/stubtest-allowlist.txt

# The release wheel for this platform into dist/, which is emptied first so a
# stale wheel can never be smoked. A release build on every `just check` is
# the price of smoking the artefact the release ships (CONVENTIONS.md §9).
#
# NIX_DONT_SET_RPATH keeps the dev shell's linker from writing its store paths into the
# extension's RUNPATH: the wheel is for machines without Nix, and on one with Nix those
# paths would load the store's libgcc_s instead of the system's.
wheel:
    rm -rf dist
    NIX_DONT_SET_RPATH=1 maturin build --release --manifest-path crates/alliumpy/Cargo.toml --out dist

# Gate: the wheel installs and works in a fresh virtual environment, offline.
# Exactly one wheel, which must exist (an unmatched glob is one literal argument);
# a venv on the shell's interpreter with no download; install
# from dist/ alone; then import, parse the smoke fixtures, and run the console
# script's --version and its check on the clean fixture, which must exit 0.
# Python runs with -I so nothing in the worktree shadows the package.
wheel-smoke: wheel
    #!/bin/sh
    set -eu
    set -- dist/*.whl
    [ "$#" -eq 1 ] && [ -f "$1" ] || { printf 'wheel-smoke: expected one wheel in dist/, found: %s\n' "$*" >&2; exit 1; }
    rm -rf target/wheel-smoke
    uv venv --python "$PYO3_PYTHON" --no-python-downloads --offline target/wheel-smoke/venv
    uv pip install --python target/wheel-smoke/venv --offline --no-index --no-deps "$1"
    target/wheel-smoke/venv/bin/python -I tests/fixtures/smoke/smoke.py
    target/wheel-smoke/venv/bin/allium --version
    target/wheel-smoke/venv/bin/allium check tests/fixtures/smoke/ok.allium

# Gate: one version, in every place it is written (CONVENTIONS.md §9). Reads
# the Cargo manifests, the wheel manifest and the console script's own output
# from the venv wheel-smoke left; fails if that venv is missing.
version-check:
    python -I scripts/version_check.py

# ------------------------------------------------------------------ parity ---

# The reference allium: upstream's own CLI, built from crates.io at the version
# the core wraps, into a root that is never on PATH, so that nothing can shadow
# the wheel's allium or be shadowed by it (CONVENTIONS.md §9). Network; outside
# `check`. The version is read from Cargo.toml so the pin cannot drift from it.
install-parity-reference:
    #!/bin/sh
    set -eu
    pin=$(python -I scripts/version_check.py --print-pin)
    cargo install "allium-cli@${pin}" --locked --root .tools/parity
    .tools/parity/bin/allium --version

# Byte-for-byte stdout and exit-code parity between the wheel's allium (the venv
# wheel-smoke, which this recipe depends on, has just rebuilt from this worktree,
# so the candidate is never stale) and the reference, over tests/fixtures/parity/
# and the argument matrix tests/parity/README.md lists. POSIX-only; outside
# `check` because the reference needs the network to build. Fails closed on an
# empty corpus and runs its own positive and negative controls first, then the
# behaviours beyond the corpus (`test_cli.py`) against the same candidate.
parity: wheel-smoke py-develop
    test -x .tools/parity/bin/allium || { printf '%s\n' 'parity: no reference; run just install-parity-reference' >&2; exit 2; }
    python -I tests/parity/run.py --reference "$PWD/.tools/parity/bin/allium" --candidate "$PWD/target/wheel-smoke/venv/bin/allium" --corpus tests/fixtures/parity
    ALLIUMPY_SMOKE_BIN="$PWD/target/wheel-smoke/venv/bin/allium" "{{ py_env }}/bin/python" -m pytest crates/alliumpy/tests/test_cli.py -rs

# --------------------------------------------------------------- aggregate ---

check-clean baseline="":
    bg-project-check clean "$1"

# The complete gate: the recipes pyproject.toml lists, in order, with the
# worktree snapshotted between each, then check-clean.
check:
    bg-project-check run
