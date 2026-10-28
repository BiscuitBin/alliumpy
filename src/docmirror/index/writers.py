"""`index.md`, `index.jsonl`, `llms.txt` and per-directory `_index.md`, sorted by path."""

from __future__ import annotations

import json
import posixpath
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from docmirror.convert.frontmatter import render_frontmatter, split_frontmatter
from docmirror.index.keywords import compute_keywords
from docmirror.index.summarize import summarizer_for
from docmirror.report.models import IndexEntry
from docmirror.state.db import atomic_write_text, now_iso

if TYPE_CHECKING:
    from pathlib import Path

    from docmirror.config.models import Config
    from docmirror.report.builder import ReportBuilder
    from docmirror.state.db import Manifest

LLMS_CAP = 2000


@dataclass(slots=True)
class IndexedPage:
    """One page as the writers see it."""

    entry: IndexEntry
    directory: str
    headings: list[str] = field(default_factory=list)


def _description(frontmatter: dict[str, object], body: str) -> str:
    text = str(frontmatter.get("description") or "")
    if text:
        return text
    from docmirror.pipeline import _first_paragraph  # noqa: PLC0415

    return _first_paragraph(body)


def collect_pages(config: Config, out_dir: Path, manifest: Manifest) -> list[IndexedPage]:
    """Read every written page, compute or load its keywords, and write them back."""
    rows = manifest.pages(written_only=True)
    bodies: dict[str, str] = {}
    texts: dict[str, tuple[dict[str, object], str]] = {}
    for row in rows:
        target = out_dir / str(row["path"])
        if not target.is_file():
            continue
        frontmatter, body = split_frontmatter(target.read_text(encoding="utf-8"))
        texts[str(row["normalized_url"])] = (frontmatter, body)
        sha = str(frontmatter.get("content_sha256") or row["content_sha256"] or "")
        if manifest.cached_keywords(sha) is None:
            bodies[str(row["normalized_url"])] = body
    if bodies:
        fresh = compute_keywords(bodies, limit=config.index.keywords_per_page)
        for url, keywords in fresh.items():
            frontmatter, _ = texts[url]
            manifest.cache_keywords(str(frontmatter.get("content_sha256") or ""), keywords)
    summarizer = summarizer_for(config.index.summarizer)
    outbound, inbound = manifest.link_counts()
    pages: list[IndexedPage] = []
    for row in rows:
        url = str(row["normalized_url"])
        if url not in texts:
            continue
        frontmatter, body = texts[url]
        sha = str(frontmatter.get("content_sha256") or "")
        keywords = manifest.cached_keywords(sha) or []
        if frontmatter.get("keywords") != keywords:
            frontmatter["keywords"] = keywords
            atomic_write_text(
                out_dir / str(row["path"]), render_frontmatter(frontmatter) + "\n" + body
            )
            manifest.upsert_page(url, frontmatter=frontmatter)
        headings = json.loads(row["headings_json"]) if row["headings_json"] else []
        title = str(frontmatter.get("title") or row["title"] or row["path"])
        description = summarizer.summarize(title, body, _description(frontmatter, body))
        entry = IndexEntry(
            path=str(row["path"]),
            source_url=str(frontmatter.get("source_url") or url),
            title=title,
            description=description,
            keywords=keywords,
            headings=headings,
            version=_opt_str(frontmatter.get("version")),
            locale=_opt_str(frontmatter.get("locale")),
            quality_score=float(str(frontmatter.get("quality_score") or 0.0)),
            low_confidence=bool(frontmatter.get("low_confidence")),
            quality_flags=[str(f) for f in _as_list(frontmatter.get("quality_flags"))],
            content_sha256=sha,
            fetched_at=str(frontmatter.get("fetched_at") or ""),
            last_modified=_opt_str(frontmatter.get("last_modified")),
            word_count=int(row["word_count"] or len(body.split())),
            outbound_internal=outbound.get(url, 0),
            inbound_internal=inbound.get(url, 0),
        )
        directory = posixpath.dirname(entry.path) or "."
        pages.append(IndexedPage(entry=entry, directory=directory, headings=headings))
    pages.sort(key=lambda p: p.entry.path)
    return pages


def _opt_str(value: object) -> str | None:
    return None if value is None else str(value)


def _as_list(value: object) -> list[object]:
    return list(value) if isinstance(value, list) else []


def _top_directory(path: str) -> str:
    return path.split("/", 1)[0] if "/" in path else "."


def _entry_line(page: IndexedPage, base: str) -> str:
    entry = page.entry
    rel = posixpath.relpath(entry.path, base) if base != "." else entry.path
    line = f"- [{entry.title}]({rel})"
    if entry.description:
        line += f" — {entry.description}"
    if entry.keywords:
        line += f" _Keywords:_ {', '.join(entry.keywords)}"
    if entry.low_confidence:
        line += " ⚠ low confidence"
    if page.headings:
        line += "\n  Sections: " + " · ".join(page.headings)
    return line


def write_index_md(
    config: Config, out_dir: Path, pages: list[IndexedPage], report: ReportBuilder | None
) -> None:
    """The human index, grouped by top-level directory, with `_index.md` for large ones."""
    threshold = config.index.hierarchical_threshold
    groups: dict[str, list[IndexedPage]] = {}
    for page in pages:
        groups.setdefault(_top_directory(page.entry.path), []).append(page)
    lines = [f"# {config.site.name or config.site.root_url} documentation index", ""]
    lines.append(f"Source: <{config.site.root_url}>  ")
    lines.append(f"Pages: {len(pages)}  ")
    run_time = report.run_id if report is not None else now_iso()
    lines.append(f"Last run: {run_time}  ")
    lines.append("Report: [crawl-report.json](crawl-report.json)")
    lines.append("")
    for directory in sorted(groups):
        members = groups[directory]
        heading = directory if directory != "." else "(root)"
        lines.append(f"## {heading}")
        lines.append("")
        if len(members) > threshold and directory != ".":
            sub = [f"# {directory}", "", f"{len(members)} pages.", ""]
            sub.extend(_entry_line(page, directory) for page in members)
            atomic_write_text(out_dir / directory / "_index.md", "\n".join(sub) + "\n")
            lines.append(f"- [{directory}]({directory}/_index.md) — {len(members)} pages")
        else:
            lines.extend(_entry_line(page, ".") for page in members)
        lines.append("")
    atomic_write_text(out_dir / "index.md", "\n".join(lines).rstrip("\n") + "\n")


def write_index_jsonl(out_dir: Path, pages: list[IndexedPage]) -> None:
    """One JSON object per page, path-sorted."""
    lines = [
        json.dumps(page.entry.model_dump(), ensure_ascii=False, sort_keys=False) for page in pages
    ]
    atomic_write_text(out_dir / "index.jsonl", "\n".join(lines) + ("\n" if lines else ""))


def write_llms_txt(config: Config, out_dir: Path, pages: list[IndexedPage]) -> None:
    """The llms.txt convention: H1, blockquote summary, an H2 per directory, link lines."""
    name = config.site.name or config.site.root_url
    summary = ""
    for page in pages:
        if page.entry.path == "index.md" or page.entry.source_url.rstrip(
            "/"
        ) == config.site.root_url.rstrip("/"):
            summary = page.entry.description
            break
    if not summary and pages:
        summary = pages[0].entry.description
    lines = [f"# {name}", ""]
    if summary:
        lines.extend([f"> {summary}", ""])
    groups: dict[str, list[IndexedPage]] = {}
    for page in pages:
        groups.setdefault(_top_directory(page.entry.path), []).append(page)
    over_cap = len(pages) > LLMS_CAP
    for directory in sorted(groups):
        members = groups[directory]
        lines.append(f"## {directory if directory != '.' else 'Pages'}")
        lines.append("")
        if over_cap and directory != "." and (out_dir / directory / "_index.md").is_file():
            lines.append(f"- [{directory}]({directory}/_index.md): {len(members)} pages")
        else:
            for page in members:
                entry = page.entry
                description = f": {entry.description}" if entry.description else ""
                lines.append(f"- [{entry.title}]({entry.path}){description}")
        lines.append("")
    atomic_write_text(out_dir / "llms.txt", "\n".join(lines).rstrip("\n") + "\n")


def write_indexes(
    config: Config, out_dir: Path, manifest: Manifest, report: ReportBuilder | None
) -> list[IndexedPage]:
    """Regenerate every index file from the manifest and the written pages."""
    pages = collect_pages(config, out_dir, manifest)
    write_index_md(config, out_dir, pages, report)
    write_index_jsonl(out_dir, pages)
    write_llms_txt(config, out_dir, pages)
    return pages
