---
title: "Deploy to GitHub Pages"
kind: "how-to"
audience: ["maintainer", "operator", "agent"]
canonical_for: ["deployment_procedure"]
requires: []
---

# Deploy to GitHub Pages

The API reference comes from both crates' rustdoc, built from main. T01 supplies the
Pages workflow under `.github/workflows/pages.yml`. The build uploads `target/doc`;
nothing is committed to a deployment branch.

The project address is <https://biscuitbin.github.io/alliumpy/>; read it back with
`gh api repos/BiscuitBin/alliumpy/pages --jq .html_url`. The site is deployed from main.

## One-time setup

Read the repository visibility and organisation plan before changing settings.
On a free organisation plan Pages needs a public repository. The maintainer made the
repository public on 2026-10-24 (T01); changing visibility or plan needs separate
authorization. The deploy job runs only for main while the repository is public.
A skipped deployment on a private repository is expected.

When visibility permits, set the Pages source to GitHub Actions and restrict the
`github-pages` environment to main. Read back `build_type`, `html_url`, and the
environment's deployment branch policy. These are repository settings, separately
authorized actions; a workflow cannot set them for itself. An unset source can cause
`Failed to create deployment (status: 404)` after a successful build.

## Where the site is served from

A project site lives beneath the repository's name on the owner's Pages host. Rustdoc's
links are relative, so the build is told nothing about `/alliumpy/` and the same tree
opens from a local directory. The site documents main and can describe unreleased work.

## What the workflow does

The `build` job checks out the repository, runs the setup action, `just check-toolchain`
and `just site`, then uploads `target/doc`. It needs `contents: read`.
The `deploy` job publishes the artefact with `pages: write` and `id-token: write`;
it checks nothing out and runs no repository code. Identity tokens replace stored secrets.
The public-visibility condition and the main-ref condition guard that job.

Deployments are serialised and never cancelled mid-flight. The concurrency group carries
the ref so a manual build on another branch cannot replace a waiting main deployment.
Environment branch rules provide another guard. Neither job is a gate; a failed deployment
blocks no merge.

## Reproduce a deployment locally

```console
just site
```

Open `target/doc/index.html`. It links to `alliumpy_core/index.html` and
`alliumpy/index.html`. The recipe empties `target/doc`, uses `just doc` with warnings
as errors, and writes the root index that stable rustdoc does not supply.

## Rolling back

Re-run the last good deployment from Actions, or revert the commit and let the next
main push rebuild. There is no state to migrate and no cache to clear beyond the browser's.

## Related pages

- [Decision 0008](../decisions/0008-api-reference-on-github-pages.md)
- [API reference](../reference/api.md)
- [Maintenance](../operations/maintenance.md)
