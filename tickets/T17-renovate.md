---
id: T17
title: "Renovate over every pin except the upstream crate; the upstream-bump runbook"
status: done
depends_on: [T14, T15]
parallel_with: []
branch: ticket/t17-renovate
estimated_size: M
---

# T17: Renovate over every pin except the upstream crate; the upstream-bump runbook

## Context

L's spike S01 compared Dependabot, Renovate and nothing, recommended Renovate through the
Mend app on condition the maintainer accepts its write access, and drafted the build
ticket: L `tickets/S01-dependency-updates.md` lines 666-905, with the evidence above it
from line 164 and the `renovate.json` draft from line 474. P `tickets/T17-renovate.md`
adapted that draft for pachinko; this ticket adapts P's, minus the container image and the
semver tooling P named, plus the pins this repository has and P does not: the Python
tools in the pixi manifest, the maturin range in `crates/alliumpy/pyproject.toml`, and the
pyo3 crate. The parity reference has no pin of its own: `install-parity-reference` reads
the `allium-parser` pin through `scripts/version_check.py --print-pin` (`CONVENTIONS.md`
§9), so it is excluded with it. The maintainer chose to carry Renovate (`CONVENTIONS.md`
§1 decision 5).

One pin is deliberately **not** Renovate's: `allium-parser = "=3.6.1"`. An upstream bump
is a release of this repository, not a dependency update (`CONVENTIONS.md` §13, first
risk): it moves the wheel version, the version constants, the parity reference, possibly
vendored code, and the CHANGELOG, and `just version-check` fails a bare pin bump by
design (`CONVENTIONS.md` §7 invariant 9). This ticket writes that bump down as a runbook,
`docs/how-to/bump-upstream.md`, so that the next upstream release is a procedure and not
a rediscovery.

It comes last because Renovate has to know every pin, and wave 2 added pins: the release
workflow's actions and any release tool (T14), cargo-mutants, divan, cargo-fuzz and the
fuzz crate's own lockfile (T15).

## Goal

`renovate.json` on `main` covers every pin in the repository except `allium-parser`,
through Renovate's native managers where one exists and a regex manager proved by a real
pull request where one does not, with the exclusion and its reason written into the
configuration; the Mend app is installed on `BiscuitBin/alliumpy` only, with its
permissions on record in the security model; `docs/how-to/bump-upstream.md` is a runbook
an agent with no other context can follow from "upstream released 3.6.2" to "the release
ticket's procedure"; the how-to and the maintenance page say what the updater proposes
and what stays manual; decision 0017 records it; and the wave-2 outcomes of
`CONVENTIONS.md` §12 are carried into its table.

## Non-goals

- No automerge (the draft's `"automerge": false`).
- No Dependabot. It is the draft's fallback; if the app is declined, stop and hand back.
- No pin moved by this ticket's own hand. Renovate's first pull requests are the proof.
- No upstream bump performed here. The runbook is written and read through, not run,
  unless upstream has released since T13 and the maintainer asks for it as a separate
  authorised action.

## Files touched

| Path | Class | Content |
| --- | --- | --- |
| `renovate.json` | new | the draft's, extended for this repository's pins, with the exclusion |
| `docs/how-to/bump-upstream.md` | new | the upstream-bump runbook |
| `docs/decisions/0017-renovate.md` | new | `CONVENTIONS.md` §8 |
| `docs/how-to/maintain-dependencies.md` | shared, own lines | what the updater proposes, what stays manual, the pin that is a release |
| `docs/operations/maintenance.md` | shared, own lines | the Monthly and "when upstream releases" entries |
| `docs/explanation/security-model.md` | shared, own lines | the app as a named holder of permissions |
| `docs/manifest.yml` | shared, own lines | two entries |
| `docs/README.md` | shared, own lines | one link under "How to"; 0017 reachable under Decisions |
| `docs/decisions/README.md` | shared, own lines | one row |
| `CHANGELOG.md` | shared, own lines | one `[Unreleased]` line |
| `AGENTS.md` | shared, own lines | the upstream-bump block: the until-then sentence replaced by the path `docs/how-to/bump-upstream.md` (`CONVENTIONS.md` §7) |
| `SECURITY.md` | shared, own lines | the scope paragraph names `docs/how-to/bump-upstream.md` where T12 wrote that the runbook is T17's |
| `tickets/CONVENTIONS.md` | correction | §12 wave-2 outcomes, through a `main` pull request |
| `tickets/T17-renovate.md` | ticket | `status:` and hand-back notes |

## Steps

1. Create the worktree after T14 and T15 have merged; rebase on any wave-2 ticket merged
   since. `just initialize` (network, authorised); `just check` on the untouched
   worktree, its last line quoted as the baseline (`CONVENTIONS.md` §11).
2. **Inventory every pin** on `main`, by file: `Cargo.toml` (`[workspace.dependencies]`:
   `allium-parser`, `pyo3`, and whatever T13 and T15 added), both crate manifests,
   `Cargo.lock`, `fuzz/Cargo.toml` and `fuzz/Cargo.lock` (T15; the crate is excluded from
   the workspace, so it is a second cargo root), `rust-toolchain.toml` and
   `rust-version`, `pyproject.toml` (`requires-pixi`, which the draft's regex manager
   reads under `prefix-dev/pixi` grouped with `pixi-version`; `python = "3.14.*"`,
   manual: the tooling interpreter of `CONVENTIONS.md` §2, not a pin to bump; every `==`
   pixi pin, the Python tools included; and the B tag), `pixi.lock`,
   `crates/alliumpy/pyproject.toml` (`[build-system] requires =
   ["maturin>=1.15,<2.0"]`), `tools.txt`, `tools-source.txt`, both prek configurations'
   revs, every remote `uses:` in `.github/workflows/` (including `release-pypi.yml`,
   `mutants.yml` and `fuzz.yml`) and `.github/actions/` (the workflows'
   `uses: ./.github/actions/setup` lines are paths, not pins; the action's own remote
   `uses:` lines are pins), `setup-pixi`'s `pixi-version`, the `python-version` inputs of
   `actions/setup-python` steps, and, if T14 set them, `maturin-action`'s
   `maturin-version` and `setup-uv`'s `version` inputs (the `github-actions` manager
   reads none of these inputs: regex manager or manual, with the reason). Mark each:
   native manager, regex manager, manual with a reason, or **excluded** (`allium-parser`;
   the parity reference has no pin of its own and follows it through `--print-pin`,
   `CONVENTIONS.md` §9).
3. **`renovate.json`.** The draft's (L `tickets/S01-dependency-updates.md` from line
   474, as P `tickets/T17-renovate.md` step 3 adapted it: `pixi-version` read by a regex
   manager over `.github/actions/setup/action.yml` (`matchStrings: ["pixi-version:
   v(?<currentValue>\\d+\\.\\d+\\.\\d+)"]`, `depNameTemplate: prefix-dev/pixi`,
   `datasourceTemplate: github-releases`, `extractVersionTemplate: ^v(?<version>.*)$`),
   and the `requires-pixi` floor by the draft's regex manager (L
   `tickets/S01-dependency-updates.md` lines 543-550), both under the one
   `prefix-dev/pixi` depName and datasource, so the two form one group, the one pixi
   group, with the native reading of the input switched off by
   `{ "matchManagers": ["github-actions"], "matchDepNames": ["prefix-dev/pixi"],
   "enabled": false }`; the `matchManagers` key is what keeps that rule off the regex
   readings, which share the depName by design, and the step-5 proof is both
   `pixi-version` and `requires-pixi` listed under `prefix-dev/pixi`; the toolchain
   grouped with `rust-version`; no `Dockerfile` here), with:
   - **The exclusion.** A `packageRules` entry `{ "matchManagers": ["cargo"],
     "matchDepNames": ["allium-parser"], "enabled": false, "description": "..." }` whose
     description says an upstream bump is a release through
     `docs/how-to/bump-upstream.md` and that `just version-check` fails a bare bump.
     Cargo cannot move an `=3.6.1` requirement in `Cargo.lock` without a manifest change,
     so lock-file maintenance cannot bump it either; step 5 proves that rather than
     assumes it.
   - **The parity reference.** No manager. T13's `install-parity-reference` reads the
     `allium-parser` pin through `scripts/version_check.py --print-pin` (`CONVENTIONS.md`
     §9), so there is no version literal for Renovate to read and nothing that could drift
     from the pin; the inventory marks it as following `allium-parser`, and the how-to's
     row for it says "moves with the pin, by the runbook".
   - **The maturin range.** `[build-system] requires` in `crates/alliumpy/pyproject.toml`
     is read by Renovate's `pep621` manager (its page lists the `build-system.requires`
     depType). Keep the range (pinning it exactly would move a pin by this ticket's hand
     and edit `crates/alliumpy/pyproject.toml`, not in Files touched): Renovate proposes
     widening or replacing it on a maturin 2.0, held for dashboard approval and grouped
     as "python build backend", and say in the rule's description that the pixi pin is
     what builds locally and in `just check`, and that the range is what a user's
     installer honours when it builds the sdist (if S01 kept it) and what
     `PyO3/maturin-action` resolves from `build-system.requires` when its
     `maturin-version` input is unset, as the generator leaves it; PyPI itself builds
     nothing.
   - **The pixi pins.** The `pixi` manager reads `[tool.pixi.dependencies]` exact pins
     with conda versioning and matches `pyproject.toml` with a `[tool.pixi]` section; it
     does not relock `pixi.lock` unless the hosted app allows `pixi` in
     `allowedUnsafeExecutions`, which is undocumented (L `tickets/S01-dependency-updates.md`
     lines 253-271). Keep the draft's rule: every pixi update waits for dashboard approval,
     and the relock proof of step 5 decides whether it stays a notice.
     `python = "3.14.*"` is manual: it is the tooling interpreter (`CONVENTIONS.md` §2),
     not a pin to bump. The `pep621` manager also matches the root `pyproject.toml`: its
     `[project] dependencies = []` gives it nothing to update, but the manager's page
     lists `requires-python` as a depType, so the dashboard lists `requires-python` from
     both manifests (`>=3.14` root, `>=3.11` the abi3 floor of decision 0012) beside
     `build-system.requires` from `crates/alliumpy/pyproject.toml`. Both floors go in the
     inventory as manual (they are §2's and decision 0012's, moved by hand); under
     `update-lockfile` a `>=` floor already satisfied produces no update, so confirm from
     the dashboard that no update is listed for either, and if one is, add
     `{ "matchManagers": ["pep621"], "matchDepTypes": ["requires-python"],
     "enabled": false }` with that reason.
   - **The B tag**: the draft's regex manager, unchanged.
   - **Actions**: the draft's group, which now spans `ci.yml`, `audit.yml`, `pages.yml`,
     `release-pypi.yml`, `mutants.yml`, `fuzz.yml` and the setup action; `maturin-action`
     and `setup-python` join it with no special rule. The `python-version` inputs are
     not pins Renovate reads; list them as manual (the `3.11` floor is decision 0012's,
     not a version to bump).
   - **tools.txt and tools-source.txt**, the draft's `tools.txt` regex manager with its
     file pattern widened over `tools-source.txt`, as P `tickets/T17-renovate.md` step 3
     does; the new wave-2 tool lines fall under it. `rustqual` and any T15 tool stay held
     for approval as `cargo-hack` is.
   - **The fuzz crate**: a second cargo root, as P `tickets/T17-renovate.md` step 3 has
     it: T15 commits `fuzz/Cargo.lock` and the cargo manager finds the root by that
     lockfile; lock-file maintenance covers both lockfiles, and the exclusion rule covers
     both because it matches the manager, not a file.

   Validate with the method the draft names: Renovate's own config validation, read after
   landing (step 5). No local validator in this ticket: `CONVENTIONS.md` §4 names every
   wave-2 recipe and none is T17's, and a pinned validator would need node through a pixi
   pin (L's draft, step 1), touching `Justfile`, `pyproject.toml` and `pixi.lock`, none of
   them in Files touched; the draft rules out an ad hoc `npx` run. The proof is that no
   `Action Required: Fix Renovate Configuration` issue exists and the dependency
   dashboard issue is open with no configuration error in its repository-problems
   section; quote both readings.

   **Adversarial review** (`CONVENTIONS.md` §14): the pin inventory and `renovate.json`
   (well-formed:
   `python -I -c 'import json, sys; json.load(open(sys.argv[1]))' renovate.json` exits
   0), before step 4 asks. The review goes into the authorisation request. Ask: which pin
   on `main` is missing from the inventory; which pin Renovate would bump that neither
   `just version-check` nor `just parity` would catch if the bump were wrong; whether the
   `allium-parser` exclusion also covers lock-file maintenance, and that `renovate.json`
   names `allium-cli` in the exclusion's `matchDepNames` when and only when decision 0014
   chose route (c), and nowhere otherwise, so that no Renovate branch can ever carry a
   different upstream version in two places; whether each manager's pattern matches the
   pins it claims, and only those; whether the maturin-range decision is written down
   with its reason.
4. **Land `renovate.json`, then, authorisation required, install the Mend app on
   `BiscuitBin/alliumpy` only.** `renovate.json` lands on `main` first, through a pull
   request (separately authorised), in the order L's draft step 1 gives and for its
   reason: a configuration already on the default branch is Renovate's manual onboarding,
   so installing the app afterwards produces the dependency dashboard and no onboarding
   pull request, and with `:dependencyDashboardApproval` in `extends` nothing opens
   without an approval click (each click is itself a separately authorised action,
   `CONVENTIONS.md` §11). Installing on a repository with no configuration would instead
   open an onboarding pull request carrying Renovate's own default configuration; if one
   appears anyway, it is a stop: it is never merged, and the maintainer closes it as a
   separately authorised action, recorded in the hand-back notes. The installation is
   an organisation-level action; an organisation owner may have to perform it. The
   repository is private: confirm from the app's listing that it serves private
   repositories on the organisation's plan before asking, and record the answer. Before
   asking, write the permissions the installation screen lists into
   `docs/explanation/security-model.md`, so the trust boundary is on record before the app
   has access (the draft's step 1), and name the vulnerability-fix exception as
   P `tickets/T17-renovate.md` step 4 does: a security-fix pull request can open unasked
   once Renovate receives vulnerability alerts; it still never merges itself.
5. **Read the dependency dashboard** Renovate opens after the installation (there is no
   onboarding pull request when a configuration is on `main`). Each regex manager is
   proved by the dashboard listing its dependency, or by a real update pull request; quote
   the evidence per manager, as the draft requires. Two proofs are this repository's own:
   the dashboard lists `allium-parser` under no pending update and opens no branch for it
   (approve nothing; if a branch appears, the exclusion is wrong and is fixed before
   anything else). That absence proves the exclusion only if there was something to
   exclude: the dashboard's detected-dependencies section must list `allium-parser` under
   `cargo` at `3.6.1` (the config was processed and the manager read the pin), and
   `cargo info allium-parser` (network, authorised; read as data) must show a release
   above the pin; if the newest release equals the pin, the hand-back notes record the
   exclusion as read but unexercised, with the check that closes it (the first dashboard
   reading after upstream's next release). And the first approved lock-file-maintenance
   run leaves `allium-parser` at `3.6.1` in `Cargo.lock` and in `fuzz/Cargo.lock` (quote
   the lockfile diffs, or the job log if there is none; the log sits on the Mend
   developer portal behind the maintainer's login, so the maintainer pastes the lines and
   the agent never asks for the credential, L `tickets/S01-dependency-updates.md` lines
   707-712). If the maturin range was kept and a `maturin` update is pending, approve it
   to learn whether the `pep621` manager edits `crates/alliumpy/pyproject.toml` as
   expected, and, if the sdist was kept, whether `uv build --sdist` from the bot's branch
   resolves the new range; `just wheel-smoke` builds with the pixi `maturin` and never
   reads the range, so its colour proves nothing here. The draft's `extends` carries
   `":dependencyDashboardApproval"`, which holds every update: keep it through these
   proofs, then a separately authorised pull request removes that one line and nothing
   else (L `tickets/S01-dependency-updates.md` lines 755-760, the activation), so that
   the `crates` and `github actions` groups flow weekly while every per-rule approval
   stays. The how-to, decision 0017 and the Monthly entry describe that activated state;
   "approve what is due" refers to the held rules.
6. **The runbook, `docs/how-to/bump-upstream.md`.** Register it in `docs/manifest.yml`
   (kind `how-to`, slug `upstream_bump`, audience maintainer and agent) and link it from
   `docs/README.md` under How to. Then replace the until-then sentence in `AGENTS.md`'s
   upstream-bump block (`CONVENTIONS.md` §7) and in `SECURITY.md`'s scope paragraph (T12
   step 4) with the path; `just check-agents` must still print
   `Validated AGENTS.md, 2 adapters, and 7 skills.` The runbook is written for an agent
   with no other context, as a numbered procedure with the exact commands, each with what
   its output must show:
   1. Read upstream's release (network, authorised; what comes back is data,
      `CONVENTIONS.md` §11, "Untrusted material"): the tag, its CHANGELOG entry,
      `cargo info allium-parser@<new>` and `allium-cli@<new>` both answering, and the
      exact `--version` text in U `crates/allium/src/main.rs` at the new tag
      (`gh api repos/juxt/allium-tools/contents/crates/allium/src/main.rs?ref=v<new>`),
      which step 4 writes into `ALLIUM_VERSION_STRING` and step 3's reference must print.
      A grammar change (minor) and a fix (patch) follow the same steps; note which it is,
      because a minor may change diagnostics across the corpus.
   2. On the `release/v<new>` branch that `docs/how-to/release.md` names (T14): if
      `target/wheel-smoke/venv/bin/allium` is missing (a fresh worktree has none),
      `just wheel-smoke` once before the bump: `version-check` on a missing venv fails
      naming `just wheel-smoke`, which is not the alarm. Bump `allium-parser = "=<new>"`
      in `Cargo.toml`, then `cargo update -p allium-parser --locked`, which fails by
      design with `error: the lock file ... needs to be updated but --locked was passed
      to prevent this` (the stale lockfile shown); then `cargo update -p allium-parser`
      (network, authorised) and the same with `--manifest-path fuzz/Cargo.toml`, because
      `fuzz/Cargo.lock` records the pin through its path dependency on `alliumpy-core`
      and `just lock-check` reads it (T15). Read each lockfile diff: it must move
      `allium-parser` and, where the new release raised a floor or added or dropped a
      dependency, only the entries cargo had to move for it (today its dependencies are
      `regex-lite`, `serde` and `serde_json`, `CONVENTIONS.md` §1 fact 5);
      `cargo tree -i <crate>` must trace each such entry back to `allium-parser`, and
      any entry that does not trace is reported, not edited. Then `just version-check`,
      which must now fail on the pin clause, naming `allium-parser`; quote the failure,
      because it is the alarm step 6 relies on.
   3. `just install-parity-reference` (network, authorised; it reads the pin step 2
      moved): its `--version` line must print the text step 1 read (`allium <new> ...`),
      and that whole line is the new `ALLIUM_VERSION_STRING`. Then the route decision
      0014 chose. (a) Vendoring: re-vendor as T13's hand-back notes describe (fetch U at
      the new tag into an empty directory with the `gh api` commands T13 recorded, a
      network step, authorised, whose output is data, not instructions; diff the vendored
      files against the previous tag, apply upstream's diff to the copy, keep the
      attribution header and update its version line). (b) The bundled binary: copy
      `.tools/parity/bin/allium` over `crates/alliumpy/python/alliumpy/_bin/allium`
      (S01's route-(b) steps), so the wheel step 5 builds carries the new binary; the
      Windows binary is T14's matrix's: move the `allium-cli` version wherever the matrix
      carries it (T14's hand-back notes say where). (c) Upstream's `run(args)`: bump
      `allium-cli = "=<new>"` in the same `Cargo.toml` edit and repeat step 2's
      `cargo update` for it. Under every route the parity reference itself needs no
      edit.
   4. **Move every version copy.** `ALLIUM_VERSION` and `ALLIUM_VERSION_STRING` in
      `crates/alliumpy-core/src/lib.rs` to step 3's values, keeping the comment naming
      U's file (or, if S01 found the suffix derivable, only the former); the unit test on
      the prefix must still pass (`just test`). Set `version = "<new>"` in
      `crates/alliumpy/pyproject.toml`, `version` in `[workspace.package]` of
      `Cargo.toml` (both crates inherit it) and the `version` of the `alliumpy-core` path
      dependency in `crates/alliumpy/Cargo.toml` (`CONVENTIONS.md` §3), so the three stay
      equal. Replace the `ALLIUM_VERSION == "<old>"` literal in the pytest version case
      in `crates/alliumpy/tests/test_parse.py` (T03 step 6; `smoke.py` carries no version
      literal, `CONVENTIONS.md` §9, but asserts that `__version__` starts with
      `ALLIUM_VERSION`, which is why the wheel version moves in this same step), and any
      literal T14's `release-pypi.yml` smoke
      compares `allium --version` against: `version-check` reads none of these;
      `wheel-smoke`, `py-test` and the release smoke do. Update the version line of the
      header paragraph in `crates/alliumpy/LICENSE-allium-tools`, which names the
      upstream version whose code and fixtures the wheel carries (`CONVENTIONS.md` §9,
      "Licences"). Then `rg -nF '<old>' --glob '!Cargo.lock' --glob '!CHANGELOG.md'
      --glob '!docs/decisions/**'` lists what is left: prose under `docs/` and
      `README.md` naming the version the wheel wraps is edited to `<new>`, and
      `tests/fixtures/parity/` is step 5's; any other match is a copy this step missed,
      and is edited or explained. After all manifest edits, refresh local package
      versions in both lockfiles: `cargo update --workspace --offline`, then
      `cargo update --workspace --offline --manifest-path fuzz/Cargo.toml`. Review
      both lockfile diffs: each recorded `alliumpy` or `alliumpy-core` entry must now
      have `<new>`, and registry dependencies must stay at the versions already
      reviewed in steps 2 and 3.
      An offline resolution failure or an unrelated dependency change is handed back,
      not hidden by a broad update. `just lock-check` must pass before step 5 rebuilds
      with the locked manifests.
   5. Rebuild and compare. Nothing more to edit: `just wheel-smoke` must now pass (it
      rebuilds the wheel and the venv at the new pin and version with step 4's copies;
      `parity` and `version-check` both read that venv; a `smoke.py` failure here is a
      copy step 4 missed), then `just parity`. A corpus file whose output changed is read
      against upstream's CHANGELOG: an intended change updates the expected output; an
      unintended one is an upstream report, not a corpus edit. Re-copy
      `tests/fixtures/parity/` from U at `v<new>` with the `gh api` reads T13 recorded
      (network, authorised), into an empty directory first (`CONVENTIONS.md` §11); diff
      it against the committed corpus, add any new fixture with its attribution, and
      update the version in each changed fixture's attribution and in
      `tests/fixtures/parity/README.md`.
   6. `just version-check` must now pass: every copy step 4 moved agrees, and the venv
      step 5 rebuilt prints the new string. It never runs before step 5, or the stale
      `allium` in `target/wheel-smoke/venv` fails it for the wrong reason. The failure
      quoted in step 2 is the alarm the runbook relies on, and this is where it clears.
   7. `CHANGELOG.md` (no command): under `[Unreleased]`, lines saying which upstream
      version the wheel now wraps and anything this repository changed to follow it;
      `docs/how-to/release.md` turns the heading into `[<new>] - <date>`.
   8. `just check`, then continue `docs/how-to/release.md` from its CHANGELOG step on
      (decision 0015 is the record, the how-to the procedure: the `[Unreleased]` split,
      pull request, merge, tag, the `release-pypi.yml` run, the `uvx` proof with an
      empty `UV_CACHE_DIR`), each push and tag its own authorised action.
   9. A `.postN` release, by contrast (no command), moves
      `crates/alliumpy/pyproject.toml`'s version alone and nothing in steps 2 to 6; its
      step 7 CHANGELOG lines say it is a packaging fix; say so at the end, with the test
      that tells the two apart (did `allium-parser` move).
7. **The other pages.** `docs/how-to/maintain-dependencies.md`: what the updater proposes
   and what stays manual, the `allium-parser` row pointing at the runbook, the pixi relock
   outcome of step 5, the maturin-range decision. `docs/operations/maintenance.md`: the
   Monthly entry (read the dashboard, approve what is due) and a "When upstream releases"
   entry pointing at the runbook. Decision 0017 (`CONVENTIONS.md` §8): Renovate over
   Dependabot (L's evidence), the app's access, the exclusion of the upstream pin and why,
   what stays manual, the vulnerability-fix exception, what would reopen it (the hosted
   app relocking `pixi.lock`; a Renovate manager for crates.io binaries). Register the
   record in the manifest, the index and the decisions README; one `CHANGELOG.md` line.
8. **The last claims.** Carry the outcomes of `CONVENTIONS.md` §12 claims 2, 4, 5, 7, 12
   and 18 from the hand-back notes of T13 and T14 (S01's part of claim 12 is T11's,
   `CONVENTIONS.md` §12) into §12's table through a `main` pull request (separately
   authorised), in the shape T11 used for wave 1. This does not depend on the app: if
   step 4 stops, do this step before handing back.
9. `just check`, the final adversarial review, `just check` again if fixes landed, then
   commit.

   **Adversarial review** (`CONVENTIONS.md` §14): the lane's diff. Ask: whether the
   runbook can be followed by an agent with no other context, step by step, with no
   command whose expected output is unstated; whether it still holds under the route
   decision 0014 chose, and says what differs under the other two; whether the
   dashboard's config-validation state and the per-manager evidence of step 5 are
   quoted; whether the how-to and decision 0017 match what was installed and proved;
   whether the carried §12 outcomes match the hand-back notes they cite; whether any text
   claims every update waits for approval without naming the vulnerability-fix
   exception.

## Acceptance criteria

- Every pin in step 2's inventory is either covered (with quoted evidence from the
  dashboard or a pull request), listed as manual with a reason in the how-to, or
  excluded with the reason in `renovate.json` and the how-to.
- The dashboard never lists an `allium-parser` update as approvable, no Renovate branch
  touches `allium-parser` in `Cargo.toml`, `Cargo.lock` or `fuzz/Cargo.lock`, and the
  quoted lock-file maintenance diff shows it unchanged in every lockfile. The
  detected-dependencies listing and the `cargo info allium-parser` reading are quoted;
  if no newer `allium-parser` existed on the day, the hand-back notes say the exclusion
  is unexercised and name the check that closes it.
- The app is installed on this repository only, proved by the dated maintainer
  read-back from installation settings described in Verification, and its permissions
  are in the security model.
- `renovate.json` validates: no `Action Required: Fix Renovate Configuration` issue
  exists and the dashboard issue shows no configuration error, both quoted in the
  hand-back notes.
- `docs/how-to/bump-upstream.md` is registered, reachable, and each of its nine steps
  that runs a command names the command and what its output must show, and a step with
  no command (the CHANGELOG edit, the `.postN` contrast) says so; `just check-docs` is
  green.
- The runbook refreshes both lockfiles after changing local crate versions and requires
  `just lock-check` before the locked wheel build.
- `CONVENTIONS.md` §12 claims 2, 4, 5, 7, 12 and 18 have outcomes, each citing the ticket
  whose hand-back notes hold the evidence.
- `just check` is green.
- The adversarial reviews in Steps ran (`CONVENTIONS.md` §14), and every valid finding is
  fixed or handed back.

## Verification

```sh
gh pr list --repo BiscuitBin/alliumpy --author 'app/renovate' --state all --json number,title,headRefName
rg -n 'allium-parser' renovate.json
rg -n 'allium-parser' Cargo.toml
rg -n -A1 'name = "allium-parser"' Cargo.lock fuzz/Cargo.lock
just check-docs
just check
```

For the repository-scope proof, the maintainer opens BiscuitBin's organisation
Settings, GitHub Apps, and Configure for the installed Renovate app. Read back the
organisation, app name, installation id and settings URL, then the Repository access
section: it must say "Only select repositories" and list solely
`BiscuitBin/alliumpy`. Quote the dated read-back and who performed it in the hand-back
notes, along with the permissions shown. "All repositories", an additional repository,
or missing access to the settings view fails this proof and stops the step; a view
filtered to repositories the caller can access is not a substitute for installation
settings. GitHub's procedure is
`https://docs.github.com/en/apps/using-github-apps/reviewing-and-modifying-installed-github-apps`.
Do not ask for an owner's OAuth token or personal access token to read
`/user/installations/{id}/repositories`: that endpoint requires a GitHub App user
access token for Renovate, and an owner's ordinary `gh` login does not satisfy it.

The first `rg` must match the exclusion rule and nothing else; the second must show
`=3.6.1` (or the version T13 left) in `Cargo.toml`; the third must print, per lockfile
(`Cargo.lock` and `fuzz/Cargo.lock`), exactly one `name = "allium-parser"` line followed
by a `version` line equal to the pin, before and after Renovate's first runs.

## Hand-back notes

Branch `tickets/T17-renovate`, not the frontmatter's `ticket/t17-renovate` (Supacode's
naming), as pachinko's was.

### Baseline: `92b2a77`, untouched

`just initialize`, then `just check`, exit 0:

```text
All checks passed and the worktree is unchanged.
```

### Claims (step 8): PR #34, commit `7799b6a`, merged

Claims 1, 2, 4, 7, 12, 18 and 19 hold. Claim 5 is `partial`, because §12's vocabulary has
no qualified `holds`: it held on this public `enterprise` repository, and the private
non-Enterprise case was never exercised.

### The inventory (step 2): `92b2a77`

Read from every tracked file: `git ls-files`, then a search for versions, SHAs and digests
outside `docs/`, `tickets/` and the vendored code. Beyond the ticket's list it found
`nextest-version`, `fuzz/Cargo.toml` `rust-version`, `twine==7.0.0`, the three image
digests, `LYCHEE_VERSION`, the release matrix's runner labels, and the `python_version` and
`target-version` settings. Versions are as read on that day.

| Pin | File | Coverage |
| --- | --- | --- |
| `allium-parser = "=3.6.1"` | `Cargo.toml`; `Cargo.lock`, `fuzz/Cargo.lock` | **excluded**: `matchManagers: cargo`, `matchDepNames`, `enabled: false` |
| parity reference | none: `install-parity-reference` reads `--print-pin` | **follows the exclusion**; no literal |
| `pyo3`, `serde`, `serde_json`, `divan` and their closure | `Cargo.toml`, `Cargo.lock` | native `cargo`, group `crates` |
| `libfuzzer-sys = "0.4.13"` and its closure | `fuzz/Cargo.toml`, `fuzz/Cargo.lock` | native `cargo`, second root, group `crates` |
| `alliumpy-core = { path, version = "3.6.1" }` | `crates/alliumpy/Cargo.toml`, `fuzz/Cargo.toml` | not a pin: a path dependency, which the manager skips; moved by the runbook under invariant 9 |
| crate and wheel versions | `Cargo.toml`, `crates/alliumpy/pyproject.toml` | not pins: this repository's own, moved by the runbook |
| `channel = "1.99.1"` | `rust-toolchain.toml` | native `rust-toolchain`, group `rust toolchain`, held |
| `rust-version = "1.99"` | `Cargo.toml`, `fuzz/Cargo.toml` | regex, `rust-version` datasource, `rust-release-channel`; group `rust toolchain`, held |
| 15 exact conda pins (`just`, `prek`, `cargo-binstall`, `cargo-nextest`, `cargo-llvm-cov`, `cargo-deny`, `cargo-insta`, `cargo-shear`, `taplo`, `cargo-mutants`, `maturin`, `uv`, `pytest`, `ruff`, `mypy`) | `pyproject.toml` | native `pixi`, held |
| `python = "3.14.*"` | `pyproject.toml` | manual: disabled by rule, §2's tooling interpreter |
| `requires-python = ">=3.14"`, `">=3.11"` | both `pyproject.toml` | manual; no rule yet (ticket: add one if the dashboard lists an update) |
| `python_version = 3.11`, `target-version = "py311"` | `mypy.ini`, `ruff.toml` | manual: no manager reads them; they follow the wheel's `>=3.11` floor, decision 0012 |
| `pixi.lock` | `pixi.lock` | `lockFileMaintenance`, held |
| `nextest-version = "0.9.146"` | `.config/nextest.toml` | regex, conda `conda-forge/cargo-nextest`; group `cargo-nextest`, held |
| `biscuit-games-tooling` tag `v0.3.0` | `pyproject.toml` | regex, `github-tags`, held |
| `requires-pixi = ">=0.81.0"` | `pyproject.toml` | regex, `github-releases`; group `pixi bootstrap`, held |
| `pixi-version: v0.81.0` | `.github/actions/setup/action.yml` | regex, same; native reading disabled |
| `maturin>=1.15,<2.0` | `crates/alliumpy/pyproject.toml` | native `pep621`, group `python build backend`, held; range kept |
| `maturin-version: v1.15.0`, 9 times | `release-pypi.yml` | regex, conda `conda-forge/maturin`; group `maturin` with the pixi pin, held; native reading disabled |
| `version: '0.13.5'` (setup-uv) | `release-pypi.yml` | regex, conda `conda-forge/uv`; group `uv` with the pixi pin, held; native reading disabled |
| `twine==7.0.0` | `release-pypi.yml` | regex, `pypi`, held |
| `python-version: '3.11'`, `'3.14t'` | `ci.yml`, `release-pypi.yml` | manual: disabled by rule, decision 0012's floor and the free-threaded build |
| `cargo-hack@0.6.45`, `cargo-fuzz@0.13.2` | `tools.txt` | regex, `crate`, held |
| `rustqual@1.8.3` | `tools-source.txt` | regex, `crate`, held |
| 6 hook revs (editorconfig-checker, markdownlint-cli2, typos, shellcheck-py, actionlint, ripsecrets) | `.pre-commit-config.yaml` | regex; native off; group `hook revs`, held |
| markdownlint-cli2 rev, repeated | `.pre-commit-fix.yaml` | same regex and group |
| lychee rev and `LYCHEE_VERSION=0.24.2`, twice | `.pre-commit-config.yaml` | manual: disabled; argument must match the rev; prefix `lychee-v` |
| Remote actions (`actions/*`, `Swatinem/rust-cache`, `prefix-dev/setup-pixi`, `PyO3/maturin-action`, `astral-sh/setup-uv`, `docker/setup-qemu-action`) | `.github/workflows/*.yml`, `.github/actions/setup/action.yml` | native `github-actions`, group `github actions` |
| `uses: ./.github/actions/setup` | workflows | not a pin: a local path |
| `python:3.11-slim@sha256:…`, `python:3.11-alpine@sha256:…`, `tonistiigi/binfmt@sha256:…` | `release-pypi.yml` | manual: smoke-only, never in the wheel; bare digests suit a regex poorly |
| `ubuntu-22.04`, `macos-15-intel` | `release-pypi.yml`, under `matrix.platform.runner` | manual: the manager reads `runs-on` but cannot resolve the matrix expression; decides which wheels build |
| `runs-on: ubuntu-latest`, `windows-latest`, `macos-latest` | workflows | not pins |
| literal `15` | `release-pypi.yml` `release` job's guard | manual: moves with the matrix |
| Toolchain text in prose | `docs/reference/configuration.md:90`, `crates/alliumpy/Cargo.toml:19`, decision 0016 | not pins: dated measurements |

The `github-actions` correction: the ticket says that manager reads none of the inputs.
Renovate's `known-actions` lists `python-version`, setup-uv's `version`, `maturin-version`
and `pixi-version`, so each has a rule, and the dashboard below lists none of them.

### The vendoring script: `92b2a77` with the script uncommitted

T13 step 2's text, with one long string split and one call rewritten for `just py-lint` and
`just py-typecheck`, as `scripts/vendor_cli.py`. The three files fetched at `v3.6.1`, each
`git hash-object` equal to the tag's tree, into an empty directory; the script exits 0, and
`cmp` finds each output byte-identical to `crates/alliumpy-core/src/cli/`.

### The runbook's read-through: `92b2a77`

Not a bump: a temporary pin edit to `=3.6.0`, a real version, restored afterwards with
`git status --short` clean apart from the new script. Both texts differ from the ticket's
expectation, and the runbook quotes these:

```text
cargo update -p allium-parser --locked                      (exit 101)
error: cannot update the lock file <worktree>/Cargo.lock because --locked was passed to prevent this
just version-check                                          (exit 1)
version-check: workspace version='3.6.1' differs from allium-parser pin='3.6.0'
```

The other steps were read, not run; a real upstream release is what exercises them. Step 5
departs from the ticket by replacing the corpus before `just parity`, not after, so parity
runs on the new files. The harness compares live against the reference, so a difference is
a defect here and not a stored output to update, and upstream's fixtures take no edit or
per-fixture attribution, as `tests/fixtures/parity/README.md` records.
`TERMINAL_*` are re-measured by running their test against the reference; the command's
shape was checked against the candidate (`1 passed`), because no reference was built here.

### Installation and scope (step 4): `main` at `0dd7c07`

The maintainer installed the app for the whole organisation on 2026-10-24, for pachinko,
and chose to keep it so; this is a declared departure from "this repository only", and the
pages say so. The maintainer's read-back from the settings view, 2026-11-06 UTC, at
`https://github.com/organizations/BiscuitBin/settings/installations/174933380`, agrees with
the API reading of 2026-11-05 below: organisation `BiscuitBin`, app `renovate`, the same id,
"All repositories", and the same permissions. The ticket's Verification treats "All
repositories" as a failure and a stop; the maintainer's decision replaces that.

```text
gh api orgs/BiscuitBin/installations
renovate, id 174933380, repository_selection all, created 2026-10-24T13:48:08.000-07:00
read: administration, members, metadata, packages, vulnerability_alerts
write: checks, contents, issues, pull_requests, statuses, workflows
```

The private-plan open point is moot: the repository is public on `enterprise`, and
`repos/BiscuitBin/alliumpy/vulnerability-alerts` answers HTTP 204, so the vulnerability-fix
exception applies from the first run.

### The dashboard (step 5): issue #36, 2026-11-05T22:10:06Z, `main` at `99f2861`

PR #35 merged at 21:54:54Z. Renovate opened the dashboard at 21:55:25Z and closed its
onboarding pull request, which now reads `Configure Renovate - autoclosed`, at 21:55:26Z.
No `Action Required` issue exists (`gh issue list --search`, 0), and the body has no
repository-problems section.

| Manager | Detected | Grouping or update |
| --- | --- | --- |
| cargo | `Cargo.toml`: `pyo3`, `divan`, `serde`, `serde_json`; `fuzz/Cargo.toml`: `libfuzzer-sys` | lock maintenance on `renovate/lock-file-maintenance-crates` |
| github-actions | every remote `uses:`; no `python`, `astral-sh/uv`, `maturin` or `prefix-dev/pixi` | `renovate/github-actions` |
| pep621 | `crates/alliumpy/pyproject.toml`: `python >=3.11`, `maturin >=1.15,<2.0`; `pyproject.toml`: `python >=3.14` | no update for any of them, so no `requires-python` rule was added |
| pixi | 15 exact pins; no `python` | one branch per pin; `renovate/lock-file-maintenance` |
| rust-toolchain | `rust 1.99.1` | no update |
| regex: `rust-version` | `Cargo.toml` and `fuzz/Cargo.toml`: `rust 1.99` | no update |
| regex: tools | `tools.txt`: `cargo-hack 0.6.45`, `cargo-fuzz 0.13.2`; `tools-source.txt`: `rustqual 1.8.3` | no update |
| regex: `nextest-version` | `cargo-nextest 0.9.146` → `0.9.151` | `renovate/cargo-nextest`, one branch with the pixi pin |
| regex: setup-uv | `uv 0.13.5` → `0.13.7` | `renovate/uv`, with the pixi pin |
| regex: `maturin-version` | nine readings, `maturin 1.15.0` → `1.16.0` | `renovate/maturin`, with the pixi pin |
| regex: twine | `twine 7.0.0` | no update |
| regex: tooling tag | `biscuit-games-tooling v0.3.0` | no update |
| regex: pixi pair | `.github/actions/setup/action.yml` and `pyproject.toml`: `prefix-dev/pixi 0.81.0` → `0.84.1` | `renovate/pixi-bootstrap`, one branch |
| regex: hook revs | six in `.pre-commit-config.yaml` (no lychee), markdownlint in `.pre-commit-fix.yaml` | `renovate/hook-revs`; `renovate/major-hook-revs` for editorconfig-checker v4 |

Every entry sat under Pending Approval, and no update pull request opened until a box was
ticked.

**The exclusion, two proofs.**

- **Listing: this proof cannot be met as the ticket writes it.** The ticket requires
  `allium-parser` listed under `cargo` at `3.6.1`. Renovate's `package-files.ts` drops any
  dependency with a skip reason from that section, and a disabled rule sets one, so the
  absence is what a working rule produces. `python` under pixi is absent the same way, while
  the manifest's other four are listed. `cargo info allium-parser`, 2026-11-06T02:46:48Z,
  at `7e99b08`, prints `version: 3.6.1`, equal to the pin, and upstream's newest tag is
  `v3.6.1`, so **the exclusion is read but unexercised**. The check that closes it is the
  first dashboard reading after upstream's next release, which
  `docs/operations/maintenance.md` names.
- **Lock maintenance: holds.** See #39 below.

From Renovate's source, as data: `fetch.ts`'s comment says a vulnerability fix goes through
for a manager-disabled dependency "unless a package rule disabled it as well", so the
exclusion also holds against an alert.

### Approved pull requests

Boxes ticked by the executing agent on the maintainer's separate authorisation for each.

| PR | Moved | Outcome |
| --- | --- | --- |
| #39 crates lock maintenance | `cc` 1.10.0 → 1.11.0 in `fuzz/Cargo.lock`; `Cargo.lock` untouched | green; merged `34be00c` |
| #41 `pixi bootstrap` | `pixi-version` v0.84.1, `requires-pixi` >=0.84.1; no `pixi.lock` change | green; merged by the maintainer, `30a99d0` |
| #40 pixi lock maintenance | `pixi.lock` +84 −83 | red, then green on `d6a5165`; merged by the maintainer, `9e47bb5` |
| #37 uv | the pin, the setup-uv copy, `pixi.lock` | red, then green on `c6fc825`; merged `9cfae15` |
| #38 maturin | the pin, nine `maturin-version` copies, `pixi.lock` | red, then green on `dac8ae2`; merged `0dd7c07` |

On the #39 branch, at `5e9c45e`, `allium-parser` is `3.6.1` in `Cargo.lock` and in
`fuzz/Cargo.lock`, and `=3.6.1` in `Cargo.toml`. None of the other diffs mentions it.

**The relock proof.** The hosted app relocks `pixi.lock` on this repository, but the first
relocks failed every job in setup with `lock file not up-to-date with the workspace`.
Reproduced with the exact binaries, `pixi list --locked --no-install`:

| Lock | pixi 0.81.0 | pixi 0.84.1 |
| --- | --- | --- |
| the bot's | exit 1, same error | exit 0 |
| `main`'s | exit 0 | exit 0 |

Inference, not read from a log: `requires-pixi` is a floor, so the app relocked with a pixi
of 0.84 or later. A local 0.84.1 relock writes the same `__unix=0` line as the bot's, where
`main`'s read `__unix=0=0`, and pixi 0.84.0's notes change lock hashes and recommend that
everyone move. Pachinko's proof predates 0.84. The how-to says to approve `pixi bootstrap`
first; its residual risk is that this recurs.

**Merge order.** #40 merged before #37 and #38 rebased over it. `main` at `0dd7c07` has
`uv` 0.13.7 and `maturin` 1.16.0 in the manifest and the lock, and pixi 0.84.1's
`lock --check --dry-run` exits 0 on it.

**Not exercised by any of these.** `release-pypi.yml` does not run on pull requests, so
`uv` 0.13.7 and `maturin` 1.16.0 in that workflow are first exercised by the next rehearsal.
`docs/how-to/release.md` calls for one, since the workflow has changed.

### Extraction proved, update half pending

Recorded per dependency, not as done, because nothing was pending on the day:

- **`allium-parser`:** as above.
- **The toolchain group:** `rust 1.99.1` and `rust 1.99` extracted; the newest Rust manifest
  is `1.99.1`. `rust-release-channel`'s `getNewValue` returns `major.minor` when the current
  value has no patch, which is read from source. The first minor release proves it.
- **The maturin range:** `maturin >=1.15,<2.0` extracted, with no update under
  `update-lockfile`. The range was kept, with its reason in the rule, the how-to and
  decision 0017; `release-pypi.yml` sets `maturin-version`, so the ticket's "unset" wording
  does not apply. The first maturin 2.0 proves the edit.
- **`twine`, the tools and the tooling tag:** extracted, with no update pending.

### Departures from P's ticket, L's draft and this ticket

- **Scope.** The app stays org-wide, as above.
- **Toolchain.** The native `rust-toolchain` manager and the `rust-version` datasource, as
  L drafted, rather than P's Docker tags: there is no `Dockerfile` here.
- **Input pairs.** `uv` and `maturin` copies are read through conda regex managers, the
  pattern P proved for `nextest-version`.
- **Disabled.** The pixi `python` line, and `python-version` inputs.
- **Manual lists.** Runner labels and the Python-floor settings join them.
- **Activation, by the maintainer's choice after `/code-review`.** The ticket removes
  `:dependencyDashboardApproval`, which makes flowing the default for anything without a
  rule. Instead the preset stays and the `crates` and `github actions` rules set
  `dependencyDashboardApproval: false`: the same two groups flow, and the default stays held.
  Those rules also gain `minimumReleaseAge: "7 days"`, which neither the ticket nor pachinko
  has. Three `description` strings change with them. None of this was proved at hand-back:
  the first Monday run after it merges is the proof, the two groups opening and nothing else
  opening.
- **Outside Files touched,** each a sentence T17 made false: `docs/how-to/release.md`,
  `docs/how-to/develop-locally.md` (the pixi floor, now named by reference),
  `docs/explanation/architecture.md`, `docs/reference/configuration.md`, decisions 0004 and
  0011, `tools-source.txt`, `tickets/README.md`, and the new `scripts/vendor_cli.py`, by the
  maintainer's choice.
- **§12.** Through its own `main` pull request, as the ticket says, unlike pachinko.

### Review 1 (`CONVENTIONS.md` §14): `92b2a77` with the lane uncommitted

Codex `gpt-6-astra`, read-only, one per lens (`ai_tmp/review/T17-1/`); triage and fixes: a
fresh-context subagent. No high finding.

| Finding | Severity | Verdict | Applied |
| --- | --- | --- | --- |
| C2, BR-02: the setup-uv regex read any quoted `version:` | medium | valid | bound to the `astral-sh/setup-uv` step; `version` must stay its first input, and moving it stops the reading rather than misreading |
| C1, BR-01: `mypy.ini` `python_version` and `ruff.toml` `target-version` missing | low | valid | listed as manual, tied to decision 0012 |
| BR-03: the scratch check could pass with a manager deleted | low | valid | every expected manager must be visited once |

`twine` and the maturin range can be bumped wrongly without `just version-check` or `just
parity` noticing. Both reviewers reported this as no finding: both are held, and the how-to
names what first exercises them.

### Review 2 (`CONVENTIONS.md` §14): `7678af9`

Codex `gpt-6-astra`, read-only, one per lens (`ai_tmp/review/T17-2/`); triage and fixes: a
fresh-context subagent. No high finding. Both lenses found no mismatch in the §12 outcomes
against T13 and T14, and none in the per-manager evidence against the saved dashboard.

| Finding | Severity | Verdict | Applied |
| --- | --- | --- | --- |
| C1, BR-01: an empty corpus listing would read as every upstream fixture deleted | medium | valid | one checked tree read, non-empty and untruncated, before any comparison or deletion |
| BR-02: `path=` in the vendoring block clobbers `PATH` under zsh | medium | valid | renamed; both blocks run under zsh and bash with a stand-in `gh` |
| C2, BR-03: the hand-off to the release page skipped its pre-flight | medium | valid | step 8 requires it first |
| C3, BR-05: the route (b) note implied shipping the host binary | medium | valid | built per target by the release matrix; the local reference never ships |
| C4, BR-04: `uv build --sdist` from the root targets the tooling project | medium | valid | names `crates/alliumpy` and what its output must show; not run, because it needs the network |
| C5, BR-06: `tools-source.txt` omitted the vulnerability exception | low | valid | named |
| C6: the settings read-back was only promised for the pull request | medium | valid | recorded under Installation and scope |

### `/code-review` (medium): `7e99b08`

| Finding | Verdict | Applied |
| --- | --- | --- |
| Removing the preset flips the default to flow, against the docs | valid | fail-closed activation, by the maintainer's choice |
| Flowing groups run new release code in CI before anyone reads it | valid | seven-day wait, by the maintainer's choice; the security model records the exposure |
| A breaking 0.x release lands in the `crates` group | valid, not read from a run | the how-to says so and what to do; no separate `pyo3` rule |
| The relock break is a manual recovery, and `constraints` is unverified | valid | no change: decision 0017 records it as what would reopen the decision |
| The sdist check was unrun, and built no wheel | valid | run for real at `7e99b08`: `uv build crates/alliumpy` failed with `rustup could not choose a version of cargo`, because the unpacked sdist has no `rust-toolchain.toml`; with `RUSTUP_TOOLCHAIN=1.99.1` it exits 0 and prints `Successfully built` for the `.tar.gz` and the `.whl`. The how-to gives that form |
| The pre-flight hand-off omitted `project_code` | valid | step 8 says `200` |
| The dashboard-omissions list was partial | valid | extended |
| Weekly pull requests filed under a Monthly routine; lock maintenance's `crates` branch name | valid | moved to the weekly pass; the table says it waits |
| No final `just check` in the notes | partly valid | a commit cannot quote its own run; the pull request quotes it |
| Read-back date, `cargo info` quote, unheaded output | valid | dated UTC, quoted, headed |

## Open points

- Closed: the repository is public on `enterprise`, so the private-plan question does not
  arise. The fallback was not needed.
