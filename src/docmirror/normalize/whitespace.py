"""Zero-width characters go; NBSP becomes a space outside `<pre>`; code is untouched."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml import html

_ZERO_WIDTH = re.compile("[\u200b‌‍⁠﻿]")


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
    text = _ZERO_WIDTH.sub("", text)
    if not in_pre:
        text = text.replace("\u00a0", " ")
    return text
