"""`docmirror verify`: offline checks of the output tree against the manifest."""

from __future__ import annotations

import json
import posixpath
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from docmirror.cli.common import Common, config_for, fail
from docmirror.convert.frontmatter import body_sha256, split_frontmatter
from docmirror.exit_codes import ExitCode
from docmirror.links.rewriter import (
    _FENCE,
    _HEADING_ANCHOR,
    _HTML_ID,
    _MD_LINK,
    has_anchor,
    outside_code_spans,
)
from docmirror.quality.measure import LANG_RATE_GATE, count_markdown
from docmirror.quality.metrics import GATE_NAMES
from docmirror.report.models import Frontmatter
from docmirror.state.db import open_manifest

REQUIRED_KEYS = (
    "source_url",
    "title",
    "fetched_at",
    "content_sha256",
    "quality_score",
    "low_confidence",
)
TOOL_FILES = {"index.md", "index.jsonl", "llms.txt", "crawl-report.json", "docmirror.toml"}
_HTML_HREF = re.compile(r'<a\b[^>]*?\bhref="([^"]*)"')


@dataclass(slots=True)
class VerifyResult:
    """Everything `verify` found."""

    pages: int = 0
    problems: list[tuple[str, str]] = field(default_factory=list)
    broken_links: list[tuple[str, str, str]] = field(default_factory=list)
    gate_failures: dict[str, int] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        """Whether nothing failed."""
        return not self.problems and not self.broken_links


def _links_outside_code(body: str) -> list[str]:
    targets: list[str] = []
    in_code = False
    fence = ""
    for line in body.split("\n"):
        match = _FENCE.match(line)
        if in_code:
            stripped = line.strip()
            if (
                stripped.startswith(fence[0])
                and set(stripped) == {fence[0]}
                and len(stripped) >= len(fence)
            ):
                in_code = False
            continue
        if match:
            in_code = True
            fence = match.group(2)
            continue
        outside_code_spans(line, lambda text: _collect_targets(text, targets))
    return targets


def _collect_targets(text: str, targets: list[str]) -> str:
    targets.extend(m.group("target") for m in _MD_LINK.finditer(text))
    targets.extend(_HTML_HREF.findall(text))
    return text


def _anchors(body: str) -> set[str]:
    anchors: set[str] = set()
    for line in body.splitlines():
        match = _HEADING_ANCHOR.search(line)
        if match:
            anchors.add(match.group(1))
    anchors.update(_HTML_ID.findall(body))
    return anchors


def _check_page(
    out_dir: Path, row: sqlite3.Row, result: VerifyResult
) -> tuple[str, set[str]] | None:
    """Check one manifest page's file and frontmatter; return its body and anchors."""
    path = str(row["path"])
    target = out_dir / path
    if not target.is_file():
        result.problems.append((path, "listed in the manifest but missing from the tree"))
        return None
    frontmatter, body = split_frontmatter(target.read_text(encoding="utf-8"))
    result.pages += 1
    missing = [key for key in REQUIRED_KEYS if key not in frontmatter]
    if missing:
        result.problems.append((path, f"frontmatter lacks {', '.join(missing)}"))
        return body, _anchors(body)
    try:
        Frontmatter.model_validate(frontmatter)
    except ValueError as error:
        result.problems.append((path, f"frontmatter invalid: {error}"))
    if frontmatter.get("content_sha256") != body_sha256(body):
        result.problems.append((path, "content_sha256 does not match the body"))
    counts = count_markdown(body)
    # Each gate counts once per page: the stored flags, plus the one gate `verify`
    # can re-measure from the Markdown alone.
    failed = {flag for flag in frontmatter.get("quality_flags") or [] if flag in GATE_NAMES}
    if counts.fences and counts.fences_tagged / counts.fences < LANG_RATE_GATE:
        failed.add("code_lang_rate")
    for gate in sorted(failed):
        result.gate_failures[gate] = result.gate_failures.get(gate, 0) + 1
    return body, _anchors(body)


def _check_links(
    out_dir: Path, bodies: dict[str, str], anchors: dict[str, set[str]], result: VerifyResult
) -> None:
    for path, body in bodies.items():
        for href in _links_outside_code(body):
            if "://" in href or href.startswith(("mailto:", "tel:", "#", "data:")):
                if href.startswith("#") and href[1:] and not has_anchor(anchors[path], href[1:]):
                    result.broken_links.append((path, href, "fragment not found on the page"))
                continue
            rel, _, fragment = href.partition("#")
            base = posixpath.dirname(path)
            resolved = posixpath.normpath(posixpath.join(base, rel)) if rel else path
            if resolved not in bodies:
                if not (out_dir / resolved).exists():
                    result.broken_links.append((path, href, "target file not found"))
                continue
            if fragment and not has_anchor(anchors[resolved], fragment):
                reason = f"fragment #{fragment} not found in {resolved}"
                result.broken_links.append((path, href, reason))


def verify_tree(out_dir: Path) -> VerifyResult:
    """Run every check and collect the findings."""
    result = VerifyResult()
    with open_manifest(out_dir) as manifest:
        rows = manifest.pages(written_only=True)
        manifest_paths = {str(row["path"]) for row in rows}
        bodies: dict[str, str] = {}
        anchors: dict[str, set[str]] = {}
        for row in rows:
            checked = _check_page(out_dir, row, result)
            if checked is None:
                continue
            path = str(row["path"])
            bodies[path] = checked[0]
            anchors[path] = checked[1] | manifest.anchors(str(row["normalized_url"]))
        _check_links(out_dir, bodies, anchors, result)
        for file in out_dir.rglob("*.md"):
            rel = file.relative_to(out_dir).as_posix()
            if (
                rel.startswith(("_removed/", ".docmirror/"))
                or rel in TOOL_FILES
                or rel.endswith("/_index.md")
            ):
                continue
            if rel not in manifest_paths:
                result.problems.append((rel, "in the tree but not in the manifest"))
    return result


def run_verify(out_dir: Path, common: Common) -> ExitCode:
    """Print the findings; exit 4 when any check failed."""
    if not out_dir.is_dir():
        fail(f"{out_dir} is not a directory", ExitCode.USAGE)
    config_for(out_dir, common)
    result = verify_tree(out_dir)
    if common.json_events:
        print(
            json.dumps(
                {
                    "event": "verify",
                    "pages": result.pages,
                    "ok": result.ok,
                    "problems": [{"path": p, "problem": m} for p, m in result.problems],
                    "broken_links": [
                        {"from_path": p, "href": h, "reason": r} for p, h, r in result.broken_links
                    ],
                    "gate_failures": result.gate_failures,
                }
            )
        )
    else:
        print(f"verify: {result.pages} pages checked")
        for path, problem in result.problems:
            print(f"  problem  {path}: {problem}")
        for path, href, reason in result.broken_links:
            print(f"  link     {path}: {href} ({reason})")
        if result.gate_failures:
            print(
                "  gate failures recorded: "
                + ", ".join(f"{k}={v}" for k, v in sorted(result.gate_failures.items()))
            )
        print(
            "verify: ok"
            if result.ok
            else f"verify: {len(result.problems)} problems, {len(result.broken_links)} broken links"
        )
    return ExitCode.OK if result.ok else ExitCode.QUALITY
