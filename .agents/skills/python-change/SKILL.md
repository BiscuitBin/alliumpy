---
name: python-change
description: Implement or review a change to the docmirror package, its tests or the console script with the golden, pytest and wheel-smoke evidence the invariants require.
---

# Change the Python package

1. Read `AGENTS.md` and the build prompt's section for the stage you are changing. The
   pipeline is `fetch -> extract -> normalize -> convert -> links -> quality -> index`,
   and every stage after fetching is a pure function of its input so it can be tested
   from a fixture without the network.
2. Decide where the change lands: a selector belongs in a profile, never in code
   (invariant 2); a Markdown fidelity rule belongs in one `normalize/` module with one
   golden test; a published artefact's shape belongs in its pydantic model so
   `docmirror schema` follows; a flag belongs in the Typer signature and the config
   override map together.
3. Write the test first and watch it fail: a unit test under `tests/unit/`, or a syrupy
   golden test under `tests/golden/` over a fixture captured under
   `tests/fixtures/<profile>/` with its `url.txt`. Live behaviour goes under
   `tests/live/` behind the `live` marker; an oracle comparison under `tests/oracle/`.
4. Keep the stage synchronous and typed; `mypy --strict` passes on the package, and a
   library without types is wrapped in one module that owns the `Any` boundary.
5. Run `just py-lint`, `just py-typecheck`, `just py-test` and `just wheel-smoke`, in
   that order, then `just check`. A changed snapshot is reviewed with
   `just py-test-accept` and explained in the commit; never accept a diff you did not
   read.
6. Report by `file:line`: what changed, which fidelity rule or site behaviour it
   serves, and the fixture that proves it.
