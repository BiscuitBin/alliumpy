---
title: "Build decisions"
kind: "explanation"
audience: ["contributor", "maintainer", "agent"]
canonical_for: ["build_choices"]
requires: []
---

# Build decisions

The build prompt fixes the stack, the scope and the index strategy and says not to ask
questions during the build: where it leaves a choice open, the agent chooses the option
that preserves more content, is more deterministic or is easier to test, in that order,
and records the choice here. Repository-level decisions with lasting consequences get a
numbered record under `decisions/`; this page is the running log of the smaller ones.

## Phase 0: the host

- The repository keeps Apache-2.0 instead of the prompt's MIT, on the maintainer's
  instruction; the dependency rule that motivated MIT (no AGPL in the default install)
  still holds, and [decision 0015](decisions/0015-docmirror-in-place-of-alliumpy.md)
  records both.
- The package ships `src/docmirror` with hatchling; the pixi environment installs it
  editable with its `dev` extra so the console script, pytest and mypy all see the
  worktree.
- The ruff rule set stays `select = ["ALL"]` as carried; the copyright-header rule is
  ignored once in `ruff.toml` because `LICENSE` carries the notice.
- Environment overrides use `DOCMIRROR_<SECTION>__<KEY>`, with a double underscore
  between section and key, because the TOML has nested sections and a single
  underscore would be ambiguous against keys such as `max_pages`.
- The flat profile keys the prompt's example uses (`tab_group`, `tab_label`,
  `tab_panel`, `admonition`, `admonition_title`) fold into the structured `tabs` and
  `admonitions` lists, so a profile can describe more than one tab shape (devsite has
  two) without a second mechanism.
- lychee comes from the pixi environment, pinned exactly, and its hooks are `local`
  entries naming that binary. Upstream's auto-installing hook resolves its download
  through the GitHub API, which the build container forbids, and a binary a hook
  fetches at first run is a pin nothing hashes; the conda-forge package is both.
- `[fetch.provider]` exists, validates, and rejects any non-empty value with a message
  saying it is reserved and not implemented.

## Related pages

- [Site notes](site-notes.md)
- [Architecture decisions](decisions/README.md)
