---
id: T12
title: "Maintainer docs: README, CHANGELOG, SECURITY, the crate READMEs"
status: open
depends_on: [T11, T13]
parallel_with: [T15]
branch: ticket/t12-maintainer-docs
estimated_size: S
---

# T12: Maintainer docs: README, CHANGELOG, SECURITY, the crate READMEs

## Context

The entry points come last so that they describe what exists rather than what was
planned. T00 left five stubs; after T11 the repository is integrated and green, and after
T13 the `allium` command in the wheel is proven against upstream (`CONVENTIONS.md` §9,
"The parity reference"). This ticket waits for T13 on purpose: `crates/alliumpy/README.md`
is the PyPI long description (`readme = "README.md"` in `crates/alliumpy/pyproject.toml`,
`CONVENTIONS.md` §9), and a description published by T14 must describe a command that
behaves as described.

P `tickets/T12-maintainer-docs.md` is the procedure, and P `README.md`, P `CHANGELOG.md`
and P `SECURITY.md` at `bf51e0d` are the stub shapes T00 copied; L `README.md`, L
`CHANGELOG.md`, L `SECURITY.md` and L `crates/pawdoku/README.md` at `ccdd001` are the
finished shapes. The handbook already holds the long form of everything here
(`docs/how-to/install-and-run.md`, `docs/explanation/packaging.md`,
`docs/explanation/security-model.md`, T07); the entry points point at it and never
restate it.

Wave 2 runs beside this ticket and also writes `CHANGELOG.md` lines (`CONVENTIONS.md`
§11, "Wave 2 shares files by rebasing"). This ticket owns the file's structure; a wave-2
ticket adds its own entry under `[Unreleased]` and rebases. T14 waits for this ticket,
then turns `[Unreleased]` into the `3.6.1` section and rewrites `SECURITY.md`'s "Supported
versions".

## Goal

A `README.md` that tells a newcomer what the package is, how to install and run it with
`uv` and `pip`, what the Python API looks like, that the behaviour is upstream's, how to
get from clone to green, and where the handbook is; a `CHANGELOG.md` in Keep a Changelog
form whose versions track upstream (`CONVENTIONS.md` §1 decision 4); a `SECURITY.md` that
says how to report a vulnerability and whose advisories apply; a README for the core
crate; and the crate README that becomes the PyPI long description, describing only what
the built wheel does.

## Non-goals

- No handbook page. Each entry point links to the handbook as a code-span path rather
  than restating it.
- No badge or URL for a service that does not exist yet (PyPI before T14, Pages while the
  repository is private, `CONVENTIONS.md` §1 fact 6).
- No release, version bump, tag or `release-pypi.yml` (T14); no `twine check` (T14
  runs it over the built artefacts).
- No change to `crates/alliumpy/pyproject.toml`: its `readme` key already names the file.

## Files touched

| Path | Class | Content |
| --- | --- | --- |
| `README.md` | final | what, install, API, status, quick start, handbook, licences |
| `CHANGELOG.md` | final | Keep a Changelog, upstream-tracking versions, `[Unreleased]` |
| `SECURITY.md` | final | reporting, scope, upstream's advisories |
| `crates/alliumpy-core/README.md` | final | what the core is and is not |
| `crates/alliumpy/README.md` | final | the PyPI long description |
| `tickets/T12-maintainer-docs.md` | ticket | `status:` and hand-back notes |

## Steps

1. Create the worktree after T11 and T13 have merged; rebase on any wave-2 ticket merged
   since. `just initialize` (network, authorised); `just check` on the untouched worktree,
   last line quoted as the baseline (`CONVENTIONS.md` §11). Read T01's hand-back notes. If
   they do not say private vulnerability reporting is enabled on `BiscuitBin/alliumpy`,
   **Authorisation required: the reporting contact.** Stop and ask the maintainer for the
   contact `SECURITY.md` names (a product decision) before writing step 4; record the
   question and the answer in the hand-back notes.
2. **`README.md`.** One paragraph on what the package is: the Allium parser and checker
   for Python code, and the `allium` command for `uv` users, built from upstream's
   `allium-parser` at an exact pin, with upstream as an autolink,
   `<https://github.com/juxt/allium-tools>`: lychee skips code spans unless
   `--include-verbatim` is passed, which the frozen hook does not, and a reader must be
   able to follow it (`CONVENTIONS.md` §11 "Paths as code spans" governs ticket text, not
   these five files; repository paths stay code spans). Install and run: `uvx --from
   alliumpy allium check <path>`, `uv tool install alliumpy` then `allium check <path>`,
   `pip install alliumpy`, written as what they will do once T14 has published, under one
   sentence saying so, as `docs/how-to/install-and-run.md` does (T07); the `--from` is not
   optional (`CONVENTIONS.md` §1 fact 11). T14 makes the sentence present tense. The
   Python API in five lines: only the names `__init__.py` lists in `__all__`, with
   signatures copied from `_alliumpy.pyi` and checked against it; not
   `ALLIUM_VERSION_STRING`, which the stub declares but `__init__.py` does not re-export,
   and no underscore-prefixed name (`CONVENTIONS.md` §9, "The T00 API"). A status line:
   the behaviour of the command and the diagnostics are upstream's, at the upstream
   version the package version names (decision 0010, step 3; `CONVENTIONS.md` §7
   invariant 1), without repeating the number, since `just version-check` holds the
   copies equal and the README is not one of them (`CONVENTIONS.md` §9); the platforms
   the release matrix builds (`CONVENTIONS.md` §1 decision 6, record 0012;
   `release-pypi.yml` is T14's, so they are stated as what T14 publishes) and the Python
   floor (`requires-python`). The quick start for contributors (`just initialize`,
   `just check`), with the prerequisites as a code-span path to
   `docs/how-to/develop-locally.md`; the handbook at `docs/README.md`; visibility as
   T01's hand-back notes record it: while private, one sentence saying so and that the CI
   badge (Open points) and the Pages link are omitted until that changes; if T01 made it
   public, the `ci.yml` badge and the Pages URL T01's notes name instead. The licences:
   Apache-2.0 for this repository, upstream's MIT text shipped in the wheel (decision
   0003). Agents read `AGENTS.md` first.
3. **`CHANGELOG.md`.** P's header, with `BiscuitBin/alliumpy` URLs. Replace the sentence
   about Semantic Versioning with the version policy of decision 0010: a version `X.Y.Z`
   means the wheel wraps allium-tools `X.Y.Z`, and `X.Y.Z.postN` is the Nth packaging-only
   fix of that wheel; upstream's own changes are not listed here, only this repository's.
   One `[Unreleased]` section listing the foundation in a few lines, not per ticket: the
   two crates, the gate, the Python API as it stands, the `allium` command with S01's
   route named (decision 0014), the handbook and the agent contract. Keep every
   `[Unreleased]` line T13 has already added (and T15's, if it has merged) verbatim
   beneath the foundation lines, and do not fold them into the summary (`CONVENTIONS.md`
   §11, "Wave 2 shares files by rebasing"): this ticket adds and orders lines and deletes
   or rewords nothing another lane wrote. Keep the `[Unreleased]` reference link in P's
   form, `[Unreleased]: https://github.com/BiscuitBin/alliumpy/commits/main/`; T14 adds
   the `3.6.1` heading and its link.
4. **`SECURITY.md`.** L's finished shape (L `SECURITY.md` at `ccdd001`; P's is a stub),
   with L's puzzle, solver and crates.io items dropped: how to report privately. If T01's
   hand-back notes say private vulnerability reporting is enabled on
   `BiscuitBin/alliumpy`, point at it; if not, name the contact the maintainer gave in
   answer to step 1's question. "Supported versions": `main` only, until T14 rewrites
   it. Scope: the conversion layer, the bindings, the console script and the packaging
   are this repository's; the parser and the checker are upstream's, so a defect in a
   diagnostic is reported upstream and upstream's advisories apply, and this repository's
   response is a pin bump through the upstream-bump runbook (say the runbook is T17's,
   without naming a path: T17 lands after T14, which waits for this ticket, so the page
   cannot exist yet). What the project already does: `forbid(unsafe_code)`, `--locked`
   everywhere, `cargo deny`, pinned tools and actions, the parity gate, secret scanning on
   every commit, and no PyPI token anywhere (`CONVENTIONS.md` §11); publishing, when T14
   adds `release-pypi.yml`, is by trusted publishing only.
5. **The crate READMEs.** `crates/alliumpy-core/README.md`: what the core is (the
   conversion layer and the version constants over `allium-parser`, plus the CLI entry if
   S01 chose vendoring), that it is not published to crates.io, where its rustdoc is
   (`just doc`). `crates/alliumpy/README.md`: this is the PyPI long description, so it is
   written for a PyPI reader who has never seen the repository: it describes the wheel T14
   publishes and carries no "once T14 publishes" sentence, because it is read only after
   publication; one paragraph on what the wheel is; install and run as step 2 gives them;
   the Python API in five lines as step 2 defines them; the exit codes of `allium check`
   as upstream defines them (0, 1 on any error or warning, 2 on no inputs;
   `CONVENTIONS.md` §1 fact 5); supported platforms (decision 6) and the Python floor; the
   sdist consequence exactly as S01 ruled it (`CONVENTIONS.md` §9, "The sdist": either
   there is no sdist and an unsupported platform fails to install, or the sdist builds
   with a Rust toolchain and `uv` or `pip` will do so silently); the licences, naming both
   files in `.dist-info/licenses/`; upstream and this repository as autolinks
   (`<https://…>`), as step 2. Nothing a reader of the wheel cannot use: no `just`, no
   tickets, no handbook paths.
6. **Render check.** The long description must render on PyPI. Run
   `mkdir -p ai_tmp && .pixi/envs/default/bin/uv -q run --no-project --python .pixi/envs/default/bin/python --with 'readme-renderer[md]' python -m readme_renderer crates/alliumpy/README.md -o ai_tmp/readme.html`
   (network, authorised: `uv` fetches `readme-renderer` and its `md` extra into an
   ephemeral environment). `--no-project` keeps `uv` from treating the root
   `pyproject.toml` as a project, which would write `uv.lock` and `.venv/` into the
   worktree; the `md` extra is required, because without it `readme_renderer` prints only
   the warning to install `readme_renderer[md]` and exits 1. `-q` silences `uv`'s own
   download and install lines, which a cold cache prints to stderr on a successful run, so
   any stderr line is `readme_renderer`'s or an install error. The command must exit 0
   with nothing on stderr; `readme_renderer` exits 1 only when the `md` extra is missing
   or the file renders to nothing, so a pass proves the renderer accepted the file, not
   that every link works on PyPI; step 5's rules (no handbook paths, URLs as autolinks)
   keep relative links out and the step 7 review checks them. A non-zero exit after a
   successful install is a README defect to fix, not a reason to defer. Only if the
   quoted `uv` output shows the download or install itself failed does the hand-back
   record that T14's `twine check` is the render proof.
   `just check-docs` (markdownlint, typos, lychee offline and `bg-validate-docs`), then
   the online link check (network, authorised). While the repository is private
   (`CONVENTIONS.md` §1 fact 6; T01's hand-back notes say whether that changed), GitHub
   answers 404 to an unauthenticated request for any `BiscuitBin/alliumpy` URL, so the
   `[Unreleased]` reference link and the `SECURITY.md` reporting link fail under a bare
   `just check-links-online`. Run it as `rm -f .lycheecache` followed by
   `GITHUB_TOKEN="$(gh auth token)" just check-links-online`: lychee reads `GITHUB_TOKEN`
   (`lychee --help`, `--github-token`), the hook inherits the environment, and `gh` is
   authenticated by prerequisite (`CONVENTIONS.md` §2). The cache is removed because
   `lychee.toml` sets `cache = true` and an earlier unauthenticated run would have cached
   that 404 in the gitignored `.lycheecache` for a day, so a quoted pass could be stale.
   With the token, lychee's GitHub fallback (`check_github` in lychee-lib
   `src/checker/website.rs` at `lychee-v0.24.2`) answers OK for any path under a private
   repository once the repository itself resolves, so the token run proves only that the
   repository exists. Prove each `BiscuitBin/alliumpy` link separately:
   `gh api 'repos/BiscuitBin/alliumpy/commits?sha=main' --jq '.[0].sha'` must print a
   SHA (the `[Unreleased]` link), and, if `SECURITY.md` links private vulnerability
   reporting,
   `gh api repos/BiscuitBin/alliumpy/private-vulnerability-reporting --jq .enabled` must
   print `true`; quote both with their exit codes. Run the bare `just check-links-online`
   first (cache removed) as the positive control and quote its 404 lines, then the
   `GITHUB_TOKEN` run; quote both in the hand-back notes. `lychee.toml` is final at T00
   and not in Files touched; a link that still fails is a hand-back note, not an
   exclusion. No PyPI URL appears in the five files until T14 (Non-goals).
7. `just check`, the final adversarial review, `just check` again if fixes landed, then
   commit.

   **Adversarial review** (`CONVENTIONS.md` §14): the five files. Ask: which entry point
   describes a recipe, page, badge or link that does not exist on `main`; which sentence
   outside the install lines, the decision-6 platforms, the trusted-publishing clause and
   the sdist sentence describes a wave-2 deliverable as existing, and whether `README.md`
   and `SECURITY.md` each carry their one sentence saying those describe T14's release and
   `crates/alliumpy/README.md` carries none; whether the long description claims anything
   the wheel smoke and the parity corpus did not prove; whether the install lines match
   `[project.scripts]` and the `--from` rule; whether the sdist sentence matches S01's
   ruling; whether the API lines name only members of `__all__` and match
   `_alliumpy.pyi`'s signatures.

## Acceptance criteria

- Every link in the five files resolves (`rm -f .lycheecache` then
  `GITHUB_TOKEN="$(gh auth token)" just check-links-online` while the repository is
  private, `just check-links-online` once it is public; network, authorised). The cache is
  removed first so that the quoted result is fresh; lychee lists only failures without
  `-v` and the frozen hook passes none, so the proof that the token reached lychee is a
  positive control: a bare `just check-links-online` after `rm -f .lycheecache`, whose
  quoted output names the `BiscuitBin/alliumpy` URLs as 404, then `rm -f .lycheecache`
  and the `GITHUB_TOKEN` run, whose quoted summary shows 0 errors and exits 0.
- While the repository is private, each `BiscuitBin/alliumpy` link is proved by its
  `gh api` line in step 6, quoted with its exit code, because lychee's GitHub fallback
  accepts any path under a private repository.
- Nothing in them describes a recipe, page, badge or link that does not exist on `main`.
  The install lines, the platforms of decision 6, the trusted-publishing clause and the
  sdist sentence describe the release T14 makes: `README.md` and `SECURITY.md` say so in
  one sentence each, which T14 makes present tense, and `crates/alliumpy/README.md` says
  nothing of the kind because it is read after publication (T14 step 7 asks whether it
  names a command the wheel does not have). The `allium` commands the long description
  names are the ones T13's parity corpus covers.
- The render check in step 6 exits 0 with an empty stderr, and the hand-back notes quote
  its output. That shows only that the renderer accepted the file, so the output must also
  have rendered the Markdown: `rg -c '<h[1-6]' ai_tmp/readme.html` and
  `rg -c '<code' ai_tmp/readme.html` each print a count above zero (headings and the
  install lines came through as HTML, not as raw text); what PyPI shows beyond that is
  T14's to see on the real page. The proof is deferred to T14's `twine check`, by name,
  only when the quoted `uv` output shows the package download or install itself failed,
  never on a non-zero exit from `readme_renderer`.
- `CHANGELOG.md` states the version policy of decision 0010 and has one `[Unreleased]`
  section.
- `just check` is green.
- The adversarial reviews in Steps ran (`CONVENTIONS.md` §14), and every valid finding is
  fixed or handed back.

## Verification

```sh
just check-docs
rm -f .lycheecache; just check-links-online; echo "exit $?"   # 404 on BiscuitBin/alliumpy while private
rm -f .lycheecache
GITHUB_TOKEN="$(gh auth token)" just check-links-online
gh api 'repos/BiscuitBin/alliumpy/commits?sha=main' --jq '.[0].sha'; echo "exit $?"
gh api repos/BiscuitBin/alliumpy/private-vulnerability-reporting --jq .enabled; echo "exit $?"   # only if SECURITY.md links it
mkdir -p ai_tmp && .pixi/envs/default/bin/uv -q run --no-project --python .pixi/envs/default/bin/python --with 'readme-renderer[md]' python -m readme_renderer crates/alliumpy/README.md -o ai_tmp/readme.html 2>ai_tmp/readme.stderr; echo "exit $?"; test ! -s ai_tmp/readme.stderr && echo "stderr empty"   # must print exit 0 and stderr empty
rg -c '<h[1-6]' ai_tmp/readme.html; rg -c '<code' ai_tmp/readme.html   # each a count above zero
rg --files-without-match 'uvx --from alliumpy allium' README.md crates/alliumpy/README.md
rg --files-without-match 'uv tool install alliumpy' README.md crates/alliumpy/README.md
just check
```

Drop the `GITHUB_TOKEN=` prefix if T01's hand-back notes say the repository is public. The
two `rg --files-without-match` lines must print nothing: a path they print lacks that
install line. The render line must print `exit 0` and `stderr empty`;
`git status --short` after it must show no `uv.lock`, and `test ! -e .venv` must succeed
(`.venv/` is gitignored, so `git status` cannot show it).

## Hand-back notes

To be written by the executing agent: the link check output and the command it ran under
(with or without `GITHUB_TOKEN`), the render check's full output and exit code, the
contact or reporting path `SECURITY.md` names and who gave it, the review record for each
checkpoint (`CONVENTIONS.md` §14), and anything handed back.

## Open points

- Whether the maintainer wants a CI badge while the repository is private (it renders
  only for people who can read the repository). Omit unless the maintainer says
  otherwise.
