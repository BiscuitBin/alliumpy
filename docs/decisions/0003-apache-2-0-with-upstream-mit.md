---
title: "Decision 0003: Apache-2.0 for this repository, upstream's MIT shipped beside it"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_license"]
requires: []
---

# Decision 0003: Apache-2.0 for this repository, upstream's MIT shipped beside it

Carried from pachinko's decision 0006 at `bf51e0d`, which carried libpawdoku's decision 0006 at `ccdd001`.

## Context

This repository distributes a Python wheel containing native Rust code and upstream's
parser. Its licence is settled before contributions arrive: relicensing later means
asking every contributor. Both Cargo crates remain `publish = false`; PyPI is the
intended registry, and no release has been made yet.

## Decision

Apache-2.0. `LICENSE` at the repository root is the licence's verbatim text; `license =
"Apache-2.0"` sits in `[workspace.package]` and every crate inherits it. No dual
MIT/Apache, no per-file headers, no `NOTICE` file.

Apache over MIT for two clauses MIT lacks. Section 3 grants every user a patent licence
from every contributor and terminates it for anyone who sues over the work, and section
5 places every contribution under the licence's terms automatically, which does the work
a contributor agreement would otherwise do. Not the Rust ecosystem's dual MIT/Apache:
that pairing exists so that MIT-only and GPLv2 consumers can take a crate, the present
distribution is a Python wrapper, and one licence is one thing to explain. No per-file
headers: the licence's appendix makes them optional, and a header is one more thing
every new file gets wrong. No `NOTICE`: section 4(d) obliges a redistributor to carry a
`NOTICE` only where one exists, and nothing here needs attribution beyond the licence
itself.

Upstream allium-tools is MIT. Its permission and attribution must travel with copies.
The wheel therefore carries both this repository's Apache-2.0 text and upstream's MIT
text, rather than pretending Apache relicenses upstream. The copies are
`crates/alliumpy/LICENSE` and `crates/alliumpy/LICENSE-allium-tools`; the latter records
upstream version and copyright. PEP 639 globs cannot leave maturin's project root, so
root-only texts would not suffice. Both enter `.dist-info/licenses/`, and T14 asserts
the released wheel's contents. [Python packaging](../explanation/packaging.md) owns the
layout.

## Consequences

Apache-2.0 is incompatible with GPLv2-only programs, which cannot link it. Accepted: no
consumer in sight is one.

Every dependency must be compatible. `deny.toml` carries an allow list of licences,
Apache-2.0 with and without the LLVM exception, MIT, the BSD family, ISC, Zlib, 0BSD,
Unicode-3.0, Unlicense and CC0-1.0, and `cargo deny check licenses` at gate 12 of `just
check` fails on any crate outside it, so a copyleft dependency cannot arrive by
accident.

A contributor's work is licensed by section 5 with no separate agreement; the repository
asks for nothing beyond the pull request.

## What would reopen this

A consumer that can only take MIT. Adding it beside Apache-2.0 would be a second licence
file, a `license = "MIT OR Apache-2.0"` line and a record superseding this one; past
contributions were made under Apache-2.0 alone, so each contributor would have to agree,
which is cheap while contributors are few and grows with every one. Or the house
choosing one licence for every repository, at which point this record follows that
decision.

## Related pages

- [Security model](../explanation/security-model.md)
- [Maintain dependencies](../how-to/maintain-dependencies.md)
