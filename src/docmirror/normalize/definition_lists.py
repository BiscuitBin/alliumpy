"""`<dl>` becomes `**term**` plus a four-space-indented definition; block definitions stay HTML."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from lxml import etree, html

from docmirror.normalize.islands import sanitize

if TYPE_CHECKING:
    from docmirror.normalize.islands import Islands

_WS = re.compile(r"\s+")
BLOCK_TAGS = frozenset({"p", "div", "ul", "ol", "pre", "table", "dl", "blockquote", "figure"})


def _has_block(definition: html.HtmlElement) -> bool:
    children = [c for c in definition if isinstance(c.tag, str)]
    if len(children) == 1 and children[0].tag == "p":
        return False
    return any(c.tag in BLOCK_TAGS for c in children)


def transform(content: html.HtmlElement, islands: Islands) -> None:
    """Rewrite each definition list."""
    for dl in list(content.iter("dl")):
        if dl.getparent() is None:
            continue
        definitions = [c for c in dl if c.tag == "dd"]
        if any(_has_block(dd) for dd in definitions):
            islands.replace_element(dl, sanitize(dl))
            continue
        indent = islands.register("    ")
        holder = html.Element("div")
        paragraph: html.HtmlElement | None = None
        for child in dl:
            if child.tag == "dt":
                # A term and its definitions share one paragraph, separated by hard
                # breaks, so the four-space indent is a continuation line and never an
                # indented code block.
                paragraph = etree.SubElement(holder, "p")
                strong = etree.SubElement(paragraph, "strong")
                strong.text = child.text
                for grandchild in list(child):
                    strong.append(grandchild)
            elif child.tag == "dd":
                if paragraph is None:
                    paragraph = etree.SubElement(holder, "p")
                etree.SubElement(paragraph, "br")
                marker = etree.SubElement(paragraph, "span")
                marker.text = indent
                source = child
                only = [c for c in child if isinstance(c.tag, str)]
                if len(only) == 1 and only[0].tag == "p" and not (child.text or "").strip():
                    source = only[0]
                marker.tail = _WS.sub(" ", source.text or "").lstrip() or None
                for grandchild in list(source):
                    if grandchild.tail:
                        grandchild.tail = _WS.sub(" ", grandchild.tail)
                    paragraph.append(grandchild)
        holder.tail = dl.tail
        parent = dl.getparent()
        if parent is not None:
            parent.replace(dl, holder)
