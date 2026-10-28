"""Unknown custom elements become plain containers so no converter drops their children."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml import html

BLOCK_TAGS = frozenset(
    {
        "p",
        "div",
        "section",
        "article",
        "pre",
        "table",
        "ul",
        "ol",
        "li",
        "dl",
        "blockquote",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "figure",
        "details",
        "aside",
        "nav",
        "header",
        "footer",
        "hr",
        "img",
    }
)


def _has_block_child(element: html.HtmlElement) -> bool:
    return any(isinstance(child.tag, str) and child.tag in BLOCK_TAGS for child in element)


def transform(content: html.HtmlElement) -> None:
    """Rename every `custom-element` to `div` (block children) or `span` (inline only)."""
    for element in list(content.iter()):
        tag = element.tag
        if not isinstance(tag, str) or "-" not in tag:
            continue
        element.tag = (
            "div"
            if _has_block_child(element) or tag.endswith(("-code", "-panel", "-selector"))
            else "span"
        )
        for name in list(element.attrib):
            if name not in {"id", "class", "data-docmirror-tab-lang"}:
                del element.attrib[name]
