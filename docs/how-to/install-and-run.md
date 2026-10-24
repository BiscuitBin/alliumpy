---
title: "Install and run"
kind: "how-to"
audience: ["user", "contributor", "maintainer", "agent"]
canonical_for: ["install_and_run"]
requires: []
---

# Install and run

Nothing is on PyPI yet. T14 publishes the first wheel; the installation commands below
describe that future release. For a checkout today, follow
[Develop locally](develop-locally.md) and run `just py-develop`.

## Run once with uv

Once T14 has published, this installs the package temporarily and invokes its command:

```console
uvx --from alliumpy allium --version
```

Use `--from alliumpy` because the distribution name differs from the command name.
`uvx alliumpy` would look for a command named `alliumpy`.

## Install the command

Once T14 has published, this creates a persistent tool installation:

```console
uv tool install alliumpy
allium --version
```

## Install for Python

Once T14 has published, this installs into your selected Python environment:

```console
pip install alliumpy
```

Python 3.11 or newer is required. The [packaging explanation](../explanation/packaging.md)
records platform coverage and the pending source distribution ruling.

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

On this main, `allium` answers `-V` and `--version` only. Other arguments return status 2
with a message that the command arrives in T13. T13 brings the remaining command behaviour.
Upstream's `allium check` prints one pretty JSON object per file to stdout: status 0
means clean, 1 means at least one error or warning, and 2 means no inputs. These are
upstream's semantics to preserve in T13, not commands available here yet.

Upstream language documentation is at <https://github.com/juxt/allium-tools>.

## Related pages

- [Test and debug](test-and-debug.md)
- [Purpose and scope](../project/purpose-and-scope.md)
