---
title: "Decision 0004: Dependency policy: caret ranges and `Cargo.lock`"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_dependency_policy"]
requires: []
---

# Decision 0004: Dependency policy: caret ranges and `Cargo.lock`

Carried from pachinko's decision 0007 at `bf51e0d`, which carried libpawdoku's decision 0007 at `ccdd001`.

## Context

An application's manifest can be the last word on its resolution. A library's manifest
is a constraint every consumer inherits. Exact patch pins in otherwise compatible ranges
can prevent consumers from resolving a common dependency. Even though these crates are
not published, a workspace-wide range policy keeps that distinction explicit.

Two further facts shape the mechanism. The gate runner snapshots the worktree between
recipes and aborts on any change, so no recipe may rewrite `Cargo.lock`. Every
dependency addition also needs a rationale under this decision.

## Decision

Third-party dependencies use full `x.y.z` caret ranges in one
`[workspace.dependencies]` table; member manifests inherit them with `workspace = true`.
The bindings declare the local `alliumpy-core` dependency with its path and version in
their own manifest. `Cargo.lock` is committed and is the pin. Every cargo
invocation in a gate that resolves dependencies carries `--locked`, so a recipe that
would need to change the lockfile fails instead, and `just lock-check` proves the
lockfile matches the manifests. The snapshot recipes are the one exception. cargo-insta
1.48.0 hands trailing options to nextest's test binaries, and cargo has no config
equivalent of `--locked`, so those recipes depend on `lock-check` and run offline, as
[Configuration](../reference/configuration.md) records under `CARGO_NET_OFFLINE`.
cargo-deny checks licences, bans and sources offline at gate 12 of `just check`, and
checks advisories in `just audit`, which runs in CI only, because the RustSec fetch can
fail for reasons unrelated to the diff. `cargo-shear` fails the gate on a dependency
nothing uses. `rust-version` follows the toolchain pin until the crate is first
published. There is no `.cargo/config.toml`: `RUSTFLAGS` set there changes fingerprints
and thrashes the build directory against rust-analyzer.

The one deliberate exception is `allium-parser = "=3.6.1"`: upstream behaviour is the
product being packaged, and [decision 0011](0011-exact-pin-on-allium-parser.md) owns the
reason for its exact pin. A bump is a release, not a routine dependency update.

Two dependencies sit outside the shipped graph
([decision 0016](0016-mutation-bench-and-fuzz.md)). divan is a development dependency of
the core, in `[workspace.dependencies]` like every other range, so it is outside the
graph the wheel resolves and outside cargo-deny's, which excludes development
dependencies. libfuzzer-sys is a full caret range in `fuzz/Cargo.toml`, a crate
outside the workspace that is never published or shipped; it cannot use
`[workspace.dependencies]`, and its own committed `fuzz/Cargo.lock` is its pin, under the
same `--locked` rule through `sync`, `lock-check` and the fuzz recipes' offline guard.

## Consequences

The consequences that hurt. Tests and shipped wheels use the locked Rust resolution;
wheel installers do not resolve the Rust caret ranges. That tests only one resolution,
not every version those ranges permit. If the core is later consumed as a Cargo library
outside this workspace, a consumer may resolve a dependency version never tested here.
Nothing updates any pin until T17 adds Renovate, so the lockfile ages
deliberately rather than by neglect. Every addition needs a reviewed rationale recorded
beside its manifest range and under this policy. And caret ranges make `cargo update` a
real change every time it runs: a moved lockfile is a diff to read, not noise to wave
through.

## What would reopen this

A binary crate in the workspace is not a reopening: one lockfile still resolves once,
and the binary ships that resolution. Publishing may add a minimal-versions check,
because a caret range is a claim that the crate builds against its floor, and nothing
here tests that today. A native dependency in a bindings crate that must be pinned
exactly would need a recorded exception like the upstream pin, not a return to exact
pins everywhere.

## Related pages

- [Maintain dependencies](../how-to/maintain-dependencies.md)
- [Configuration](../reference/configuration.md)
- [Decision 0016: Mutation testing, benchmarks and fuzzing](0016-mutation-bench-and-fuzz.md)
