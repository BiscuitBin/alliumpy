---
title: "Install and run"
kind: "how-to"
audience: ["user", "contributor", "maintainer", "agent"]
canonical_for: ["install_and_run"]
requires: []
---

# Install and run

`alliumpy` is published on PyPI as <https://pypi.org/project/alliumpy/>, with a wheel for
each platform the [packaging explanation](../explanation/packaging.md) lists. To work
from a checkout instead, follow [Develop locally](develop-locally.md) and run
`just py-develop`.

## Run once with uv

This installs the package temporarily and invokes its command:

```console
uvx --from alliumpy allium --version
```

Use `--from alliumpy` because the distribution name differs from the command name.
`uvx alliumpy` runs the wheel's other script, `alliumpy`, described under
[Gate specifications in CI](#gate-specifications-in-ci).

## Install the command

This creates a persistent tool installation:

```console
uv tool install alliumpy
allium --version
```

## Install for Python

This installs into your selected Python environment:

```console
pip install alliumpy
```

Python 3.11 or newer is required. The [packaging explanation](../explanation/packaging.md)
records platform coverage and the source distribution.

## Use the API

After `just py-develop` in a checkout, run these five lines with the pixi interpreter;
installed users can use their own interpreter. `parse` returns upstream diagnostics:

```python
import alliumpy

diagnostics = alliumpy.parse("-- allium: 1\n?\n")
first = diagnostics[0]
print(first.line, first.col, first.severity)
print(alliumpy.ALLIUM_VERSION)
```

Expected output is `2 1 error` then `3.6.1`. The [API reference](../reference/api.md)
describes each exported name.

## Command behaviour

`allium` is upstream's command at the pinned version: `check`, `analyse`, `parse`,
`plan`, `model`, `help`, `-h`, `--help`, `-V` and `--version`, with upstream's stdout and
exit codes. `allium check` prints one pretty JSON object per file to stdout: status 0
means clean, 1 means at least one error or warning, and 2 means no inputs.

```sh
allium check path/to/specs
allium help check
```

Upstream language documentation is at <https://github.com/juxt/allium-tools>.

## Gate specifications in CI

`alliumpy gate` runs upstream's `check` and `analyse` on files or directories and exits
by one policy, so a CI step needs one line and no `--from`:

```sh
uvx alliumpy gate specs/
```

It prints each diagnostic once as `file:line:col: severity: message [code]`, each
`analyse` finding as `file: finding type: summary`, and a closing count. A character
that is not printable, such as a line break in a file name, is printed as its backslash
escape. The exit status is 0 when every file was read and none has an error or a warning, and 1 when one does or
a file cannot be read. It is 2 for a usage error, a path that is not UTF-8, or when no `.allium` file is found, and
3 when the checker could not report. `info` diagnostics and findings are printed but do
not fail the gate. `alliumpy --help` and `alliumpy gate --help` print usage.

Two options choose what fails. `--fail-on error`, `--fail-on warning` (the default) or
`--fail-on info` fails on any diagnostic at or above that severity, so a repository
with existing warnings can adopt the gate on errors first. `--fail-on-findings` also
fails on any `analyse` finding. A file that cannot be read fails the gate whatever the
options say.

In GitHub Actions, `--format github` prints each diagnostic as an annotation on its file,
line and column, and each finding as an annotation on its file:

```sh
uvx alliumpy gate --fail-on error --format github specs/
```

The gate is this repository's, not upstream's, and its policy differs from `allium
analyse`'s on an error with no finding. [Decision 0019](../decisions/0019-alliumpy-gate-script.md)
records the policy and the Typer dependency it brings.

## Related pages

- [Test and debug](test-and-debug.md)
- [Purpose and scope](../project/purpose-and-scope.md)
