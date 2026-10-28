"""GFM footnotes when the source uses a recognizable `fnref`/`fn` pattern; else plain links."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from urllib.parse import urldefrag

from lxml import etree, html

if TYPE_CHECKING:
    from collections.abc import Callable

    from docmirror.normalize.islands import Islands

_REF = re.compile(r"^#?(?:fn|footnote)[-:_]?(?:ref[-:_]?)?([A-Za-z0-9_-]+)$")
_BACKREF_PREFIXES = ("fnref", "footnote-ref", "fn-ref")


def _same_page_fragment(href: str, page: str | None) -> str:
    """The fragment of a link to this page, or empty for a link elsewhere.

    Extraction makes links absolute, so a same-page link is the page URL plus a fragment;
    without a known page URL only a bare `#fragment` counts.
    """
    if href.startswith("#"):
        return href[1:]
    if page is None:
        return ""
    target, fragment = urldefrag(href)
    return fragment if target == urldefrag(page)[0] else ""


def transform(content: html.HtmlElement, islands: Islands, convert: Callable[[str], str]) -> None:
    """Rewrite footnote references and definitions."""
    definitions: dict[str, html.HtmlElement] = {}
    for item in content.iter("li", "div", "p"):
        identifier = item.get("id") or ""
        match = _REF.match(identifier)
        if match and "ref" not in identifier.lower():
            definitions[match.group(1)] = item
    if not definitions:
        return
    page = content.base_url
    # Backlinks go first, so the reference pass below cannot take one for a reference.
    for item in definitions.values():
        for back in list(item.iter("a")):
            if _same_page_fragment(back.get("href") or "", page).startswith(
                _BACKREF_PREFIXES
            ) or "footnote-backref" in (back.get("class") or ""):
                back.drop_tree()
    for anchor in list(content.iter("a")):
        fragment = _same_page_fragment(anchor.get("href") or "", page)
        match = _REF.match("#" + fragment) if fragment else None
        if not match or "ref" in fragment.lower() or match.group(1) not in definitions:
            continue
        label = match.group(1)
        holder = anchor
        parent = anchor.getparent()
        if (
            parent is not None
            and parent.tag == "sup"
            and len(parent) == 1
            and not (parent.text or "").strip()
        ):
            holder = parent
        islands.replace_element(holder, f"[^{label}]", block=False)
    blocks: list[str] = []
    for label, item in definitions.items():
        inner = (item.text or "") + "".join(
            etree.tostring(c, encoding="unicode", method="html") for c in item
        )
        text = islands.restore(convert(inner)).strip().replace("\n", "\n    ")
        blocks.append(f"[^{label}]: {text}")
        item.getparent().remove(item) if item.getparent() is not None else None
    for section in list(content.iter("section", "div", "ol")):
        if (
            section.getparent() is not None
            and "footnote" in (section.get("class") or "")
            and not section.text_content().strip()
        ):
            section.drop_tree()
    trailer = html.Element("p")
    trailer.text = islands.register("\n".join(blocks))
    content.append(trailer)
