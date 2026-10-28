"""Rewrite links in written pages: in-manifest targets become relative paths.

Runs once every page of a run is known, over every written page, and is idempotent: a
relative link whose target is still written stays as it is, one whose target was
removed goes back to its absolute source URL, and an absolute link whose target is now
written becomes relative. Fragments ride along and are checked against the target's
anchors.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import unquote, urljoin, urlsplit

from docmirror.convert.frontmatter import body_sha256, render_frontmatter, split_frontmatter
from docmirror.links.paths import relative_path
from docmirror.state.db import atomic_write_text

if TYPE_CHECKING:
    from collections.abc import Callable

    from docmirror.frontier.urls import ScopeRules, UrlNormalizer
    from docmirror.pipeline import Crawler
    from docmirror.state.db import Manifest

# `[text](target "title")` and `](target)` with balanced parentheses in the target.
_MD_LINK = re.compile(
    r"(?<!\!)\]\((?P<target>[^()\s]+(?:\([^()\s]*\)[^()\s]*)*)(?P<title>\s+\"[^\"]*\")?\)"
)
_HTML_HREF = re.compile(r'(?P<prefix><a\b[^>]*?\bhref=")(?P<target>[^"]*)(?P<suffix>")')
_FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})")
_BACKTICKS = re.compile(r"`+")
_HEADING_ANCHOR = re.compile(r"\{#([^}\s]+)\}\s*$")
_HTML_ID = re.compile(r'\bid="([^"]+)"')


@dataclass(slots=True)
class PageRow:
    """The rewriter's view of a written page."""

    normalized_url: str
    path: str
    source_url: str
    tombstoned: bool


@dataclass(slots=True)
class RewriteOutcome:
    """Flags and link rows the rewrite produced for one page."""

    flags: set[str] = field(default_factory=set)
    links: list[tuple[str, str, str, str | None]] = field(default_factory=list)
    broken: list[tuple[str, str]] = field(default_factory=list)


class LinkRewriter:
    """Resolves link targets against the manifest."""

    def __init__(
        self,
        manifest: Manifest,
        normalizer: UrlNormalizer,
        scope: ScopeRules,
        out_dir: Path,
    ) -> None:
        """Index every known page by URL and by path."""
        self.manifest = manifest
        self.normalizer = normalizer
        self.scope = scope
        self.out_dir = out_dir
        self.by_url: dict[str, PageRow] = {}
        self.by_path: dict[str, PageRow] = {}
        for row in manifest.pages():
            if not row["path"]:
                continue
            frontmatter = row["frontmatter_json"]
            source = row["canonical_url"] or row["normalized_url"]
            if frontmatter:
                import json  # noqa: PLC0415

                source = json.loads(frontmatter).get("source_url", source)
            page = PageRow(
                normalized_url=str(row["normalized_url"]),
                path=str(row["path"]),
                source_url=str(source),
                tombstoned=row["tombstoned_at"] is not None or row["status"] != "written",
            )
            self.by_url[page.normalized_url] = page
            self.by_path[page.path] = page
        self._anchor_cache: dict[str, set[str]] = {}

    def anchors_of(self, page: PageRow) -> set[str]:
        """The fragment anchors a written page carries, from the manifest and its text."""
        cached = self._anchor_cache.get(page.normalized_url)
        if cached is not None:
            return cached
        anchors = set(self.manifest.anchors(page.normalized_url))
        target = self.out_dir / page.path
        if target.is_file():
            _, body = split_frontmatter(target.read_text(encoding="utf-8"))
            for line in body.splitlines():
                match = _HEADING_ANCHOR.search(line)
                if match:
                    anchors.add(match.group(1))
            anchors.update(_HTML_ID.findall(body))
        self._anchor_cache[page.normalized_url] = anchors
        return anchors

    def resolve(self, current: PageRow, target: str, outcome: RewriteOutcome) -> str:
        """The rewritten form of one link target found in `current`."""
        if target.startswith(("mailto:", "tel:", "javascript:", "data:")):
            return target
        if target.startswith("#"):
            self._check_fragment(current, target[1:], outcome, target)
            return target
        parts = urlsplit(target)
        if not parts.scheme and not target.startswith("/"):
            # A relative link this tool wrote earlier: find its page by path.
            # (A site-absolute `/path` is resolved against the source URL below.)
            path_part, _, fragment = target.partition("#")
            resolved = _join_path(current.path, path_part)
            known = self.by_path.get(resolved)
            if known is None:
                return target
            if known.tombstoned:
                outcome.flags.add("dangling_inbound")
                outcome.broken.append((target, "target removed"))
                return known.source_url + (f"#{fragment}" if fragment else "")
            self._check_fragment(known, fragment, outcome, target)
            outcome.links.append((known.normalized_url, fragment, "internal", known.path))
            return target
        absolute = urljoin(current.source_url, target)
        normalized, fragment = self.normalizer.split_fragment(absolute)
        normalized = self.normalizer.normalize(self.scope.with_locale(normalized))
        alias = self.manifest.resolve_alias(normalized)
        if alias:
            normalized = alias
        if normalized == current.normalized_url:
            # A self-link is no edge of the graph, exactly as a bare `#fragment` is not,
            # so the counts do not change once it has been rewritten to one.
            self._check_fragment(current, fragment, outcome, target)
            return f"#{fragment}" if fragment else _source_form(target, absolute)
        known = self.by_url.get(normalized)
        if known is not None and not known.tombstoned:
            self._check_fragment(known, fragment, outcome, target)
            outcome.links.append((normalized, fragment, "internal", known.path))
            rel = relative_path(current.path, known.path)
            return rel + (f"#{fragment}" if fragment else "")
        if self.scope.in_scope(normalized):
            outcome.flags.add("uncrawled_internal")
            outcome.links.append((normalized, fragment, "uncrawled", None))
        else:
            outcome.links.append((normalized, fragment, "external", None))
        return _source_form(target, absolute)

    def _check_fragment(
        self, known: PageRow, fragment: str, outcome: RewriteOutcome, target: str
    ) -> None:
        if fragment and not has_anchor(self.anchors_of(known), fragment):
            outcome.flags.add("unresolved_fragment")
            outcome.broken.append((target, f"fragment #{fragment} not found in {known.path}"))

    def rewrite_text(self, current: PageRow, body: str) -> tuple[str, RewriteOutcome]:
        """Rewrite every link outside fenced code in `body`."""
        outcome = RewriteOutcome()
        out: list[str] = []
        in_code = False
        fence = ""
        for line in body.split("\n"):
            match = _FENCE.match(line)
            if in_code:
                out.append(line)
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
                out.append(line)
                continue
            out.append(
                outside_code_spans(line, lambda text: self._rewrite_links(current, text, outcome))
            )
        return "\n".join(out), outcome

    def _rewrite_links(self, current: PageRow, text: str, outcome: RewriteOutcome) -> str:
        rewritten = _MD_LINK.sub(
            lambda m: (
                "]("
                + self.resolve(current, m.group("target"), outcome)
                + (m.group("title") or "")
                + ")"
            ),
            text,
        )
        return _HTML_HREF.sub(
            lambda m: (
                m.group("prefix")
                + self.resolve(current, m.group("target"), outcome)
                + m.group("suffix")
            ),
            rewritten,
        )


def outside_code_spans(line: str, fn: Callable[[str], str]) -> str:
    """Apply `fn` to the parts of one line outside its inline code spans.

    A span opens on a run of n backticks and closes on the next run of exactly n, as in
    CommonMark; an unmatched run is literal text. Spans are matched within one line,
    which is the shape the converter emits.

    >>> outside_code_spans("a `b` ``c`` ` d", str.upper)
    'A `b` ``c`` ` D'
    """
    out: list[str] = []
    start = 0
    pos = 0
    while (opening := _BACKTICKS.search(line, pos)) is not None:
        width = len(opening.group())
        closing = next(
            (m for m in _BACKTICKS.finditer(line, opening.end()) if len(m.group()) == width),
            None,
        )
        if closing is None:
            pos = opening.end()
            continue
        out.append(fn(line[start : opening.start()]))
        out.append(line[opening.start() : closing.end()])
        start = pos = closing.end()
    out.append(fn(line[start:]))
    return "".join(out)


def _source_form(target: str, absolute: str) -> str:
    """A target left unrewritten: a site-absolute `/path` becomes its absolute URL."""
    return absolute if target.startswith("/") else target


def _canonical(fragment: str) -> str:
    return html.unescape(unquote(fragment))


def has_anchor(anchors: set[str], fragment: str) -> bool:
    """Whether a page carries the fragment, as written, percent-decoded or HTML-unescaped.

    A javadoc anchor holds spaces and angle brackets: the href carries `%20` and
    `&lt;`, the heading suffix carries the raw characters.

    >>> has_anchor({"apply(a, b)"}, "apply(a,%20b)")
    True
    >>> has_anchor({"get(Optional<Q>)"}, "get(Optional&lt;Q&gt;)")
    True
    """
    if fragment in anchors:
        return True
    wanted = _canonical(fragment)
    return any(_canonical(anchor) == wanted for anchor in anchors)


def _join_path(current_path: str, relative: str) -> str:
    import posixpath  # noqa: PLC0415

    base = posixpath.dirname(current_path)
    return posixpath.normpath(posixpath.join(base, relative)) if relative else current_path


def rewrite_all(crawler: Crawler) -> None:
    """Rewrite every written page of the crawl's output directory."""
    rewriter = LinkRewriter(crawler.manifest, crawler.normalizer, crawler.scope, crawler.out_dir)
    from docmirror.report.models import BrokenLink  # noqa: PLC0415

    for page in list(rewriter.by_url.values()):
        if page.tombstoned:
            continue
        target = crawler.out_dir / page.path
        if not target.is_file():
            continue
        text = target.read_text(encoding="utf-8")
        frontmatter, body = split_frontmatter(text)
        new_body, outcome = rewriter.rewrite_text(page, body)
        flags = set(frontmatter.get("quality_flags") or [])
        flags -= {"uncrawled_internal", "unresolved_fragment", "dangling_inbound"}
        flags |= outcome.flags
        sha = body_sha256(new_body)
        frontmatter["quality_flags"] = sorted(flags)
        frontmatter["content_sha256"] = sha
        new_text = render_frontmatter(frontmatter) + "\n" + new_body
        if new_text != text:
            atomic_write_text(target, new_text)
        crawler.manifest.upsert_page(
            page.normalized_url, content_sha256=sha, flags=sorted(flags), frontmatter=frontmatter
        )
        crawler.manifest.replace_links(page.normalized_url, outcome.links)
        for href, reason in outcome.broken:
            crawler.report.broken_links.append(
                BrokenLink(from_path=page.path, href=href, reason=reason)
            )
