# Copyright 2026 Steven Cutting
"""Validate the agent guidance, its provider adapters, and the skill bridges.

`AGENTS.md` is the single source of truth. Everything under `.claude/` and
`.codex/` exists only so those tools can discover it, so this check fails when
a bridge grows content of its own or drifts from the canonical skill.

Skills named in `skills-lock.json` are third-party, installed unchanged by the
skills tool that wrote the lock (decision 0018). They are exempt from the house
rules, but not from the inventory: each must be installed where the lock says,
with the Claude entry the tool links, and nothing else of theirs may appear.

Ported from `bg-validate-agents` in biscuit-games-tooling v0.3.0 (`6c5c07f`), which
has no way to exempt a skill; this repository owns its agent validation since.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

CANONICAL_SKILLS = Path(".agents/skills")
PROVIDERS = ("claude", "codex")
# The lock the skills tool writes. Its `skills` keys are the vendored skills.
VENDOR_LOCK = Path("skills-lock.json")
# Where the skills tool links each vendored skill for Claude Code, and what the link
# names. Codex reads `.agents/skills/` itself, so a vendored skill has no Codex entry.
VENDOR_LINKS = Path(".claude/skills")
VENDOR_LINK_TARGET = "../../.agents/skills/{name}"
# The whole of a bridge body. Compared against this rather than measured: a word
# budget lets a bridge carry an instruction of its own as long as it is brief,
# and an instruction surface that says "this bridge adds nothing" has to mean it.
BRIDGE_BODY = (
    "Follow `../../../.agents/skills/{name}/SKILL.md`. "
    "That file is canonical and this bridge adds nothing to it."
)
MANAGED_DIRECTORIES = (Path(".agents"), *(Path(f".{provider}") for provider in PROVIDERS))

# Committed provider configuration that is neither a skill nor an adapter.
# Tolerated rather than expected: the inventory permits these without demanding
# them.
TOLERATED = {Path(".claude/settings.json")}

ADAPTERS = {
    "CLAUDE.md": "@AGENTS.md\n",
    ".github/copilot-instructions.md": (
        "# GitHub Copilot repository adapter\n\n"
        "Read and follow `../AGENTS.md` as the canonical repository instruction file "
        "before proposing or editing code. This adapter adds no permissions and must "
        "not duplicate or weaken the canonical policy.\n"
    ),
}
# Phrases AGENTS.md must carry. Each names an invariant that is expensive to
# rediscover: how untrusted input is treated, the one command that proves a
# change, where authority stops, where scratch work goes, what decides
# behaviour, and which reactivity model the components use.
REQUIRED_GUIDANCE = (
    "untrusted",
    "just check",
    "explicit authorization",
    "ai_tmp/",
    "docs/specs/",
    "runes",
)
UNRESOLVED = re.compile(r"{" + r"{|{" + r"%|{" + r"#")
# A house skill's description must say when to use it, in more than a few words.
MINIMUM_DESCRIPTION_WORDS = 8
# Below this, AGENTS.md cannot be carrying the working agreement.
MINIMUM_GUIDANCE_WORDS = 300


def _git() -> str:
    """Git's absolute path, so no later lookup can pick a different executable."""
    git = shutil.which("git")
    if git is None:
        print("agent validation: git is not on PATH", file=sys.stderr)
        raise SystemExit(2)
    return git


def _root() -> Path:
    """The top level of the Git worktree the current directory is inside."""
    result = subprocess.run(
        [_git(), "rev-parse", "--show-toplevel"], check=False, capture_output=True, text=True
    )
    if result.returncode != 0:
        print("agent validation: run this from inside a Git worktree", file=sys.stderr)
        raise SystemExit(2)
    return Path(result.stdout.strip())


def _vendored_names(root: Path) -> tuple[str, ...]:
    """The skills the lock names, or none when there is no lock."""
    path = root / VENDOR_LOCK
    if not path.is_file():
        return ()
    try:
        skills = json.loads(path.read_text(encoding="utf-8"))["skills"]
    except (ValueError, KeyError, TypeError) as error:
        message = f"{VENDOR_LOCK} has no readable skills table: {error!r}"
        raise RuntimeError(message) from error
    if not isinstance(skills, dict):
        message = f"{VENDOR_LOCK} has no readable skills table"
        raise TypeError(message)
    return tuple(sorted(skills))


def _skill_names(root: Path, vendored: tuple[str, ...]) -> tuple[str, ...]:
    """The house skills: every skill directory the lock does not name."""
    return tuple(
        sorted(
            path.name
            for path in (root / CANONICAL_SKILLS).iterdir()
            if path.is_dir() and path.name not in vendored
        )
    )


def _expected_files(names: tuple[str, ...]) -> set[Path]:
    expected = {Path("AGENTS.md")}
    expected.update(Path(relative) for relative in ADAPTERS)
    for name in names:
        expected.add(CANONICAL_SKILLS / name / "SKILL.md")
        for provider in PROVIDERS:
            expected.add(Path(f".{provider}/skills") / name / "SKILL.md")
    return expected


def _versioned_paths(root: Path) -> set[Path]:
    """List every path Git would keep, ignored files excluded.

    Assistants write their own state into these directories -- Claude Code
    creates `.claude/settings.local.json` on the first permission approval --
    and a filesystem walk would report that state as an unexpected managed
    file. Deferring to Git means a `.gitignore` entry is enough to keep local
    tool state out of the inventory, while anything a reviewer would actually
    receive still counts.

    This project's own `.gitignore` is the only rule set consulted, rather than
    `--exclude-standard`. That option also honours `.git/info/exclude` and the
    user's global `core.excludesFile`, and putting `.claude/` in a personal
    global ignore file is a common habit -- it would hide the skills from this
    inventory and report every one of them as missing.
    """
    result = subprocess.run(
        [_git(), "ls-files", "-z", "--cached", "--others", "--exclude-from=.gitignore"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        detail = result.stderr.decode(errors="backslashreplace").strip()
        raise RuntimeError(detail or "git ls-files failed; run just initialize")
    return {Path(os.fsdecode(item)) for item in result.stdout.split(b"\0") if item}


def _is_vendored(relative: Path, vendored: tuple[str, ...]) -> bool:
    """Whether a path is a vendored skill's own file or its Claude link."""
    return any(
        CANONICAL_SKILLS / name in relative.parents or relative == VENDOR_LINKS / name
        for name in vendored
    )


def _managed_files(root: Path, vendored: tuple[str, ...]) -> set[Path]:
    named = (*ADAPTERS, "AGENTS.md")
    top_level = {Path(relative) for relative in named}
    return {
        relative
        for relative in _versioned_paths(root)
        if (
            relative in top_level
            or any(directory in relative.parents for directory in MANAGED_DIRECTORIES)
        )
        and not _is_vendored(relative, vendored)
    }


def _parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        message = "missing opening frontmatter"
        raise ValueError(message)
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        message = "missing closing frontmatter"
        raise ValueError(message) from error
    fields: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            message = f"invalid frontmatter line: {line}"
            raise ValueError(message)
        key, value = line.split(":", 1)
        key = key.strip()
        # Last-wins would let a block carrying three lines satisfy a rule about
        # two keys, so the repeat is the error rather than the survivor.
        if key in fields:
            message = f"duplicate frontmatter key: {key}"
            raise ValueError(message)
        fields[key] = value.strip()
    return fields, "\n".join(lines[end + 1 :])


def _check_inventory(
    root: Path, names: tuple[str, ...], vendored: tuple[str, ...], errors: list[str]
) -> None:
    expected = _expected_files(names)
    actual = _managed_files(root, vendored)
    errors.extend(f"missing managed file: {relative}" for relative in sorted(expected - actual))
    errors.extend(
        f"unexpected managed file: {relative}" for relative in sorted(actual - expected - TOLERATED)
    )
    for relative in sorted(expected & actual):
        path = root / relative
        if path.is_symlink() or not path.is_file():
            errors.append(f"managed path must be a regular file: {relative}")
        elif UNRESOLVED.search(path.read_text(encoding="utf-8")):
            errors.append(f"managed file has unresolved template syntax: {relative}")


def _check_vendored(root: Path, vendored: tuple[str, ...], errors: list[str]) -> None:
    """Each locked skill is installed, versioned, and linked for Claude as the tool links it."""
    versioned = _versioned_paths(root)
    for name in vendored:
        skill = CANONICAL_SKILLS / name / "SKILL.md"
        if skill not in versioned or not (root / skill).is_file() or (root / skill).is_symlink():
            errors.append(f"{VENDOR_LOCK} names {name}, but {skill} is not a versioned file")
        link = VENDOR_LINKS / name
        target = VENDOR_LINK_TARGET.format(name=name)
        if link not in versioned or not (root / link).is_symlink():
            errors.append(f"vendored skill {name}: {link} must be a versioned link to {target}")
        elif str((root / link).readlink()) != target:
            errors.append(f"vendored skill {name}: {link} must link to {target}")


def _check_canonical(root: Path, errors: list[str]) -> None:
    path = root / "AGENTS.md"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    lowered = text.lower()
    errors.extend(
        f"AGENTS.md is missing required guidance: {phrase!r}"
        for phrase in REQUIRED_GUIDANCE
        if phrase.lower() not in lowered
    )
    if len(text.split()) < MINIMUM_GUIDANCE_WORDS:
        errors.append("AGENTS.md is too short to carry the working agreement")
    if (root / "CODEX.md").exists():
        errors.append("CODEX.md is forbidden; Codex reads AGENTS.md directly")


def _check_adapters(root: Path, errors: list[str]) -> None:
    # Compared whole rather than stripped. docs/reference/agent-contract.md calls
    # these byte-pinned, and a comparison that forgave surrounding whitespace or a
    # missing final newline would be enforcing something weaker than the word.
    for relative, expected in ADAPTERS.items():
        path = root / relative
        if path.is_file() and path.read_text(encoding="utf-8") != expected:
            errors.append(f"{relative} must remain the exact thin adapter")


def _check_bridges(root: Path, name: str, fields: dict[str, str], errors: list[str]) -> None:
    for provider in PROVIDERS:
        bridge = root / f".{provider}/skills" / name / "SKILL.md"
        if not bridge.is_file():
            continue
        try:
            bridge_fields, bridge_body = _parse_frontmatter(bridge)
        except ValueError as error:
            errors.append(f".{provider}/skills/{name}/SKILL.md: {error}")
            continue
        if bridge_fields != fields:
            errors.append(
                f".{provider}/skills/{name}/SKILL.md: frontmatter must match the canonical skill"
            )
        if bridge_body.strip() != BRIDGE_BODY.format(name=name):
            errors.append(
                f".{provider}/skills/{name}/SKILL.md: "
                "must stay a thin pointer to the canonical skill"
            )


def _check_skills(root: Path, names: tuple[str, ...], errors: list[str]) -> None:
    if not names:
        errors.append(".agents/skills must define at least one skill")
        return

    for name in names:
        canonical = root / CANONICAL_SKILLS / name / "SKILL.md"
        if not canonical.is_file():
            continue
        try:
            fields, body = _parse_frontmatter(canonical)
        except ValueError as error:
            errors.append(f".agents/skills/{name}/SKILL.md: {error}")
            continue

        if set(fields) != {"name", "description"}:
            errors.append(
                f".agents/skills/{name}/SKILL.md: frontmatter must be name and description"
            )
        if fields.get("name") != name:
            errors.append(f".agents/skills/{name}/SKILL.md: name must match the directory")
        if len(fields.get("description", "").split()) < MINIMUM_DESCRIPTION_WORDS:
            errors.append(f".agents/skills/{name}/SKILL.md: description must state a real trigger")
        if "just " not in body or "AGENTS.md" not in body:
            errors.append(
                f".agents/skills/{name}/SKILL.md: a skill must cite AGENTS.md and use just recipes"
            )
        _check_bridges(root, name, fields, errors)


def main() -> int:
    """Report every inconsistency in the agent surface at once."""
    root = _root()
    if not (root / CANONICAL_SKILLS).is_dir():
        print("agent validation: .agents/skills is missing", file=sys.stderr)
        return 1

    errors: list[str] = []
    try:
        vendored = _vendored_names(root)
        names = _skill_names(root, vendored)
        _check_inventory(root, names, vendored, errors)
        _check_vendored(root, vendored, errors)
    except (RuntimeError, TypeError) as failure:
        print(f"agent validation: {failure}", file=sys.stderr)
        return 1
    _check_canonical(root, errors)
    _check_adapters(root, errors)
    _check_skills(root, names, errors)

    if errors:
        for error in sorted(set(errors)):
            print(f"agent validation: {error}", file=sys.stderr)
        return 1
    print(
        f"Validated AGENTS.md, {len(ADAPTERS)} adapters, {len(names)} skills, "
        f"and {len(vendored)} vendored skills."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
