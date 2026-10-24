---
title: "Decision 0008: The API reference on GitHub Pages, when the repository's visibility allows it"
kind: "decision"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["decision_api_reference_on_pages"]
requires: []
---

# Decision 0008: The API reference on GitHub Pages, when the repository's visibility allows it

Carried from pachinko's decision 0013 at `bf51e0d`, which carried libpawdoku's decision 0016 at `ccdd001`.

## Context

The API reference is the one rustdoc generates, and reading it locally takes a clone and
`just doc`. Both crates are `publish = false`, so docs.rs holds nothing. The repository
is private. On a free organisation plan, Pages needs public visibility; a suitable paid
plan is the alternative. T01 must resolve that with the maintainer first.

## Decision

**When enabled, the site is rustdoc alone, from `main`, on every push, as a project
site.** [Deploy to GitHub Pages](../how-to/deploy-to-github-pages.md) owns the expected
address and how to confirm it. There is no site generator; the handbook stays on GitHub.

**It is built by `just site`**, which empties `target/doc`, runs `just doc` with the
gate's own flags, and adds a root `index.html` that links both crates, because stable
rustdoc writes none. No second build of the documentation exists: what is hosted is what
the doc gate proved.

**The deploy design has a workflow of its own**, `.github/workflows/pages.yml`. Its
build job holds `contents: read`. Its deploy job runs only for `main` when the
repository is public, holds `pages: write` and `id-token: write`, checks nothing out and
runs no code from the repository.

**The push is the authorisation.** `AGENTS.md` lists deploying among the actions that
need explicit authorisation each time, and pushing beside it. A deployment here follows
from a push to `main`, whether typed or made by GitHub when a pull request merges.
Pushing is on that list already, and merging a pull request is the maintainer's own act,
so no action an agent takes deploys on its own. Starting the workflow by hand from
`main` is a deployment and is authorised as one.

The workflow has three guards because a manual branch build must not publish:

- The deploy job carries a condition on `main` and public repository visibility. A setting can be changed
  where no reviewer sees it; a line in the workflow cannot.
- The concurrency group carries the ref. A group keeps one run waiting and a newer one
  takes its place, so one group for every ref would let a run from another branch, which
  deploys nothing, displace a waiting deployment of `main`.
- The `github-pages` environment's branch rule is checked by hand before the first
  deployment and admits `main` alone, as
  [Deploy to GitHub Pages](../how-to/deploy-to-github-pages.md) records.

Turned down:

- **A site generator for the handbook.** A second tool and a second build, for a
  handbook whose frontmatter and manifest are made for GitHub's rendering.
- **Publishing on release only.** Readers should not need to wait for T14.
- **A tree per version.** These crates are not headed for crates.io; a versioned site
  would be a separate build and hosting policy.

## Consequences

The ones that hurt.

- **The first workflow that holds a write scope.** Every sentence that said the
  workflows only read had to be reworded, and the security model now has a job to
  describe rather than an absence.
- **The site describes `main` and says so nowhere on its pages.** Rustdoc prints the
  crate's version and nothing about the branch, so a reader may find an item no release
  has. Only the handbook says it.
- **The handbook's explanations are not on the site.** A reader of the hosted reference
  who wants the reasoning follows a path to GitHub.
- **A branch that differs from `main` only in case is not told apart.** Expressions and
  concurrency groups ignore case, so a hand-started run from a branch named `Main`
  passes the deploy job's `if:` and shares `main`'s group. The environment's rule is
  then the only guard, and that is the setting the `if:` was written not to lean on.
  Nothing in an expression compares with case, so the workflow cannot close this itself.
- **Two settings live outside the repository.** The Pages source and the environment's
  rule are not in any file, so no gate reads them.
- **The build installs the whole gate's tooling to run one `cargo doc`**, because the
  setup action is the one tested path to `just` and the pinned toolchain.

## What would reopen this

Publishing the handbook as a site. A third documented crate requiring a different root
index. A custom domain for this repository. A need for versioned documentation. A change
of repository visibility or plan, which requires reconsidering whether deployment is
available and the workflow condition fits.

## Related pages

- [Deploy to GitHub Pages](../how-to/deploy-to-github-pages.md)
- [API reference](../reference/api.md)
- [Security model](../explanation/security-model.md)
- [Quality gates](../reference/quality-gates.md)
