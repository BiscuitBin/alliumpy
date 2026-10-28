"""Raw-HTML islands: subtrees that stay HTML in the Markdown, carried through conversion.

A converter cannot be told "keep this table but not that one", so an island is replaced
by a unique token before conversion and the sanitized HTML is put back afterwards. The
token is a plain word, which every backend passes through unchanged.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from lxml import etree, html

if TYPE_CHECKING:
    from collections.abc import Iterable

_TOKEN = "DOCMIRRORISLAND{index}X"
_TOKEN_RE = re.compile(r"DOCMIRRORISLAND(\d+)X")
_BLANK_LINE = re.compile(r"\n(?:[ \t]*\n)+")
_INDENT = re.compile(r"\n[ \t]+")
KEEP_ATTRIBUTES = frozenset(
    {"rowspan", "colspan", "id", "scope", "href", "src", "alt", "title", "open"}
)


def sanitize(element: html.HtmlElement, keep: Iterable[str] = KEEP_ATTRIBUTES) -> str:
    """Serialize an element keeping only the listed attributes, without scripts or styles."""
    kept = set(keep)
    for node in element.iter():
        if not isinstance(node.tag, str):
            continue
        for name in list(node.attrib):
            if name not in kept:
                del node.attrib[name]
    for node in list(element.iter("script", "style")):
        node.drop_tree()
    for pre in element.iter("pre"):
        # A blank line ends a Markdown HTML block, so none may survive inside an island;
        # inside code a lone space keeps the line without changing what it shows.
        for node in pre.iter():
            if node.text:
                node.text = _BLANK_LINE.sub("\n \n", node.text)
            if node.tail and node is not pre:
                node.tail = _BLANK_LINE.sub("\n \n", node.tail)
    serialized = etree.tostring(element, encoding="unicode", method="html").strip()
    # Outside <pre>, leading indentation is dropped too: an indented line would read as
    # an indented code block if the HTML block were ever interrupted.
    parts = re.split(r"(<pre\b.*?</pre>)", serialized, flags=re.DOTALL)
    cleaned = [part if part.startswith("<pre") else _INDENT.sub("\n", part) for part in parts]
    return _BLANK_LINE.sub("\n", "".join(cleaned))


class Islands:
    """The registry of islands for one page."""

    def __init__(self) -> None:
        """Start with no islands."""
        self._chunks: list[str] = []

    def __len__(self) -> int:
        """How many islands were registered."""
        return len(self._chunks)

    @property
    def chunks(self) -> tuple[str, ...]:
        """Every registered chunk, in registration order."""
        return tuple(self._chunks)

    def register(self, raw_html: str) -> str:
        """Register a raw chunk and return its token."""
        self._chunks.append(raw_html)
        return _TOKEN.format(index=len(self._chunks) - 1)

    def replace_element(
        self, element: html.HtmlElement, raw_html: str, *, block: bool = True
    ) -> None:
        """Swap an element for its token (as a paragraph when `block`)."""
        token = self.register(raw_html)
        holder = html.Element("p" if block else "span")
        holder.text = token
        holder.tail = element.tail
        parent = element.getparent()
        if parent is not None:
            parent.replace(element, holder)

    def restore(self, markdown: str) -> str:
        """Put every island's HTML back in place of its token."""

        def swap(match: re.Match[str]) -> str:
            index = int(match.group(1))
            return self._chunks[index] if index < len(self._chunks) else match.group(0)

        return _TOKEN_RE.sub(swap, markdown)
