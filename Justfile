set positional-arguments := true
set shell := ["sh", "-eu", "-c"]

# Who provides the tools is said here and nowhere else. There are two providers
# while the Nix flake is being introduced (decision 0018).
#
# Inside the flake's dev shell, which sets ALLIUMPY_TOOLS=nix, the shell provides
# the tools and the compiler, and PATH is left as the shell made it: the Justfile
# adds nothing from .pixi or .tools, even when both exist. A tool the shell does
# not hold falls through to the PATH the shell inherited, so the shell, not this
# file, decides what is complete; check-toolchain at least requires the compiler
# to come from the Nix store.
#
# Anywhere else pixi owns every tool binary and the Python environment
# (.pixi/envs/default; pyproject.toml is the manifest, pixi.lock the pin). Tools
# conda-forge lacks (tools.txt, and tools-source.txt for those with no release
# binary) live in .tools/bin, which holds only what conda-forge lacks. Every
# recipe, and every hook that runs through a recipe, sees both first. Neither
# directory holds a cargo, so the compiler is whichever cargo PATH names next.
#
# Either way a recipe finds Python and every tool on PATH by name, and
# check-toolchain proves the compiler is the one rust-toolchain.toml pins. Any
# other value is refused, so a typo cannot fall through to the machine's tools.
tools := env("ALLIUMPY_TOOLS", "pixi")
provider_path := if tools == "nix" { "" } else if tools == "pixi" { justfile_directory() / ".pixi" / "envs" / "default" / "bin" + ":" + justfile_directory() / ".tools" / "bin" } else { error("ALLIUMPY_TOOLS is '" + tools + "'; the flake's dev shell sets it to nix, and nothing else should set it") }

# The hook gate and its mutating counterpart. The dev shell's form calls the
# shell's own checkers by name; pixi's form lets prek fetch and build them.
hook_config := if tools == "nix" { ".pre-commit-nix.yaml" } else { ".pre-commit-config.yaml" }
fix_config := if tools == "nix" { ".pre-commit-nix-fix.yaml" } else { ".pre-commit-fix.yaml" }

# Where py-develop installs the extension. Neither provider's own Python
# environment can take it: the dev shell's is read-only, in the Nix store. So
# the editable install goes into a virtual environment under target/, built on
# the provider's interpreter and seeing its packages (pytest, mypy). Its bin
# comes first, so once py-develop has run, `python` by name is the interpreter
# that can import the extension; before that the directory does not exist and
# `python` is the provider's own.
develop_env := justfile_directory() / "target" / "py-develop"

export PATH := develop_env / "bin" + ":" + if provider_path == "" { env("PATH") } else { provider_path + ":" + env("PATH") }

# Every cargo invocation compiles the bindings against the provider's Python,
# found by name: the provider's own interpreter, never the virtual environment's,
# so the value does not change when py-develop first runs and cargo's
# fingerprints stay put. A missing interpreter leaves the bare name, so pyo3's
# build script says what it could not run and no recipe fails before it starts.
export PYO3_PYTHON := shell('PATH="$1${1:+:}$PATH"; command -v python || printf "%s\n" python', provider_path)

# Line-coverage floor over crates/alliumpy-core/src/**. Lower the complexity, not the
# number.
coverage_floor := "90"

default:
    @just --list

# ------------------------------------------------------------------ setup ---

# One explicit first-run command. Never stages, commits, tags, or pushes.
initialize:
    sh scripts/initialize.sh

# Whoever provides cargo, the compiler it runs must be the one rust-toolchain.toml
# pins, with the components the file names: a cargo from pixi, Homebrew or a
# distribution ignores the file and builds with whatever it is, and rustup's
# proxy obeys RUSTUP_TOOLCHAIN or a `rustup override` before it. So the gate asks
# cargo and the rustc cargo will run (RUSTC, if set) for their release, and
# refuses any other than the channel, which must be an exact release for the
# comparison to mean anything. Stable cargo cannot say which rustc it will run, so
# the variables that would make it run another one (CARGO_BUILD_RUSTC and the
# three wrapper variables) are refused outright; cargo's config files are not
# read, and this repository has none (decision 0004). rustfmt, cargo-clippy and
# clippy-driver must report that rustc's commit, which a component of another
# toolchain reached through PATH cannot, and llvm-cov and llvm-profdata, which
# coverage needs, must sit in that rustc's own sysroot and report its release.
# A component the file names and this recipe cannot verify is refused, not
# skipped. `channel` and `components` must each sit on one line, spelt as
# rust-toolchain.toml spells them now; any other form is refused, not misread.
# RUSTUP_AUTO_INSTALL=0 makes an uninstalled toolchain a refusal instead of a
# download where rustup is the provider; no other provider reads it.
check-toolchain:
    #!/bin/sh
    set -eu
    export RUSTUP_AUTO_INSTALL=0
    fail() { printf 'check-toolchain: %s\n' "$1" >&2; exit 2; }
    pin=$(sed -n 's/^channel = "\(.*\)"$/\1/p' rust-toolchain.toml)
    [ -n "$pin" ] || fail 'rust-toolchain.toml names no channel'
    case "$pin" in
        *[!0-9.]* | *.*.*.* | .* | *. | *..*) fail "the channel $pin is not an exact release" ;;
        *.*.*) ;;
        *) fail "the channel $pin is not an exact release" ;;
    esac
    cargo_info=$(cargo -vV) || fail "cargo ($(command -v cargo || printf missing)) cannot run the pinned $pin"
    cargo_release=$(printf '%s\n' "$cargo_info" | sed -n 's/^release: //p')
    [ "$cargo_release" = "$pin" ] || fail "cargo is ${cargo_release:-unknown}, not the pinned $pin ($(command -v cargo))"
    for var in CARGO_BUILD_RUSTC RUSTC_WRAPPER CARGO_BUILD_RUSTC_WRAPPER RUSTC_WORKSPACE_WRAPPER; do
        eval "value=\${$var:-}"
        [ -z "$value" ] || fail "$var is set ($value), so cargo may run a compiler this check cannot see; unset it"
    done
    rustc=${RUSTC:-rustc}
    rustc_info=$("$rustc" -vV) || fail "$rustc cannot run"
    rustc_release=$(printf '%s\n' "$rustc_info" | sed -n 's/^release: //p')
    [ "$rustc_release" = "$pin" ] || fail "rustc is ${rustc_release:-unknown}, not the pinned $pin ($(command -v "$rustc"))"
    host=$(printf '%s\n' "$rustc_info" | sed -n 's/^host: //p')
    commit=$(printf '%s\n' "$rustc_info" | sed -n 's/^commit-hash: \(.........\).*$/\1/p')
    [ -n "$host" ] && [ -n "$commit" ] || fail 'rustc names no host or no commit'
    components=$(sed -n 's/^components = \[\(.*\)\]$/\1/p' rust-toolchain.toml | tr -d '" ' | tr ',' ' ')
    [ -n "$components" ] || fail 'rust-toolchain.toml names no components'
    for component in $components; do
        case "$component" in
            rustfmt) have=$(cargo fmt --version 2>/dev/null) || fail 'the rustfmt component is missing' ;;
            clippy)
                have=$(cargo clippy --version 2>/dev/null) || fail 'the clippy component is missing'
                driver=$(clippy-driver --version 2>/dev/null) || fail 'clippy-driver is missing'
                case "$driver" in
                    *"($commit"*) ;;
                    *) fail "clippy-driver is '$driver', not the pinned compiler's ($commit)" ;;
                esac ;;
            llvm-tools | llvm-tools-preview)
                bin=$("$rustc" --print sysroot)/lib/rustlib/$host/bin
                for tool in llvm-cov llvm-profdata; do
                    version=$("$bin/$tool" --version 2>/dev/null) || fail "$tool from the $component component is missing from $rustc's sysroot"
                    case "$version" in
                        *"-rust-$pin-"*) ;;
                        *) fail "$tool in $rustc's sysroot is not the pinned $pin's" ;;
                    esac
                done
                continue ;;
            *) fail "rust-toolchain.toml names the component $component, which this recipe cannot verify" ;;
        esac
        case "$have" in
            *"($commit"*) ;;
            *) fail "$component is '$have', not the pinned compiler's ($commit)" ;;
        esac
    done
    if [ "{{ tools }}" = nix ]; then
        for tool in cargo "$rustc"; do
            case "$(command -v "$tool")" in
                /nix/store/*) ;;
                *) fail "the dev shell is the provider, but $tool resolves to $(command -v "$tool"), outside the Nix store" ;;
            esac
        done
    fi
    printf '%s (%s) with %s, from %s\n' "$pin" "$host" "$components" "$(command -v cargo)"

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

# Every lockfile, exactly as committed. Never rewrites any. pixi's environment is
# installed only where pixi is the provider; the dev shell's is already there.
sync:
    cargo fetch --locked
    cargo fetch --locked --manifest-path fuzz/Cargo.toml
    {{ if tools == "pixi" { "pixi install --frozen" } else { "true" } }}

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
    {{ if tools == "pixi" { "pixi lock --check --offline --dry-run" } else { "true" } }}

# The shim, then every hook environment (seven clones; Go under prek's cache;
# the ripsecrets build with the machine's rustup and the pinned toolchain), so
# that `just check` never fetches. lychee is `language: script` and downloads
# its binary at first run, not at prepare, so it is run once here on one
# Markdown file; its exit status is lint's business, not this recipe's. Its
# checkout pins `stable`, and its script's cargo-binstall calls rustc, so
# without RUSTUP_AUTO_INSTALL=0 rustup would install that toolchain.
#
# In the dev shell every hook is a tool the shell holds, so there is nothing to
# prepare and nothing is fetched; the shim names the dev shell's form, and a
# commit made from outside the shell fails on a `just` or a checker it cannot
# find rather than passing.
install-hooks:
    git rev-parse --is-inside-work-tree >/dev/null
    command -v prek >/dev/null || { printf '%s\n' {{ if tools == "nix" { "'prek is not on PATH; enter the dev shell'" } else { "'prek is not on PATH; run just initialize first'" } }} >&2; exit 2; }
    prek install --overwrite --hook-type=pre-commit --config {{ hook_config }} {{ if tools == "nix" { "" } else { "--prepare-hooks" } }}
    {{ if tools == "nix" { "true" } else { "prek prepare-hooks --config .pre-commit-fix.yaml" } }}
    -{{ if tools == "nix" { "true" } else { "RUSTUP_AUTO_INSTALL=0 prek run lychee --files README.md" } }}

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
    {{ if tools == "nix" { "just nix-format" } else { "true" } }}
    cargo fmt --all
    cargo fmt --manifest-path fuzz/Cargo.toml
    taplo fmt

# Automatic repairs. The fix config is run twice because a
# fixer's first pass may itself fail on what another fixer then repairs.
fix:
    {{ if tools == "nix" { "just nix-format" } else { "true" } }}
    -prek run --all-files --config {{ fix_config }}
    prek run --all-files --config {{ fix_config }}
    cargo fmt --manifest-path fuzz/Cargo.toml
    cargo clippy --workspace --all-targets --all-features --locked --fix --allow-dirty --allow-staged
    cargo clippy --manifest-path fuzz/Cargo.toml --all-targets --locked --fix --allow-dirty --allow-staged
    just lint

# ------------------------------------------------------------------ check ---

lint:
    prek run --all-files --config {{ hook_config }}

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
# version decides what the gate reports, so a missing rustqual must not fall
# through to another one on PATH. Each provider owns the version it expects: the
# dev shell exports the one the flake builds, and pixi's side reads
# tools-source.txt. An expectation that is empty is refused too.
metrics:
    #!/bin/sh
    set -eu
    if [ "{{ tools }}" = nix ]; then
        pin=${ALLIUMPY_RUSTQUAL_VERSION:-}; owner=flake.nix; remedy='enter the dev shell'
    else
        pin=$(sed -n 's/^rustqual@//p' tools-source.txt); owner=tools-source.txt; remedy='run just install-tools'
    fi
    [ -n "$pin" ] || { printf 'metrics: %s names no rustqual version; %s\n' "$owner" "$remedy" >&2; exit 1; }
    have=$(rustqual --version 2>/dev/null | sed -n 's/^rustqual //p')
    if [ "$have" != "$pin" ]; then
        printf 'metrics: rustqual %s on PATH, %s pins %s; %s\n' "${have:-missing}" "$owner" "$pin" "$remedy" >&2
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
    prek run --all-files --config {{ hook_config }} markdownlint-cli2 typos lychee
    bg-validate-docs

check-agents:
    bg-validate-agents

# The two hook entries with no gate of their own (the agent-contract hook runs
# check-agents). A git hook does not inherit this file's PATH, so each hook
# reaches its `bg-*` command through a recipe, as the Rust and Python hooks do,
# and none names where the command lives. The secret scan receives the staged
# files as arguments, and finds ripsecrets on the PATH prek gives its hook
# environment, which the recipe's PATH keeps behind the provider's.
[private]
hook-validate-docs:
    bg-validate-docs

[private]
hook-ripsecrets *files:
    bg-ripsecrets "$@"

check-links-online:
    prek run --all-files --config {{ hook_config }} --hook-stage manual lychee-online

# --------------------------------------------------------------------- nix ---

# The flake's own files are code: formatted exactly as nixfmt writes them, with
# nothing statix warns about and no binding deadnix finds unused. The three tools
# come from the dev shell, so this runs only there; it joins check's recipe list
# when the shell becomes the only provider. Git names the files, because a flake
# sees only what Git tracks, and a listing that names none fails: all three tools
# exit 0 when handed nothing.
nix-check:
    #!/bin/sh
    set -eu
    [ "$(git ls-files '*.nix' | grep -c .)" -gt 0 ] || { printf '%s\n' 'nix-check: git lists no Nix file' >&2; exit 1; }
    git ls-files -z '*.nix' | xargs -0 nixfmt --check
    git ls-files -z '*.nix' | xargs -0 -n 1 statix check
    git ls-files -z '*.nix' | xargs -0 deadnix --fail

# The mutating counterpart: `just format` and `just fix` call it in the dev shell.
nix-format:
    git ls-files -z '*.nix' | xargs -0 nixfmt

# ------------------------------------------------------------------ python ---

# Builds the extension in place (the .so beside __init__.py, gitignored) and
# installs it editable into the virtual environment the seam names. uv makes
# that environment on the provider's interpreter, offline and without
# downloading one, and keeps an existing one; --system-site-packages is what
# lets it see the provider's pytest and mypy. maturin is handed it through
# VIRTUAL_ENV, set on this line alone, with CONDA_PREFIX unset because maturin
# refuses to choose between the two, and installs with the uv on PATH.
# `locked = true` in crates/alliumpy/pyproject.toml makes it honour Cargo.lock.
# Not a gate: py-test and py-stubtest depend on it.
py-develop:
    uv venv --quiet --python "$PYO3_PYTHON" --system-site-packages --no-python-downloads --offline --allow-existing "{{ develop_env }}"
    env -u CONDA_PREFIX VIRTUAL_ENV="{{ develop_env }}" maturin develop --manifest-path crates/alliumpy/Cargo.toml

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
# a venv on the provider's own interpreter with no download; install
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
parity: wheel-smoke
    test -x .tools/parity/bin/allium || { printf '%s\n' 'parity: no reference; run just install-parity-reference' >&2; exit 2; }
    python -I tests/parity/run.py --reference "$PWD/.tools/parity/bin/allium" --candidate "$PWD/target/wheel-smoke/venv/bin/allium" --corpus tests/fixtures/parity
    ALLIUMPY_SMOKE_BIN="$PWD/target/wheel-smoke/venv/bin/allium" python -m pytest crates/alliumpy/tests/test_cli.py -rs

# --------------------------------------------------------------- aggregate ---

check-clean baseline="":
    bg-project-check clean "$1"

# The complete gate: the recipes pyproject.toml lists, in order, with the
# worktree snapshotted between each, then check-clean.
check:
    bg-project-check run
