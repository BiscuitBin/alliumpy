set positional-arguments := true
set shell := ["sh", "-eu", "-c"]

# pixi owns every tool binary and the Python environment (.pixi/envs/default;
# pyproject.toml is the manifest, pixi.lock the pin). Tools conda-forge lacks
# (tools.txt, and tools-source.txt for those with no release binary) live in
# .tools/bin, which holds only what conda-forge lacks. Every recipe, and every hook that
# runs through a recipe, sees both first; cargo finds cargo-nextest and friends
# on PATH by name. Neither directory holds a cargo, so rustup's proxy stays
# first for the compiler (check-toolchain proves it).
export PATH := justfile_directory() / ".pixi" / "envs" / "default" / "bin" + ":" + justfile_directory() / ".tools" / "bin" + ":" + env("PATH")

# Every cargo invocation compiles the bindings against pixi Python.
export PYO3_PYTHON := justfile_directory() / ".pixi" / "envs" / "default" / "bin" / "python"

# Line-coverage floor over crates/alliumpy-core/src/**. Lower the complexity, not the
# number.
coverage_floor := "90"

default:
    @just --list

# ------------------------------------------------------------------ setup ---

# One explicit first-run command. Never stages, commits, tags, or pushes.
initialize:
    sh scripts/initialize.sh

# The pin in rust-toolchain.toml is honoured only by rustup's cargo proxy. A
# cargo from pixi, Homebrew or a distribution ignores the file and builds with
# whatever it is, so the gate refuses it before anything else runs.
check-toolchain:
    command -v rustup >/dev/null || { printf '%s\n' 'rustup is not installed; see docs/how-to/develop-locally.md' >&2; exit 2; }
    case "$(command -v cargo)" in "${CARGO_HOME:-$HOME/.cargo}"/bin/cargo) ;; *) printf '%s\n' "cargo resolves to $(command -v cargo), not rustup's proxy" >&2; exit 2;; esac
    rustup show active-toolchain

# Installs the toolchain, components and targets rust-toolchain.toml names.
install-toolchain:
    rustup toolchain install

# Tools conda-forge lacks into .tools/bin (network). cargo-binstall comes from
# the pixi environment. tools.txt is binary-only: a release archive or nothing.
# tools-source.txt holds tools with no release binary, so its loop may compile,
# and cargo-binstall passes --locked through to `cargo install`. It tries a
# signed cargo-quickinstall build first, and would take one that appeared for
# the pin; --only-signed refuses an unsigned one, and an upstream release
# asset, which nothing would sign, is refused too (decision 0007). That pass runs without a GitHub token, so no build script it
# compiles can read one; its one quickinstall lookup needs no rate-limit lift.
# A pass whose list is empty is skipped, since cargo binstall with no crate
# fails; the guard is plain sh, so it holds for GNU and BSD alike. sed, not
# grep, strips the comments: it exits 0 on a list with no pins but still fails,
# and so fails the recipe, when the file is missing or unreadable.
install-tools:
    pins=$(sed -e '/^#/d' -e '/^$/d' tools.txt); [ -z "$pins" ] || cargo binstall --root .tools --no-confirm --locked --disable-strategies compile $pins
    pins=$(sed -e '/^#/d' -e '/^$/d' tools-source.txt); [ -z "$pins" ] || env -u GITHUB_TOKEN -u GH_TOKEN cargo binstall --root .tools --no-confirm --locked --disable-strategies crate-meta-data --only-signed --no-discover-github-token $pins

# All three lockfiles, exactly as committed. Never rewrites any.
sync:
    cargo fetch --locked
    cargo fetch --locked --manifest-path fuzz/Cargo.toml
    pixi install --frozen

lock:
    cargo update --workspace
    cargo update --workspace --manifest-path fuzz/Cargo.toml
    pixi lock

# Within the manifest's constraints only; every direct pin is exact, so this
# moves transitives (openssl, libcxx, the Python patch level). `pixi upgrade`
# rewrites the pins themselves and is not this recipe.
lock-upgrade:
    cargo update
    cargo update --manifest-path fuzz/Cargo.toml
    pixi update

# Offline, like every gate recipe: a cold Cargo cache fails rather than
# fetching the registry index (`just sync` fills it), and an offline solve on a
# stale lock still fails, which is the right answer. --dry-run because pixi
# would otherwise rewrite a stale lock from that restricted solve.
lock-check:
    cargo update --workspace --locked --offline
    cargo update --workspace --locked --offline --manifest-path fuzz/Cargo.toml
    pixi lock --check --offline --dry-run

# The shim, then every hook environment (seven clones; Go under prek's cache;
# the ripsecrets build with the machine's rustup and the pinned toolchain), so
# that `just check` never fetches. lychee is `language: script` and downloads
# its binary at first run, not at prepare, so it is run once here on one
# Markdown file; its exit status is lint's business, not this recipe's. Its
# checkout pins `stable`, and its script's cargo-binstall calls rustc, so
# without RUSTUP_AUTO_INSTALL=0 rustup would install that toolchain.
install-hooks:
    git rev-parse --is-inside-work-tree >/dev/null
    test -x .pixi/envs/default/bin/prek || { printf '%s\n' 'the pixi environment is not installed; run just initialize first' >&2; exit 2; }
    prek install --overwrite --hook-type=pre-commit --prepare-hooks
    prek prepare-hooks --config .pre-commit-fix.yaml
    -RUSTUP_AUTO_INSTALL=0 prek run lychee --files README.md

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
# because cargo-fuzz defaults to the triple it was built for, and its macOS
# binary is x86_64. seconds bounds the fuzzing, not the build.
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
# cargo-insta 1.48.0 forwards trailing options as test arguments, so nextest
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

# cargo fmt --all skips the fuzz crate, which is outside the workspace.
fmt-check:
    cargo fmt --all --check
    cargo fmt --manifest-path fuzz/Cargo.toml --check

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
# rustqual.toml, once per crate. The version check comes first: rustqual's
# version decides what the gate reports, so a missing .tools/bin/rustqual must
# not fall through to another one on PATH.
metrics:
    #!/bin/sh
    set -eu
    pin=$(sed -n 's/^rustqual@//p' tools-source.txt)
    have=$(rustqual --version 2>/dev/null | sed -n 's/^rustqual //p')
    if [ "$have" != "$pin" ]; then
        printf 'metrics: rustqual %s on PATH, tools-source.txt pins %s; run just install-tools\n' "${have:-missing}" "$pin" >&2
        exit 1
    fi
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
# out what Git ignores, or it would carry .pixi/ and .tools/ into every build.
# `cargo test`, not nextest, because nextest skips doctests and a mutant only a
# doc example catches would be reported missed. The core alone: the pyo3 crate's
# tests are Python's, so every mutant there would be missed, and its test binary
# needs libpython. The first line is the positive control over the same selection
# the run uses, the caller's filters included: a filter that matched nothing would
# otherwise print a green summary over zero mutants. Exit 2
# means a mutant survived, 3 a timeout, 4 a failing baseline.
mutants *args:
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

# Builds the extension into the pixi environment in place (the .so beside
# __init__.py, gitignored). maturin needs an environment to install into and
# finds the pixi one through CONDA_PREFIX, set on this line alone; it installs
# with the pinned uv on PATH. `locked = true` in crates/alliumpy/pyproject.toml
# makes it honour Cargo.lock. Not a gate: py-test and py-stubtest depend on it.
py-develop:
    CONDA_PREFIX="{{ justfile_directory() }}/.pixi/envs/default" maturin develop --manifest-path crates/alliumpy/Cargo.toml

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
    python -m pytest crates/alliumpy/tests

# Gate: the stub file describes the built module exactly. The allowlist is
# reviewed in T03 and must stay short; an entry hides a discrepancy.
py-stubtest: py-develop
    python -m mypy.stubtest alliumpy._alliumpy --allowlist crates/alliumpy/tests/stubtest-allowlist.txt

# The release wheel for this platform into dist/, which is emptied first so a
# stale wheel can never be smoked. A release build on every `just check` is
# the price of smoking the artefact the release ships (CONVENTIONS.md §9).
wheel:
    rm -rf dist
    maturin build --release --manifest-path crates/alliumpy/Cargo.toml --out dist

# Gate: the wheel installs and works in a fresh virtual environment, offline.
# Exactly one wheel, which must exist (an unmatched glob is one literal argument);
# a venv on the pixi interpreter with no download; install
# from dist/ alone; then import, parse the smoke fixtures, and run the console
# script. Python runs with -I so nothing in the worktree shadows the package.
wheel-smoke: wheel
    #!/bin/sh
    set -eu
    set -- dist/*.whl
    [ "$#" -eq 1 ] && [ -f "$1" ] || { printf 'wheel-smoke: expected one wheel in dist/, found: %s\n' "$*" >&2; exit 1; }
    rm -rf target/wheel-smoke
    uv venv --python .pixi/envs/default/bin/python --no-python-downloads --offline target/wheel-smoke/venv
    uv pip install --python target/wheel-smoke/venv --offline --no-index --no-deps "$1"
    target/wheel-smoke/venv/bin/python -I tests/fixtures/smoke/smoke.py
    target/wheel-smoke/venv/bin/allium --version

# Gate: one version, in every place it is written (CONVENTIONS.md §9). Reads
# the Cargo manifests, the wheel manifest and the console script's own output
# from the venv wheel-smoke left; fails if that venv is missing.
version-check:
    python -I scripts/version_check.py

# --------------------------------------------------------------- aggregate ---

check-clean baseline="":
    bg-project-check clean "$1"

# The complete gate: the recipes pyproject.toml lists, in order, with the
# worktree snapshotted between each, then check-clean.
check:
    bg-project-check run
