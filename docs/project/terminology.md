---
title: "Terminology"
kind: "project"
audience: ["contributor", "maintainer", "operator", "agent"]
canonical_for: ["project_terminology"]
requires: []
---

# Terminology

These words mean one thing here. Using them loosely is how a review ends up arguing
about vocabulary instead of behaviour. When this glossary and upstream disagree on an
Allium term, upstream is right and this glossary is corrected.

## The repository

| Term | Meaning and preferred usage |
| --- | --- |
| Repository | This whole source tree and its engineering contract; use repository, not package, for it. |
| Core crate | `alliumpy-core`, the interpreter-independent conversion layer; use core, not bindings. |
| Bindings crate | `alliumpy`, the thin pyo3 Cargo member; use bindings crate, not Python package. |
| Python package | The importable `alliumpy` tree; use package, not crate, for Python imports. |
| Wheel | The built `.whl` installation artefact; use wheel, not sdist or binary, for it. |
| Sdist | A source distribution requiring a build; use sdist, not wheel; S01 recommends shipping it (decision 0014, T13). |
| abi3 | CPython's stable ABI used from the declared Python floor; use abi3, not universal, for its compatibility. |
| Console script | The installed `allium` entry point; use command or console script, not package name, when invoking it. |
| Upstream | `juxt/allium-tools`, which defines parser and command behaviour; use upstream, not this repository, for that authority. |
| Upstream pin | The exact `allium-parser` dependency version; use pin, not a floating range. |
| Parity | Byte-for-byte stdout and equal exit status against the pinned CLI over a corpus (T13); use parity, not proof of all possible inputs. |
| Gate | A check that must pass before hand-back; use gate, not test, for the aggregate policy. |
| Recipe | One named `Justfile` command; use recipe, not gate, when it is outside `check`. |

## Allium terms

| Term | Meaning and preferred usage |
| --- | --- |
| Module | Upstream's documentation defines an Allium module; use module, not Python module, in this context, and this repository converts, never reinterprets it. |
| Diagnostic | Upstream's documentation defines a diagnostic; use diagnostic, not exception, for parser output, and this repository converts, never reinterprets it. |
| Severity | Upstream's documentation defines severity; use severity, not local priority, and this repository converts, never reinterprets it. |
| Finding | Upstream's documentation defines a finding; use finding, not a new local diagnostic category, and this repository converts, never reinterprets it. |

Upstream's documentation in juxt/allium-tools defines the language and diagnostic codes.
Codes move with upstream releases, so this glossary does not enumerate them.

## Related pages

- [Purpose and scope](purpose-and-scope.md)
- [API reference](../reference/api.md)
