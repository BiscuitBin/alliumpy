# The parity harness

`run.py` compares the wheel's `allium` command with upstream's `allium-cli` at the
pinned version, byte for byte on stdout and exactly on the exit status, over the corpus
in `tests/fixtures/parity/` (its `README.md` says what the corpus holds). It is S01's
harness, copied verbatim from that spike's hand-back notes (sha-256
`db22c87f84f2aa202eb794e47f7f5afc65e86ffe4af4151baac880de205ae8ae`); decision 0014
records the route it proves.

## Running it

```sh
just install-parity-reference   # once per pin; network
just parity
```

`install-parity-reference` builds the reference with `cargo install allium-cli@<pin>
--locked --root .tools/parity`, the pin read from `Cargo.toml`. `.tools/parity/bin` is
never on `PATH`. `parity` rebuilds the wheel through `wheel-smoke`, runs this harness
with the reference by absolute path and the smoke venv's `allium` as the candidate,
then runs `crates/alliumpy/tests/test_cli.py` against the same candidate. Both are
POSIX-only and outside `just check`, because the reference needs the network to build;
the `parity` CI job runs them on Linux.

The harness by hand:

```sh
python -I tests/parity/run.py --reference "$PWD/.tools/parity/bin/allium" \
  --candidate "$PWD/target/wheel-smoke/venv/bin/allium" --corpus tests/fixtures/parity
```

## What it compares

Each row runs one binary with one argument list from the corpus's parent directory,
with stdin from `/dev/null`, a 120-second timeout and an environment of `PATH=/usr/bin:/bin`,
`TZ=UTC` and `LC_ALL=C` alone. A row differs when stdout bytes or the exit status
differ, or when either binary could not run.

**stderr is reported but never compared.** A stderr difference is printed on its row as
`stderr differs, reported only` and does not fail it. Upstream's stderr carries usage
lines, read errors in the platform's words and, on a failed write, a Rust panic message
naming a thread id that changes between runs of the reference itself.

Before the matrix, a **positive control**: the first corpus file, in sorted order, whose
`check` the reference exits 1 on; none means a harness error. After it, two **negative
controls**: the candidate with one byte appended to its stdout, and the candidate forced
to exit 0, each rerun against the reference on the positive control; each must be
reported as the difference it targets, or nothing is printed but the harness error.

Exit status: 0 when nothing differs and both controls fired; 1 when a row differs; 2
for a harness error (an argument, binary or corpus problem, an empty corpus, no positive
control, a negative control that did not fire, an entry in the corpus that is not a
regular file or directory). The summary line is `N compared, M differ`.

## The argument matrix

5N + 53 + 4P rows for an N-file corpus with P importing pairs. Here N = 29 (upstream's 27
files and this repository's pair) and P = 1, so **202 rows**. `F` is each corpus file,
`first` and `last` the first and last in sorted order, `<corpus>` the corpus directory
as a path relative to the working directory.

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

## What it never compares

stderr bytes, which are reported only; anything beside the corpus, since no row passes
`.`; and behaviour no argument list reaches: a closed or full stdout, a broken pipe,
SIGINT, an argument that is not UTF-8 and the order of the two streams on a terminal.
Those are `test_cli.py`'s cases. Windows is out of scope here.
