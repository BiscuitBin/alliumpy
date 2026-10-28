"""The measurement itself: DOM counts against counts in the Markdown AST.

The Markdown side is parsed with markdown-it-py (GFM tables and footnotes); raw HTML
blocks are parsed with lxml so a preserved `<table>` counts as a table, its cells as
cells, and a `<pre>` inside it as a code block.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from lxml import html
from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin

from docmirror.normalize.tables import is_layout
from docmirror.quality.metrics import QualityResult

if TYPE_CHECKING:
    from markdown_it.token import Token

_WORD = re.compile(r"[a-z0-9]+")
WEIGHTS = {
    "text_coverage": 0.40,
    "code_blocks": 0.15,
    "tables": 0.075,
    "table_cells": 0.075,
    "headings": 0.10,
    "links": 0.10,
    "code_lang_rate": 0.05,
    "images": 0.05 / 3,
    "list_items": 0.05 / 3,
    "tabs_expanded": 0.05 / 3,
}
TEXT_COVERAGE_GATE = 0.97
RATIO_GATE = 0.98
LANG_RATE_GATE = 0.90

_PARSER = MarkdownIt("commonmark", {"html": True}).enable("table").use(footnote_plugin)


@dataclass(slots=True)
class MarkdownCounts:
    """What the Markdown output carries."""

    code_blocks: int = 0
    fences: int = 0
    fences_tagged: int = 0
    tables: int = 0
    table_cells: int = 0
    headings: int = 0
    links: int = 0
    images: int = 0
    list_items: int = 0
    text: str = ""


def words(text: str) -> list[str]:
    """Lowercased alphanumeric tokens."""
    return _WORD.findall(text.lower())


def _count_html(fragment: str, counts: MarkdownCounts, text_parts: list[str]) -> None:
    try:
        root = html.fragment_fromstring(fragment, create_parent="div")
    except (ValueError, TypeError):
        return
    for element in root.iter():
        tag = element.tag
        if not isinstance(tag, str):
            continue
        if tag == "pre":
            counts.code_blocks += 1
            code = element.find("code")
            classes = (
                (code.get("class") if code is not None else None) or element.get("class") or ""
            )
            if any(c.startswith(("language-", "lang-")) for c in classes.split()):
                counts.fences_tagged += 1
        elif tag == "table":
            counts.tables += 1
        elif tag in {"td", "th"}:
            counts.table_cells += 1
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            counts.headings += 1
        elif tag == "a" and element.get("href"):
            counts.links += 1
        elif tag == "img":
            counts.images += 1
        elif tag == "li":
            counts.list_items += 1
    for pre in list(root.iter("pre")):
        pre.drop_tree()
    # Joined with spaces: text_content() would glue adjacent cells into one token.
    text_parts.append(" ".join(root.itertext()))


def count_markdown(markdown: str) -> MarkdownCounts:
    """Walk the token stream and count what the gates compare."""
    counts = MarkdownCounts()
    text_parts: list[str] = []
    tokens: list[Token] = _PARSER.parse(markdown)

    def visit(stream: list[Token]) -> None:
        for token in stream:
            if token.type == "fence":
                counts.code_blocks += 1
                counts.fences += 1
                if token.info.strip():
                    counts.fences_tagged += 1
            elif token.type == "code_block":
                counts.code_blocks += 1
            elif token.type == "table_open":
                counts.tables += 1
            elif token.type in {"td_open", "th_open"}:
                counts.table_cells += 1
            elif token.type == "heading_open":
                counts.headings += 1
            elif token.type == "list_item_open":
                counts.list_items += 1
            elif token.type == "html_block":
                _count_html(token.content, counts, text_parts)
            elif token.type == "inline":
                for child in token.children or []:
                    if child.type == "link_open":
                        counts.links += 1
                    elif child.type == "image":
                        counts.images += 1
                        text_parts.append(child.content)
                    elif child.type in {"text", "code_inline"}:
                        text_parts.append(child.content)
                    elif child.type == "html_inline":
                        _count_html(child.content, counts, text_parts)
                    elif child.type in {"softbreak", "hardbreak"}:
                        text_parts.append(" ")
                if token.children:
                    visit(token.children)

    visit(tokens)
    counts.text = " ".join(text_parts)
    return counts


def text_coverage(dom_words: list[str], markdown_words: list[str]) -> float:
    """Recall of DOM word tokens found in the Markdown text."""
    if not dom_words:
        return 1.0
    have: dict[str, int] = {}
    for token in markdown_words:
        have[token] = have.get(token, 0) + 1
    hit = 0
    for token in dom_words:
        count = have.get(token, 0)
        if count:
            have[token] = count - 1
            hit += 1
    return hit / len(dom_words)


def _dom_words(dom: html.HtmlElement) -> list[str]:
    parts: list[str] = []
    for element in dom.iter():
        if not isinstance(element.tag, str):
            continue
        if element.tag == "pre" or any(a.tag == "pre" for a in element.iterancestors()):
            continue
        if element.text:
            parts.append(element.text)
        if element.tail:
            parts.append(element.tail)
    return words(" ".join(parts))


def _ratio(have: int, want: int) -> float:
    if want == 0:
        return 1.0
    return min(have / want, 1.0)


def measure(dom: html.HtmlElement, markdown: str, counts: dict[str, int]) -> QualityResult:
    """Every gate of the specification, from the DOM counts and the Markdown counts."""
    md = count_markdown(markdown)
    dom_words = _dom_words(dom)
    coverage = text_coverage(dom_words, words(md.text))
    # Element counts come from the normalized tree plus its HTML islands: what the page
    # must carry after tabs were expanded and chrome removed. The DOM copy is the
    # fallback for a caller without counts, and the source of the text-coverage words.
    dom_code = counts.get("code_blocks", sum(1 for _ in dom.iter("pre")))
    dom_tables = counts.get("tables", sum(1 for t in dom.iter("table") if not is_layout(t)))
    dom_cells = counts.get("table_cells", sum(1 for _ in dom.iter("td", "th")))
    dom_headings = counts.get(
        "headings", sum(1 for _ in dom.iter("h1", "h2", "h3", "h4", "h5", "h6"))
    )
    dom_links = counts.get("links", sum(1 for a in dom.iter("a") if a.get("href")))
    dom_images = counts.get("images", sum(1 for _ in dom.iter("img")))
    dom_items = counts.get("list_items", sum(1 for _ in dom.iter("li")))
    tabs_found = counts.get("tab_panels", 0)
    tabs_emitted = counts.get("tab_panels_emitted", 0)
    lang_rate = (md.fences_tagged / md.fences) if md.fences else 1.0
    metrics = {
        "text_coverage": round(coverage, 4),
        "code_blocks": float(md.code_blocks),
        "dom_code_blocks": float(dom_code),
        "code_lang_rate": round(lang_rate, 4),
        "tables": float(md.tables),
        "dom_tables": float(dom_tables),
        "table_cells": float(md.table_cells),
        "dom_table_cells": float(dom_cells),
        "headings": float(md.headings),
        "dom_headings": float(dom_headings),
        "links": float(md.links),
        "dom_links": float(dom_links),
        "images": float(md.images),
        "dom_images": float(dom_images),
        "list_items": float(md.list_items),
        "dom_list_items": float(dom_items),
        "tabs_found": float(tabs_found),
        "tabs_emitted": float(tabs_emitted),
    }
    passed = {
        "text_coverage": coverage >= TEXT_COVERAGE_GATE,
        "code_blocks": md.code_blocks == dom_code,
        "code_lang_rate": lang_rate >= LANG_RATE_GATE or md.fences == 0,
        "tables": md.tables == dom_tables,
        "table_cells": md.table_cells == dom_cells,
        "headings": md.headings == dom_headings,
        "links": _ratio(md.links, dom_links) >= RATIO_GATE,
        "images": md.images == dom_images,
        "list_items": _ratio(md.list_items, dom_items) >= RATIO_GATE,
        "tabs_expanded": tabs_found == tabs_emitted,
    }
    score = sum(WEIGHTS[g] for g, ok in passed.items() if ok) / sum(WEIGHTS.values())
    return QualityResult(
        metrics=metrics,
        failed=[gate for gate, ok in passed.items() if not ok],
        score=round(score, 4),
    )
