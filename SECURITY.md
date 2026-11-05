# Security policy

## Reporting a vulnerability

Report suspected vulnerabilities privately through
[GitHub's private vulnerability reporting](https://github.com/BiscuitBin/alliumpy/security/advisories/new).
Please do not open a public issue for something you believe is exploitable. Include
what you did, what happened, what you expected, and a minimal input or program that
reproduces the problem.

## Supported versions

The newest `alliumpy` release on PyPI is supported. Releases track upstream's
(decision 0010): a fix ships as a new release, a `.postN` for a packaging fix or the
next upstream version, and there are no backports to older releases.

## What is in scope

- This repository's conversion layer, Python bindings, console script and packaging.
- Credential material committed to the repository.
- Tampered dependencies, tool binaries or GitHub Actions, and lockfiles that disagree
  with their manifests.

The parser and checker belong to upstream, <https://github.com/juxt/allium-tools>.
Report defects in their diagnostics upstream; upstream's advisories apply to the
wrapped code. This repository responds through a pin bump using the upstream-bump runbook
owned by T17, which is not available yet.

## What this project already does

- Every crate forbids unsafe code through `forbid(unsafe_code)` in its lint table.
- `Cargo.lock` is committed; Cargo gates that build or resolve dependencies use
  `--locked`, and wheel builds use maturin's `locked = true`. `cargo shear` accepts no
  lock flag; snapshot checks validate locks first and run offline.
- `cargo deny` checks licences, bans and sources in the gate; the separate audit
  workflow checks locked Rust dependencies against RustSec advisories.
- Tools and the compiler are pinned, and remote hooks and GitHub Actions use commit
  SHAs. The supply-chain limits are described in `docs/explanation/security-model.md`.
- The parity gate compares the wheel command's stdout and exit codes with upstream
  over the corpus.
- Secret scanning runs through the pre-commit hook where installed and on the checked
  files in `just check` and CI, with matched values suppressed from logs.
- No PyPI token is stored anywhere.

Publishing uses trusted publishing only, from `.github/workflows/release-pypi.yml`
behind the `release` environment's required reviewer, and every published file is
attested (decision 0015).
See `docs/explanation/security-model.md` for the security boundaries and rationale.
