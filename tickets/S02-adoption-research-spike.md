---
id: S02
title: "Spike: research on making Allium easier to adopt"
status: open
depends_on: [T14]
parallel_with: []
branch: spike-prek-and-more
estimated_size: M
---

# S02: Spike: research on making Allium easier to adopt

## Context

A project that adopts Allium (upstream's agent skills and the `allium` command) does so
by hand today, and so does every project of ours. The maintainer wants adoption and
continued use across the life of a project to be easy: the standard Allium workflow, a
git-hook gate, a CI gate, skills that stay in step with the checker. This spike is the
research that comes before any of that is designed. It builds nothing.

Four answers from the maintainer, taken on 2026-11-17, scope it:

1. Tooling, when it is built, lives **inside alliumpy** (this repository and its wheel).
2. It is designed for **our projects first** (`BiscuitBin/pachinko`, `BiscuitBin/knarr`,
   `BiscuitBin/rove`, `steven-cutting/libpawdoku`) and stays usable by any uv or Python
   project.
3. The research looks at whether `just` has module or import features worth using, or
   whether another vehicle is better.
4. The skills side is **tool-neutral**: `.agents/skills/`, `AGENTS.md` and thin bridges,
   not one agent's plugin format.

The repository has no place for a research note other than a spike ticket: `docs/`
accepts seven page kinds and a research note is none of them
(`docs/reference/documentation-contract.md`, "The rules"), and `S01-cli-strategy-spike.md`
is the precedent for an investigation whose output is its hand-back notes.

The sources are not the lettered ones of `CONVENTIONS.md` §0, whose pins are older than
what was surveyed. This ticket cites a repository by `owner/name` and the commit read,
then the path as a code span:

| Repository | Commit or tag read | Read on |
| --- | --- | --- |
| `BiscuitBin/pachinko`, branch `ticket/t35-decide-q1-q2` | `c7cf2ae` | 2026-11-17 |
| `BiscuitBin/knarr`, `main` | `d7cf7b4` | 2026-11-17 |
| `BiscuitBin/rove`, `main` | `615d093` | 2026-11-17 |
| `steven-cutting/libpawdoku`, `main` | `e800326` | 2026-11-17 |
| `steven-cutting/biscuit_games_tooling` | tag `v0.3.0` (`6c5c07f`) | 2026-11-17 |
| `juxt/allium-tools` (the parser, the CLI, the editor tooling) | tag `v3.6.1` | 2026-11-17 |
| `juxt/allium` (the skills and the plugin) | `7f7f008` (tag `v3.16.0`) | 2026-11-17 |
| `juxt/homebrew-allium` | `a19ad88` | 2026-11-17 |
| this repository | `545e7f2` | 2026-11-17 |

A third-party repository is cited by `owner/name` and path at its default branch on the
day, because no commit was recorded for those reads. Web documentation is cited by URL,
as a code span (`CONVENTIONS.md` §11, "Paths as code spans").

## Goal

A research note, in the hand-back notes below, that a later design can start from: how
our four repositories use Allium today, what upstream provides and leaves out, how
third-party adopters gate on Allium, which mechanisms of comparable tools are worth
copying, what `just` can and cannot do for distribution, which of this repository's
invariants and decisions constrain any option, and a ranked list of options, each with
its evidence, its cost and the decision it would need. Fact and inference are kept
apart, and what was not verified is listed.

## Non-goals

- Any tooling, recipe, hook manifest, workflow, skill or handbook page. Nothing but this
  file changes.
- A drafted ticket or a drafted decision record. Unlike S01, this spike ends in ranked
  options and open questions; the maintainer chooses before anything is drafted.
- A change in any other repository, an issue or pull request anywhere, or anything filed
  upstream.
- Measuring gate timings in the four repositories, or running Claude Code, Codex or any
  skills installer to observe live behaviour. The note says where it rests on
  documentation alone.

## Files touched

| Path | Class | Change |
| --- | --- | --- |
| `tickets/S02-adoption-research-spike.md` | ticket | the research note in the hand-back notes |
| `tickets/README.md` | ticket index | the S02 row and one sentence placing it outside the waves |

No other path. `ai_tmp/` holds the survey reports and is never committed.

## Steps

1. `just initialize` (network, authorised by the maintainer on 2026-11-17 for this
   worktree) and `just check` on the untouched worktree, last line quoted as the baseline.
2. **Survey our repositories**, read-only, with `gh api` and shallow clones into empty
   scratch directories, nothing executed from them: where the specifications live, how
   the command is installed and pinned, every place it is invoked (recipes, hooks, CI),
   how the skills are vendored, how specifications connect to tests, and what friction
   the repositories record.
3. **Survey upstream and its adopters**, read-only: the install paths, the command's
   surface and exit codes, what upstream ships for hooks and CI, its release cadence, and
   how public third-party repositories that gate on Allium do it.
4. **Survey comparable tools**, from their own documentation and repositories: hook
   distribution, CI distribution, scaffolding and drift commands, and agent-skill
   distribution.
5. **`just`.** From the just manual and repository: `import`, `mod`, optional imports,
   `--justfile`, the global justfile, and whether recipes can be shipped from a wheel or
   fetched remotely; compared with a second console script in the wheel and with gating
   through the hook runner alone.
6. **Spot-check** the claims of step 4 that the options lean on, against their sources,
   and mark each as re-verified, corrected or not verified.
7. Write the note. Stage this file (the hooks read only tracked files), run `just check`
   and quote its last line.

## Acceptance criteria

- Every claim in the note carries a repository path at a commit, a path in this
  repository or a URL; every inference is labelled as one.
- Each spot-checked claim is marked re-verified, corrected or not verified.
- Each option names the evidence for it, its cost, the invariant or decision it touches
  and the decision it would need.
- `git status --short` lists only this file; `just check` is green with it staged.

## Verification

```sh
git status --short
just check
```

Expected: one line naming this file; the runner's success line.

**Authorisation required: commit, push and open a pull request.** Stop and ask
(`CONVENTIONS.md` §11, "Separately authorised actions").

## Hand-back notes

### How to read this note

"Fact" below means a source was read and says so; the source is named. "Inference" is
this note's own conclusion and is labelled. Sections 1 to 4 rest on three read-only
surveys made on 2026-11-17 by subagents of the session that planned this spike; their
citations are carried here but were not re-read line by line afterwards, except where
"Spot checks" says so. Claims about this repository were re-read in the worktree at
`545e7f2`.

### 1. How our projects use Allium today

**Fact: none of the four uses the alliumpy wheel.** All four run the upstream CLI at
3.6.1 from `juxt/allium-tools` release tarballs.

**The shared package.** pachinko, libpawdoku and rove take two commands from
`steven-cutting/biscuit_games_tooling` at `v0.3.0` (its `pyproject.toml`):

- `bg-install-allium` (`src/biscuit_games_tooling/install_allium.py`) holds the pin,
  `VERSION = "3.6.1"`, and four SHA-256 values computed by hand, downloads
  `https://github.com/juxt/allium-tools/releases/download/v{version}/allium-{target}.tar.gz`
  and writes `.tools/bin/allium`. Four Unix targets, no Windows. Each worktree downloads
  its own binary before its hooks can pass.
- `bg-run-allium` (`src/biscuit_games_tooling/run_allium.py`) accepts only `check` and
  `analyse`, reads the JSON and decides the exit status itself.

The package's README calls a move of `VERSION` a major release of the package. knarr
does not depend on the package: it copied the runner in (`BiscuitBin/knarr` at
`d7cf7b4`, `scripts/checks/run_allium.py`, whose header names the `v0.3.0` commit), reads
the pin from two `tools.txt` lines, and added a `plan` mode.

**Why the wrapper exists.** Upstream's exit codes cannot gate. `BiscuitBin/pachinko` at
`c7cf2ae`, `docs/decisions/0005-project-managed-allium-cli.md`: "`allium check` exits
non-zero on warnings as well as errors but 0 on an `info` diagnostic, and `allium analyse` keys its status on
findings alone and ignores diagnostics entirely". This repository records the same
behaviour from upstream's source (`S01-cli-strategy-spike.md`, "Step 2", "Exit codes"),
and the wheel's command keeps it on purpose (invariant 1).

**Per repository.**

- **pachinko** (`c7cf2ae`). One specification, `docs/specs/pachinko.allium`. `Justfile`
  recipes `install-allium`, `check-specs` (`bg-run-allium check`), `analyse-specs`
  (`bg-run-allium analyse`) and `plan-spec`, which calls `.tools/bin/allium plan` by path
  because the wrapper has no `plan`. Two prek hooks in `.pre-commit-config.yaml`
  (`entry: pixi run --frozen bg-run-allium check`, and `analyse`), with
  `files: ^(docs/specs/|pyproject\.toml$)`. CI's `documents` job runs
  `just install-allium`, then the two recipes again after the hook gate
  (`.github/workflows/ci.yml`). Skills: seven upstream skills and the house skill
  `spec-change` under `.agents/skills/`, edited copies with no lock, with six-line
  bridges under `.claude/skills/` and `.codex/skills/`, and the skills' reference files
  moved to `allium-skill-reference/` at the root. `.claude/settings.json` is exactly
  `{"enabledPlugins": {"allium@juxt-plugins": true}}`, with no marketplace declared.
  Tests carry `// obligation:` and `// scenario:` tags; checking them against
  `just plan-spec` output is done by hand (`tickets/T28-invariant-walk.md`).
- **libpawdoku** (`e800326`). Nine specifications that import each other. The same
  recipes, hooks and CI as pachinko. A `skills-lock.json` exists and nothing checks it;
  its decision 0010 says the skills are vendored byte for byte, while its `allium`
  `SKILL.md` has the hash of pachinko's edited copy. Tests are named after the clause
  they prove (`crates/pawdoku/tests/board_rules.rs`). `tickets/T24-plan-spec-recipe.md`
  records why `plan-spec` calls the binary. Two open tickets there (C01, C02) already ask
  for a reusable CI workflow and a configurable agent contract in the shared package.
- **rove** (`615d093`). Four specifications. uv instead of pixi: recipes and hooks run
  `uv run --frozen bg-install-allium` and `uv run --frozen bg-run-allium check`. CI runs
  `just install-allium` then `just check`. `tickets/T07-allium-gate.md` lists what
  adopting Allium touched, about 25 files: `.gitignore`, `.editorconfig`,
  `.gitattributes`, `_typos.toml`, `lychee.toml`, the markdownlint configuration,
  `scripts/initialize.sh`, `ci.yml`, eight skills and sixteen bridges,
  `allium-skill-reference/`, three decision records, two handbook pages and the
  manifest.
- **knarr** (`d7cf7b4`). Eleven specifications, none importing another. The command is
  installed from `tools.txt` by a generic script; `scripts/checks/run_allium.py` reads
  the specifications path from `checks.toml`. **No prek hook for specifications**; the
  gate is `just check`. Skills: the seven upstream skills copied unedited from
  `juxt/allium` `v3.16.0` with their `references/` directories, and a `skills-lock.json`
  naming the tag, the commit and a SHA-256 per file, which the copied
  `validate_agents.py` checks in both directions
  (`docs/reference/agent-contract.md`). No plugin and no `.claude/settings.json`. Source
  modules name their contract in a header (`src/knarr/cost_mapping.gleam`).

**Comparison.**

| | pachinko | libpawdoku | rove | knarr |
| --- | --- | --- | --- | --- |
| Specifications | 1 | 9, with imports | 4, with imports | 11, no imports |
| Environment | pixi | pixi | uv | pixi |
| Install | `bg-install-allium` | same | same, through `uv run` | `tools.txt` and a script |
| Where the pin lives | the shared package | same | same | `tools.txt` |
| `check` and `analyse` | `bg-run-allium` | same | same | a copied `run_allium.py` |
| `plan` | the binary by path | same | same | `run_allium.py plan` |
| prek hook for specifications | yes | yes | yes | no |
| Skills | edited copies, no lock | edited copies, unchecked lock | edited copies, no lock | upstream `v3.16.0`, checked lock |
| Claude plugin enabled | yes, no marketplace declared | same | same | no |
| Codex bridges | yes | yes | yes | no |
| Specification to test | obligation tags, checked by hand | clause-named tests | no code yet | contract headers |

**What is copied by hand at each adoption** (fact, from rove's T07 and the four trees):
the ignore, editorconfig, typos, lychee and markdownlint entries; the recipes, hooks and
CI steps; near-identical decision records and handbook pages; the skills with a few
sentences edited per repository; in knarr, the runner and the checksums too.

**Inference.**

- pachinko's decision 0005 names what would reopen it: "A distribution channel that a
  lockfile can name". alliumpy on PyPI is one: `uv.lock` or pixi's PyPI dependencies
  would pin the hashes, on more platforms than `bg-install-allium` supports, with no
  per-worktree download. The JSON-reading gate is still needed, because the wheel keeps
  upstream's exit codes.
- Three repositories load both the plugin and the vendored skills, so an agent may see
  two versions of one skill; and with no marketplace declared, the plugin probably loads
  only where the user added upstream's marketplace themselves ("Spot checks" has what
  the documentation says).
- Nothing automates the link from a specification to its tests in any of the four, and
  each chose a different convention. That is a candidate for later work, not a packaging
  problem.

### 2. What upstream provides and what it leaves out

Upstream is two repositories with separate version series: `juxt/allium-tools` (parser,
Rust CLI, a Node language server, the VS Code extension) at `v3.6.1`, released
2026-08-26, and `juxt/allium` (skills, agents, hooks, plugin manifests) at plugin
version 3.16.0 (`.claude-plugin/plugin.json` at `7f7f008`).

**The command** (`juxt/allium-tools` at `v3.6.1`, `crates/allium/src/main.rs`; the same
facts are in `S01-cli-strategy-spike.md`, "Step 2"):

- `check`, `analyse`, `parse`, `plan`, `model`, `help`. No other flag than `--help` and
  `--version`. No `init`, no `fmt`, no configuration file, no environment variable.
- Output is JSON only: `check` and `analyse` print one pretty object per file, back to
  back, not an array. No SARIF, no text format, no severity flag.
- `check` exits 1 on any error or warning and 0 on `info`; `analyse` exits 1 only on
  findings; 2 means no input or an unknown command.
- `check` and `analyse` build their cross-module context from the set of files they are
  given, and since 3.6.1 import resolution also consults the filesystem (`CHANGELOG.md`).
- Suppression is an inline comment only (`-- allium-ignore <code>`,
  `crates/allium-parser/src/analysis.rs`).
- `--fail-on`, `--min-severity`, `--format text|json|sarif`, `--baseline`, `--changed`,
  formatting, diagrams and rule-to-test tracing exist only as Node scripts in the
  extension's source (`extensions/allium/`), which read `allium.config.json` and are
  shipped in no release asset and no npm package. The README's feature table credits
  the CLI with some of them.

**Hooks and CI.**

- One pre-commit hook: `juxt/allium` at `7f7f008`, `.pre-commit-hooks.yaml`, with
  `id: allium-check`, `entry: allium check`, `language: system`, `files: '\.allium$'`,
  `pass_filenames: true`. Because the language is `system`, a `rev` pins the skills
  repository and never the CLI. It passes only the changed files. Inference: that loses
  the cross-module context, since the context is built from the files given
  (`Ragazoor/dispatch-tui`, `scripts/check-allium.sh`, says a file checked alone reports
  `use.unresolvedPath` on every `use`).
- A post-edit agent hook, `hooks/hooks.json` running `hooks/allium-check.mjs`, which
  needs Node.
- No GitHub Action and no CI recipe for consumers in either repository.

**Distribution.**

- Homebrew, `cargo install allium-cli`, release binaries for five targets, AUR.
- The release's `SHA256SUMS.txt` covers the `.vsix` and the language-server tarball, not
  the CLI binaries (`scripts/build-release-artifacts.sh`). The Homebrew formula has
  `sha256 ""` for two targets (`juxt/homebrew-allium` at `a19ad88`, `Formula/allium.rb`).
  Nothing is on npm.
- `allium-cli` depends on `allium-parser` by caret range, so `cargo install` without
  `--locked` can resolve a newer parser.

**Versioning.**

- Patch releases change what passes. The 3.6.1 `CHANGELOG.md` says "two of the changes
  can turn a previously green gate red on upgrade".
- A `v4` branch, read on the day with no commit recorded, changes the exit semantics so
  that, in its words, "a well-formed spec produces zero warnings".
- The skills (3.16.0) and the CLI (3.6.1) are versioned separately; nothing states which
  skills release goes with which CLI release.

**Skills.** Seven skills (`allium`, `elicit`, `distill`, `propagate`, `tend`, `weed`,
`witness`) and five agents. Install routes: the Claude Code and Codex plugin through
the `juxt/claude-plugins` marketplace, `npx skills add juxt/allium` for other agents, or
copying. Upstream's loop keeps its state in a git-ignored `.allium-loop/` directory
(`README.md` at `7f7f008`).

### 3. How third-party adopters gate on Allium

Adoption is sparse: about 15 to 20 public third-party repositories show real use, from
GitHub code search on 2026-11-17, which was cut short by rate limits and is approximate.
Fact: every one found that gates on Allium wrote its own install step and its own
severity filter.

| Repository | Install | Gate |
| --- | --- | --- |
| `ravenoak/layerforge` | `curl` of the release tarball with a SHA-256 it computed itself (`.github/workflows/tests.yaml`) | `scripts/check_specs.sh` ignores the exit code, filters the JSON with `jq`, one file at a time |
| `Ragazoor/dispatch-tui` | `cargo install allium-cli --locked --version 3.6.1` | `scripts/check-allium.sh`: a warning baseline, a minimum-version check, a count of JSON documents |
| `OPeyrusse/katan-alysis` | `cargo install allium-cli` | `scripts/check-specs.sh` wraps `analyse`; its own `sh` post-edit hook, `.claude/hooks/allium-check.sh`; a `skills-lock.json` with hashes and no commit |
| `rtclauss/hass-config` | `curl` of 3.2.3 with a SHA-256 | `scripts/allium_weed_check.py`: a deterministic gate that maps specifications to implementation paths and takes `--changed-from` |
| `ravenoak/oh-my-stigmergy` | cargo, pinned in a file | its CI broke when a parser patch release changed an API and dropped a syntax (`docs/distillation/waivers/2026-08-21-ci-unblock-allium-locked.md`) |

Three adopters (`OPeyrusse/katan-alysis`, `ravenoak/oh-my-stigmergy` and the
`johanolofsson72` repositories) rewrote upstream's Node post-edit hook in `sh`.
`DataDog/datadog-agent` carries a static copy of the skills with no lock and no gate.

**Inference: the repeated work is the same everywhere, ours included.** An install step
with a pin and a checksum; a gate that reads the JSON instead of trusting the exit code;
checking the whole specification set and not only the changed files; a post-edit hook
without Node; and a record of which skills version is vendored. The wheel on PyPI
already answers the first. The rest is what an adoption effort has to supply.

### 4. Mechanisms worth copying from comparable tools

Each line names the mechanism, its source and whether "Spot checks" re-read it.

**The command line to print everywhere.** PyPI `allium` is an unrelated package
(decision 0009; `https://pypi.org/pypi/allium/json`, re-verified), so `uvx allium` would
install the wrong thing. The form is `uvx --from 'alliumpy==X' allium ...`; uv's tools
guide shows the same shape for another package
(`https://github.com/astral-sh/uv/blob/main/docs/guides/tools.md`).

**Hook distribution.** Three shapes exist for a tool shipped as a PyPI wheel:

- A mirror repository: `astral-sh/ruff-pre-commit` holds a manifest whose hooks are
  `language: python` and a placeholder `pyproject.toml` with `dependencies =
  ["ruff==X"]`; a scheduled `mirror.py` reads PyPI, rewrites the pin, commits and tags
  `vX` (re-verified).
- A placeholder package in the tool's own repository: `crate-ci/typos` keeps
  `.pre-commit-hooks.yaml` and a root `setup.py` named `pre_commit_placeholder_package`
  with `install_requires=[f'typos=={TYPOS_VERSION}']` (re-verified).
- No published hook at all: a `repo: local` hook in the consumer's configuration with
  `language: python`, `entry: allium check`, `additional_dependencies:
  ['alliumpy==X']` and `files: '\.allium$'`. prek's own test suite exercises
  `additional_dependencies` in a `repo: local` Python hook (re-verified).

prek reads the same `.pre-commit-hooks.yaml` as pre-commit; a manifest that uses only
upstream fields serves both, and prek-only fields are not recognised by pre-commit
(`https://raw.githubusercontent.com/j178/prek/main/docs/authoring-hooks.md`, re-verified). prek
installs Python hooks with `uv pip install`. identify has no tag for `.allium`, so the
match is a `files` regex and `types` stays at its default (`https://pre-commit.com/`).

**Version bots.** Renovate's `pre-commit` manager is off by default; Renovate has no
manager for `prek.toml` (a pull request for one has been open since 2026-03-30); a
custom regex manager with the `pypi` datasource can track a `uvx --from 'alliumpy==X'`
line (all re-verified; the regex itself was not run). This repository's own
`renovate.json` already uses custom regex managers for pins no native manager reads.

**CI.** `astral-sh/setup-uv` followed by one `uvx --from` step needs no action of our
own. GitHub's annotation syntax (`::error file=,line=,col=::message`) and a SARIF upload
are the two ways to put diagnostics on a pull request
(`https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands`).
**Corrected:** `astral-sh/ruff-action` does not read `uv.lock` by default. With no
`version` input it reads the nearest `pyproject.toml`, and `uv.lock` only when
`version-file` names it. The idea that survives is narrower: an action can take its
version from a file the project already has.

**Scaffolding and drift.** The patterns that make a scaffold safe to run twice:

- Write only when the file is missing, and say so otherwise (`buf config init`,
  `https://buf.build/docs/reference/cli/buf/config/init/`).
- Record a manifest of content hashes for the files the tool wrote, refresh a file only
  while its hash still matches, and refuse an edited one without `--force` (Spec Kit,
  `https://github.com/github/spec-kit/blob/main/docs/upgrade.md`).
- Compare bodies, not only version stamps, to find stale skills (OpenSpec,
  `https://github.com/Fission-AI/OpenSpec/blob/main/src/core/update.ts`).
- A command that exits non-zero on drift, for CI (`cruft check`,
  `https://github.com/cruft/cruft`; `lefthook check-install`,
  `https://github.com/evilmartians/lefthook/blob/master/docs/usage/commands/check-install.md`).
- A `doctor` command that reports the environment without changing it (`brew doctor`,
  `https://docs.brew.sh/Manpage`).

**Skills.**

- `npx skills` (vercel-labs/skills 1.9.0): `npx skills add owner/repo@v1.2.3` pins a tag
  or a full commit; `skills-lock.json` version 2 records `source`, `ref`, the full
  `commit` and a `computedHash` (a SHA-256 over the installed files) per skill; skills
  land in `.agents/skills/<name>` with `.claude/skills/<name>` as a relative symlink, or
  a copy with `--copy` (re-verified). Restoring from the lock is still
  `experimental_install`.
- `gh skill install --pin <tag|sha>` exists, in preview since GitHub CLI 2.90.0. It
  records the pin in the installed `SKILL.md` frontmatter, so it edits the skill file,
  and it writes no project lock that was found (re-verified, with that correction).
- Quint publishes its skills at the repository root so that both installers and the
  Claude Code marketplace can read one tree
  (`https://github.com/informalsystems/quint/blob/main/skills/README.md`; not
  spot-checked).
- **Claude Code does not read `.agents/skills/`** per its documentation: the skills page
  lists `.claude/skills/` and plugins only
  (`https://code.claude.com/docs/en/skills.md`, re-verified). Codex, GitHub Copilot,
  Cursor and Gemini CLI document `.agents/skills/` (read by a subagent, not re-opened).
  A bridge under `.claude/skills/` is therefore still needed, which is what our
  repositories and both installers already do.
- Claude Code plugins: a project's `enabledPlugins` does not install a plugin; each
  user installs it, and with the marketplace neither declared nor known the
  documentation describes no message at all
  (`https://code.claude.com/docs/en/plugins/loading.md`, re-verified). A `command`
  plugin source exists: a shell command that prints a plugin directory, run at install,
  at update and once per session
  (`https://code.claude.com/docs/en/plugins/marketplace-reference.md`, re-verified).

### 5. `just` integration options

Facts, from the just README at `casey/just` `62784c2a` (the source of the manual at
`https://just.systems/man/en/`), its `CHANGELOG.md` and `GRAMMAR.md`, read 2026-11-17;
"observed" means run with just 1.59.0 in a scratch directory. This repository and
libpawdoku pin just 1.58.0 and pachinko 1.59.0 (each `pyproject.toml`).

- `import 'path'` (stable since 1.18.0) merges another file's recipes into the same
  namespace. The path is absolute, relative to the importing file, or starts with `~/`.
  `import? 'path'` skips a missing file silently (1.21.0). A recipe of the same name in
  both files is an error unless `set allow-duplicate-recipes` is on (observed). Imported
  recipes run in the importer's directory.
- `mod name` and `mod name 'path'` (stable since 1.31.0) load a file as a namespaced
  module, run as `just name recipe` or `just name::recipe`. Each module has its own
  settings and cannot use another module's variables. Module recipes run in the module
  file's directory unless marked `[no-cd]` or the module sets `set no-cd` (1.51.0).
  `mod? name` tolerates a missing file; recipes that depend on it are disabled (1.52.0).
- An import or module path is a string literal, not an expression. A shell-expanded
  string, `x'$VAR/file.just'` (1.27.0), may use an environment variable; a just
  variable, a backtick command or a format string is a parse error (grammar; observed).
- There is no remote import. A URL fails with "could not find source file for import"
  (observed). The manual's "Remote Justfiles" section is a workaround: an optional
  import plus a recipe that fetches the file. The maintainer declined the feature in
  `https://github.com/casey/just/issues/1799` and again in
  `https://github.com/casey/just/issues/3285` (2026-04).
- `--justfile`, `--working-directory`, `--global-justfile` and the global fallback
  justfile are per-user or per-invocation. None lets a project say "also load the
  recipes an installed package provides".

One precedent for shipping recipes in a package was found, in npm:
`sablier-labs/lockup` at `546e66b` imports `./node_modules/@sablier/devkit/just/evm.just`.
None was found for a Python wheel, a copier template or a cruft template; the search was
one query deep.

**The four vehicles compared (inference).**

| Vehicle | Works because | For | Against |
| --- | --- | --- | --- |
| (a) A console script writes a `.just` file into the project, which loads it with `mod` | relative paths; this is the manual's fetch-then-import pattern with the wheel as the source | works offline and before any environment exists; reviewable in the consumer's diff; namespaced; a `--check` mode gives a drift gate | a second copy that can go stale; the wheel owns a generator; the module needs `set no-cd`, a floor of just 1.51.0 |
| (b) `mod?` pointing at a file inside the virtual environment | a wheel's `data` directory unpacks to a fixed path under the environment | no copy in the project | absent before the first sync and then silently missing; useless under `uvx`; assumes `.venv`; the path cannot be computed in the justfile; recipes change with the lock and no diff shows it. Not built or tested |
| (c) An ordinary recipe that calls a console script | nothing beyond a recipe | one visible pin; no coupling to just's features; the same line works in Make or CI; a regex manager can bump it | each project writes its own recipes |
| (d) The hook runner is the gate and `just` calls `prek run` | prek and pre-commit read one manifest | one pin per repository; runs on commit and in CI | hooks are file-driven, so a whole-set check needs `pass_filenames: false`; no bot reads `prek.toml` |

**Reading (inference).** just has nothing that makes a wheel's recipes appear in a
project, so `just` is not the distribution vehicle. Our repositories need three
recipes (`check-specs`, `analyse-specs`, `plan-spec`), and with a console script that
gates correctly each is one line. (c) for the recipes and (d) for the commit gate cover
the need; (a) is worth its generator only if the recipe set grows; (b) is not worth
pursuing.

### 6. Constraints from this repository's invariants and decisions

- **Invariant 1 and decision 0014.** The wheel's `allium` command has stdout and
  exit-code parity with `allium-cli` at the pin, proved by `just parity`. So `init`,
  `doctor`, a strict gate mode, a severity flag or a new output format cannot be
  subcommands or flags of `allium` without a decision record that narrows the invariant.
  Inference: a second console script in the wheel is the vehicle that leaves the
  invariant alone, because parity is stated for the `allium` command, not for the wheel.
- **Invariant 9 and decision 0010.** The wheel's version is upstream's, with `.postN`
  for a packaging-only release; tags are `vX.Y.Z` and `vX.Y.Z.postN`
  (`docs/decisions/0015-release-process.md`), and a tag is a release. The wheel on PyPI
  is plain 3.6.1 today (`https://pypi.org/pypi/alliumpy/json`, re-verified). Three
  consequences, the first from the packaging specification
  (`https://packaging.python.org/en/latest/specifications/version-specifiers/`, of which
  only part was read verbatim) and the others inference:
  - `alliumpy==3.6.1` does not match `3.6.1.post1`; `alliumpy==3.6.1.*` does. A pinned
    consumer never receives a packaging fix until its pin moves.
  - Anything new the wheel carries beyond upstream's behaviour (a second script, a hook
    manifest) can change only in a `.postN` or an upstream bump, so a fix to our own
    gate logic is a `.postN` release. Adoption tooling would make `.postN` releases
    routine where today they are rare.
  - `allium --version` prints upstream's string without the suffix, so a version check
    in a consumer must read the installed distribution's metadata, not the command.
- **Invariant 8 and decision 0004.** A new dependency needs its note. A gate script that
  reads JSON needs none in Python (the standard library) and none in Rust (`serde_json`
  is already in the core).
- **Invariant 2 and the stub rule.** New Python surface means the stub, a pytest case
  and the wheel smoke move with it (`AGENTS.md`, the Python block).
- **Decision 0013.** This repository keeps no specification gate and no Allium skills of
  its own, so nothing built here would be exercised here by daily use. Its reopening
  condition is "A way to run a specification gate through this repository's own
  installed wheel, proving the selected executable and retaining an offline,
  reproducible gate"; a gate script in the wheel is a step towards meeting it.
  Shipping upstream's skills inside the wheel would reopen it outright, and would tie a
  skills release (3.16.0) to a CLI release (3.6.1) that upstream versions separately.
- **Decision 0009.** The package and the command have different names; every snippet
  must carry `--from`.
- **The root `pyproject.toml` is the tooling project** (`name = "alliumpy-tooling"`, the
  pixi manifest), not the wheel, whose manifest is `crates/alliumpy/pyproject.toml`. A
  `language: python` hook published from this repository makes the hook runner run
  `pip install .` at the root. Inference: the root would have to become a placeholder
  that depends on `alliumpy==X`, as typos' root does, or the install would fail or try
  a source build; that adds one more copy of the version for `just version-check` to
  hold, and the tag exists before the wheel is on PyPI. Not tested.
- **The scoping answers.** "Inside alliumpy" rules out a separate mirror repository
  such as ruff's. "Tool-neutral" rules out making a Claude Code plugin the primary
  skills channel.

### 7. Ranked options for alliumpy

The ranking is inference throughout: it weighs how much hand work in sections 1 and 3 an
option removes against its cost and the decisions it needs. Sizes are rough (S, M, L)
and unmeasured.

| Rank | Option | Evidence | Cost | Touches | Decision it would need |
| --- | --- | --- | --- | --- | --- |
| 1 | **Document the adoption recipe**: the `uvx --from` form, a `repo: local` hook that checks the whole specification set (`pass_filenames: false`), a `setup-uv` CI step, a Renovate regex manager for the pin | every adopter wrote these by hand (sections 1, 3); all parts exist today | S: one how-to page | the handbook manifest | none; but without option 2 the hook inherits upstream's exit codes, so it cannot be the whole answer |
| 2 | **A second console script in the wheel that gates**: runs `check` and `analyse` over a path, reads the JSON, exits by a stated policy; later an annotation format | the wrapper is rebuilt in the shared package, in knarr and by four third-party adopters; upstream's own version is unshipped Node | M: Python over the vendored command, stub, pytest, smoke, a how-to | invariant 1 (kept, if the script is not `allium`), invariant 9 (`.postN`) | a decision record: the script's name, that it is outside parity, its exit policy, and how it tracks upstream's `v4` exit changes |
| 3 | **Move our four repositories from the tarball to the wheel**, pinned in their lockfiles | pachinko's decision 0005 reopening condition is met; removes hand-computed checksums, the per-worktree download and the four-target limit | M, outside this repository: the shared package and four repositories | none here | the maintainer's, per repository; whether `bg-run-allium` stays or option 2 replaces it |
| 4 | **Skills pinned by tag with a checked lock, tool-neutral**: adopt one of knarr's model or `npx skills` with `skills-lock.json` version 2, and move house sentences out of the skill bodies into `AGENTS.md` | three repositories carry edited copies with no checked lock; knarr shows unedited copies with a two-way check work; lock v2 records the commit | M: mostly in the consuming repositories; here, at most a documented procedure or a check in the second script | decision 0013 if anything ships in the wheel | which lock format; whether alliumpy states the skills tag that goes with a wheel version |
| 5 | **A hook manifest in this repository** (`.pre-commit-hooks.yaml`, `language: python`, upstream fields only) | one `rev` then pins the checker, which upstream's `system` hook cannot | M: the root project becomes a placeholder; a version copy; a test that the hook installs a wheel and not a source build | the root `pyproject.toml`, invariant 9 | whether the root may double as a placeholder package, or the `repo: local` hook of option 1 is enough |
| 6 | **Scaffold and drift commands in the second script** (`init` that writes only missing files with a hash manifest; a check that exits non-zero on drift) | rove's adoption touched about 25 files; the safe-rerun patterns are in section 4 | L: templates for ignore files, hooks, CI and recipes; our repositories differ (pixi and uv) | invariant 9; decision 0013 if it writes skills | what the scaffold owns; whether templates serve pixi, uv or both |
| 7 | **A post-edit hook entry point without Node**, in the second script | three adopters rewrote upstream's `.mjs` in `sh` | S after option 2 | none new | per-agent configuration is not tool-neutral; which agents to document |
| 8 | **A composite action or reusable workflow in this repository** | upstream ships none | S to M | CI here would need to test it | probably none; option 1's `uvx` step may be enough |
| 9 | **A vendored `just` module written by the second script** (vehicle (a) of section 5) | just has no native way to ship recipes | M | a floor on the consumer's just version | only if the recipe set outgrows three one-line recipes |

**Not recommended, with the reason.**

- New subcommands or flags on `allium` itself: invariant 1.
- A separate mirror repository for hooks: scoping answer 1.
- A Claude Code plugin backed by a `command` source as the skills channel: scoping
  answer 4, and it matches skills to whatever `allium` is on the user's `PATH`, not to
  the project's pin (inference; not run).
- Shipping upstream's skills in the wheel: decision 0013, and the two version series.
- `mod?` into the virtual environment: section 5, vehicle (b).
- Formatting and rule-to-test tracing: they exist only in upstream's TypeScript and
  belong upstream.

**A possible order (inference).** Rank is value against cost, not sequence: option 1 is
ranked first because it is nearly free, but it is not the first to build. Option 2
first, because options 1, 3, 5, 6 and 7 are all better with a command that gates correctly; then 1 and 3 together, which is the
point at which our repositories stop carrying their own installer; then 4. Options 5 to
9 wait for evidence that the simpler form is not enough.

### Spot checks

Made on 2026-11-17 against the sources named; "re-verified" means the source was
fetched again and says what the survey reported.

| Claim | Verdict | Source |
| --- | --- | --- |
| prek reads pre-commit's hook manifest; one manifest with upstream fields serves both; `prek.toml` exists beside the YAML configuration | re-verified | `https://raw.githubusercontent.com/j178/prek/main/docs/authoring-hooks.md`, `docs/configuration.md` |
| `additional_dependencies` works in a `repo: local` Python hook under prek | re-verified | `https://raw.githubusercontent.com/j178/prek/main/crates/prek/tests/languages/python.rs` |
| Claude Code has a `command` plugin source | re-verified; the full list is relative path, `github`, `url`, `git-subdir`, `npm`, `archive`, `command`, with no PyPI source | `https://code.claude.com/docs/en/plugins/marketplace-reference.md` |
| `enabledPlugins` in project settings does not install a plugin | re-verified; with the marketplace unknown no message is documented | `https://code.claude.com/docs/en/plugins/loading.md`, `https://code.claude.com/docs/en/settings-reference.md` |
| `skills-lock.json` version 2 records the commit | re-verified; also `ref` and a SHA-256 `computedHash`; pin syntax is `owner/repo@tag` or a full commit | `vercel-labs/skills` at `57217cf`, `src/local-lock.ts`, `docs/commands.md` |
| `gh skill install --pin` | re-verified, corrected in one respect: the pin is written into the installed `SKILL.md` frontmatter, not a project lock | `https://cli.github.com/manual/gh_skill_install`; `cli/cli` at `e121949`, `internal/skills/frontmatter/frontmatter.go` |
| Claude Code does not read `.agents/skills/` | re-verified from documentation only | `https://code.claude.com/docs/en/skills.md` |
| Renovate: `pre-commit` manager off by default; no `prek.toml` manager; a regex manager can use the `pypi` datasource | re-verified; the regex was not run | `renovatebot/renovate`, `lib/modules/manager/pre-commit/readme.md`, `lib/modules/manager/custom/regex/readme.md`; `https://github.com/renovatebot/renovate/pull/42254` |
| `astral-sh/ruff-action` reads its version from the project's lockfile | **corrected**: `pyproject.toml` by default; `uv.lock` only through `version-file` | `https://raw.githubusercontent.com/astral-sh/ruff-action/main/README.md` |
| `astral-sh/ruff-pre-commit` is a mirror whose tags track releases; typos uses a placeholder package | re-verified; typos' own page says "GitHub releases" while its `setup.py` installs the PyPI wheel | the two repositories' `.pre-commit-hooks.yaml`, `mirror.py`, `setup.py` |
| PyPI `allium` is unrelated; `alliumpy` is at 3.6.1 with no `.postN` | re-verified | `https://pypi.org/pypi/allium/json`, `https://pypi.org/pypi/alliumpy/json` |

### What was not verified

- **Sections 1 to 4 rest on survey reads that were not repeated.** The quotes and paths
  are as the surveys reported them; in section 4 only the rows of "Spot checks" were
  read again. Third-party repositories were read at their default branch with no commit
  recorded.
- Live behaviour of Claude Code: plugin loading, the `command` source, skill discovery.
  Everything said about it is from its documentation.
- `npx skills` and `gh skill` were read, not run. That `skills update` follows `ref`
  and not `commit`, and that `gh skill`'s inline `skill@version` form does not mark a
  pin, are inferences from source.
- Whether `npx skills` carries upstream's `hooks/` directory.
- A wheel that ships a `.just` file in its `data` directory; whether
  `https://github.com/casey/just/pull/2917` merged; which just version added the global
  fallback justfile.
- The Renovate regex manager for `uvx --from` pins; ruff-action's resolver source.
- The `==` and `==X.*` rules for post-releases come from a fetch of the packaging
  specification that returned the "Version matching" section only in summary; the
  ordering of post-releases was read verbatim.
- Whether a `language: python` hook published from this repository's root would install
  a wheel or attempt a source build.
- Gate timings in any repository. The size of the third-party adopter population.
- That the wheel's `allium` gives our four repositories the same results as the release
  binary they run today. Parity is proved over upstream's corpus (`just parity`), not
  over their specifications.

### Handed back

- **To the maintainer.** The choice among the options of section 7, and the open points
  below. This spike drafts no ticket and no decision record by design.
- **To the maintainer.** Two stale lines found in passing, neither fixed here:
  `docs/project/purpose-and-scope.md` still says the script answers `--version` only
  until T13, and decision 0009 says "nothing has been published yet"; the wheel has been
  on PyPI since 2026-11-05 (`CHANGELOG.md`).

### Deviations

- `status: open`. `tickets/README.md` defines a spike as done when its recommendation,
  drafted record and drafted ticket body are in its notes and reviewed. This spike has
  no drafts by design, and no adversarial review (`CONVENTIONS.md` §14) has run.
- The branch is `spike-prek-and-more`, the worktree's own name, not `ticket/<id>-<slug>`
  (`CONVENTIONS.md` §11).
- The surveys of steps 2 to 4 ran before this ticket existed, in the session that
  planned it; steps 5 and 6 ran afterwards. Their reports are scratch and are not
  committed; this note is the durable copy.
- Sources are cited by repository and commit, not by the letters of `CONVENTIONS.md`
  §0, whose pins predate what was surveyed.
- The file was staged (`git add`) before the final `just check`, so that the hooks read
  it; nothing was committed.

### Verification

Network use: `just initialize` in this worktree, authorised by the maintainer on
2026-11-17; read-only `gh api`, clone and web reads by the surveys.

At `545e7f2`, untouched: `just initialize` exit 0 (`Ready. Next: just check.`);
`just check` exit 0, last line:

```text
All checks passed and the worktree is unchanged.
```

At `545e7f2` with uncommitted changes (this file only, staged): `git status --short`,
then `just check` exit 0, last line:

```text
A  tickets/S02-adoption-research-spike.md
All checks passed and the worktree is unchanged.
```

## Open points

- The name and scope of a second console script, and whether it gates by reading the
  vendored command's JSON in Python or through a new entry in the core.
- The exit policy of a gate: which severities fail, whether `analyse` findings fail,
  whether a baseline is wanted, and what happens when upstream's `v4` changes the exit
  semantics.
- Whether adoption tooling justifies routine `.postN` releases, or whether our gate
  logic should be versioned some other way that invariant 9 allows.
- Whether this repository may publish a hook manifest from its root, given that the
  root is the tooling project.
- Which skills lock our repositories standardise on, and whether house edits to skill
  bodies can move into `AGENTS.md` so that the copies stay byte-identical to upstream.
- Whether alliumpy should state which `juxt/allium` tag goes with a wheel version, when
  upstream states no such pairing.
- Whether the shared package's `bg-install-allium` and `bg-run-allium` are retired,
  kept as thin callers of the wheel, or left for repositories that have not moved.
- Whether a deterministic specification-to-test link (obligation tags, clause names,
  contract headers) belongs in this effort at all.
