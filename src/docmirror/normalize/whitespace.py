"""Outside `<pre>`, zero-width characters go and NBSP and newline runs become a space.

Code is untouched. A newline run in ordinary text is what a browser collapses to one
space; left alone, a blank line inside a list item becomes a paragraph the converter
indents, and an indented paragraph is an indented code block.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml import html

_ZERO_WIDTH = re.compile("[\u200b‌‍⁠﻿]")
_NEWLINE_RUN = re.compile(r"[ \t]*\n[ \t\n]*")


def _inside_pre(element: html.HtmlElement) -> bool:
    return any(a.tag == "pre" for a in element.iterancestors()) or element.tag == "pre"


def transform(content: html.HtmlElement) -> None:
    """Apply to every text and tail node."""
    for element in content.iter():
        if not isinstance(element.tag, str):
            continue
        in_pre = _inside_pre(element)
        if element.text:
            element.text = _clean(element.text, in_pre=in_pre)
        if element.tail:
            parent = element.getparent()
            element.tail = _clean(element.tail, in_pre=parent is not None and _inside_pre(parent))


def _clean(text: str, *, in_pre: bool) -> str:
    if not in_pre:
        text = _ZERO_WIDTH.sub("", text)
        text = text.replace("\u00a0", " ")
        if text.strip():
            # Only text with words: the whitespace between block tags stays, so an
            # HTML island keeps its line structure when it is serialized later.
            text = _NEWLINE_RUN.sub(" ", text)
    return text
