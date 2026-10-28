"""GFM footnotes when the source uses a recognizable `fnref`/`fn` pattern; else plain links."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from lxml import etree, html

if TYPE_CHECKING:
    from collections.abc import Callable

    from docmirror.normalize.islands import Islands

_REF = re.compile(r"^#?(?:fn|footnote)[-:_]?(?:ref[-:_]?)?([A-Za-z0-9_-]+)$")


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
    for anchor in list(content.iter("a")):
        href = anchor.get("href") or ""
        fragment = href.rsplit("#", 1)[-1] if "#" in href else ""
        match = _REF.match("#" + fragment) if fragment else None
        if not match or match.group(1) not in definitions:
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
        for back in list(item.iter("a")):
            if (back.get("href") or "").lstrip("#").startswith(
                ("fnref", "footnote-ref", "fn-ref")
            ) or "footnote-backref" in (back.get("class") or ""):
                back.drop_tree()
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
