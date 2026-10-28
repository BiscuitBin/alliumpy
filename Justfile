set positional-arguments := true
set shell := ["sh", "-eu", "-c"]

# pixi owns every tool binary and the Python environment (.pixi/envs/default;
# pyproject.toml is the manifest, pixi.lock the pin). Every recipe, and every
# hook that runs through a recipe, sees the environment first.
export PATH := justfile_directory() / ".pixi" / "envs" / "default" / "bin" + ":" + env("PATH")

default:
    @just --list

# ------------------------------------------------------------------ setup ---

# One explicit first-run command. Never stages, commits, tags, or pushes.
initialize:
    sh scripts/initialize.sh

# The lockfile, exactly as committed. Never rewrites it. Installs the package
# editable with its test extras, so the console script and pytest see the
# worktree's sources.
sync:
    pixi install --frozen

lock:
    pixi lock

# Within the manifest's constraints only; every direct pin is exact, so this
# moves transitives. `pixi upgrade` rewrites the pins themselves and is not
# this recipe.
lock-upgrade:
    pixi update

# Offline, like every gate recipe: an offline solve on a stale lock fails,
# which is the right answer. --dry-run because pixi would otherwise rewrite a
# stale lock from that restricted solve.
lock-check:
    pixi lock --check --offline --dry-run

# The shim, then every hook environment, so that `just check` never fetches.
# ripsecrets builds in prek's cache with the machine's rustup; without
# RUSTUP_AUTO_INSTALL=0 rustup would install a toolchain for it.
install-hooks:
    git rev-parse --is-inside-work-tree >/dev/null
    test -x .pixi/envs/default/bin/prek || { printf '%s\n' 'the pixi environment is not installed; run just initialize first' >&2; exit 2; }
    RUSTUP_AUTO_INSTALL=0 prek install --overwrite --hook-type=pre-commit --prepare-hooks
    prek prepare-hooks --config .pre-commit-fix.yaml

# The Chromium build patchright drives (network). Tier 1 of the fetch ladder
# needs it; `docmirror doctor` reports whether it is present.
install-browser:
    patchright install chromium

# ----------------------------------------------------------------- format ---

format:
    ruff format .
    taplo fmt

# Automatic repairs. The fix config is run twice because a
# fixer's first pass may itself fail on what another fixer then repairs.
fix:
    -prek run --all-files --config .pre-commit-fix.yaml
    prek run --all-files --config .pre-commit-fix.yaml
    just lint

# ------------------------------------------------------------------ check ---

lint:
    prek run --all-files

toml-check:
    taplo fmt --check
    taplo lint

# Gate: ruff over every Python file ruff.toml names; --show-files must list
# the package, or an exclude has emptied the gate (ruff exits 0 on no files);
# then the positive control: the fixture must fail with exit status 1
# (violations found) and the output must name F401 and E501, the fixture's
# own violations. Exit 2 is a tool or usage error, not a fired control; a
# missing fixture is E902 with exit 1, so it is tested first.
py-lint:
    ruff check .
    ruff format --check .
    ruff check --show-files . | grep -q 'src/docmirror/__init__\.py$' || { printf '%s\n' 'py-lint: ruff did not see the package' >&2; exit 1; }
    test -f tests/fixtures/py-lint-violation/ruff.py || { printf '%s\n' 'py-lint: the positive control fixture is missing' >&2; exit 1; }
    status=0; out=$(ruff check --quiet --output-format concise tests/fixtures/py-lint-violation/ruff.py) || status=$?; [ "$status" -eq 1 ] && printf '%s\n' "$out" | grep -q ': F401 ' && printf '%s\n' "$out" | grep -q ': E501 ' || { printf '%s\n' "$out" 'py-lint: the positive control did not fire (exit 1 naming F401 and E501)' >&2; exit 1; }

# Gate: mypy over the files mypy.ini names (the package, the tests, scripts/),
# then the positive control: the fixture must fail with exit status 1 (type
# errors). Exit 2 is a usage or I/O error, not a fired control.
py-typecheck:
    mypy
    status=0; mypy --no-error-summary tests/fixtures/py-lint-violation/mypy.py || status=$?; [ "$status" -eq 1 ] || { printf '%s\n' 'py-typecheck: the positive control did not fire' >&2; exit 1; }

# Gate: the offline suites (unit and golden). `live` and `oracle` are
# deselected by pyproject.toml's addopts and have recipes of their own.
py-test:
    python -m pytest

# The snapshot recipe that writes: rerun the golden suite and accept every
# changed snapshot. Read the diff before committing, and explain each intended
# change.
py-test-accept:
    python -m pytest tests/golden --snapshot-update

# The live smoke suite: real crawls of the target sites (network).
py-test-live:
    python -m pytest -m live --override-ini addopts= tests/live

# The oracle suite: fidelity against upstream Markdown endpoints (network).
py-test-oracle:
    python -m pytest -m oracle --override-ini addopts= tests/oracle

# The release wheel into dist/, which is emptied first so a stale wheel can
# never be smoked. No build isolation: hatchling is pinned in the pixi
# environment, so the build never reaches the network.
wheel:
    rm -rf dist
    uv build --wheel --no-build-isolation --python .pixi/envs/default/bin/python --out-dir dist

# Gate: the wheel installs and works in a fresh virtual environment, offline.
# Exactly one wheel, which must exist (an unmatched glob is one literal
# argument); a venv on the pixi interpreter with no download that sees the
# environment's site-packages, so the wheel's runtime dependencies resolve
# from the lock while the wheel itself installs with --no-deps from dist/
# alone; then the smoke script and the console script. Python runs with -I so
# nothing in the worktree shadows the package.
wheel-smoke: wheel
    #!/bin/sh
    set -eu
    set -- dist/*.whl
    [ "$#" -eq 1 ] && [ -f "$1" ] || { printf 'wheel-smoke: expected one wheel in dist/, found: %s\n' "$*" >&2; exit 1; }
    rm -rf target/wheel-smoke
    uv venv --python .pixi/envs/default/bin/python --no-python-downloads --offline --system-site-packages target/wheel-smoke/venv
    uv pip install --python target/wheel-smoke/venv --offline --no-index --no-deps "$1"
    target/wheel-smoke/venv/bin/python -I tests/fixtures/smoke/smoke.py target/wheel-smoke/venv/bin/docmirror
    target/wheel-smoke/venv/bin/docmirror --version

# Gate: one version, in every place it is written. Reads pyproject.toml, the
# package's `__version__` and the console script's own output from the venv
# wheel-smoke left; fails if that venv is missing.
version-check:
    python -I scripts/version_check.py

# --------------------------------------------------------------- documents ---

check-docs:
    prek run --all-files markdownlint-cli2 typos lychee
    bg-validate-docs

check-agents:
    bg-validate-agents

check-links-online:
    prek run --all-files --hook-stage manual lychee-online

# --------------------------------------------------------------- aggregate ---

check-clean baseline="":
    bg-project-check clean "$1"

# The complete gate: the recipes pyproject.toml lists, in order, with the
# worktree snapshotted between each, then check-clean.
check:
    bg-project-check run
