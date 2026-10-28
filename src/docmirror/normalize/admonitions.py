"""Callouts become GFM alerts: NOTE, TIP, IMPORTANT, WARNING or CAUTION blockquotes."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from lxml import etree, html

from docmirror.extract.extractor import select

if TYPE_CHECKING:
    from docmirror.config.models import AdmonitionSpec, Profile

KINDS = {
    "note": "NOTE",
    "info": "NOTE",
    "tip": "TIP",
    "hint": "TIP",
    "key-point": "TIP",
    "keypoint": "TIP",
    "important": "IMPORTANT",
    "special": "IMPORTANT",
    "objective": "IMPORTANT",
    "warning": "WARNING",
    "warn": "WARNING",
    "caution": "CAUTION",
    "danger": "CAUTION",
    "error": "CAUTION",
    "deprecated": "WARNING",
    "beta": "NOTE",
    "experimental": "NOTE",
    "success": "TIP",
    "key-term": "NOTE",
    "dogfood": "NOTE",
}
_TRAILING_COLON = re.compile(r"\s*:\s*$")


def _kind_from_class(element: html.HtmlElement) -> tuple[str, str]:
    for cls in (element.get("class") or "").split():
        lowered = cls.lower()
        if lowered in KINDS:
            return KINDS[lowered], cls
        for key, kind in KINDS.items():
            if lowered in {
                f"alert-{key}",
                f"admonition-{key}",
                f"is-{key}",
                f"callout-{key}",
                f"{key}-box",
            }:
                return kind, key
    return "", ""


def _kind_from_text(text: str) -> str:
    return KINDS.get(_TRAILING_COLON.sub("", text).strip().lower(), "")


def _title_element(element: html.HtmlElement, spec: AdmonitionSpec) -> html.HtmlElement | None:
    if not spec.title:
        return None
    for candidate in select(element, spec.title):
        parent = candidate.getparent()
        if parent is element or (
            parent is not None and parent.getparent() is element and parent.tag == "p"
        ):
            return candidate
        if parent is not None and parent is element:
            return candidate
    return None


def convert_one(element: html.HtmlElement, spec: AdmonitionSpec, counts: dict[str, int]) -> None:
    """Rewrite one callout in place as a blockquote whose first paragraph is `[!KIND]`."""
    title = _title_element(element, spec)
    title_text = " ".join(title.text_content().split()) if title is not None else ""
    kind, label = ("", "")
    if spec.kind_from == "class" or not title_text:
        kind, label = _kind_from_class(element)
    if not kind and title_text:
        kind = _kind_from_text(title_text)
    if not kind and spec.kind_from == "tag":
        kind = KINDS.get(element.tag, "")
    original = _TRAILING_COLON.sub("", title_text) or label
    if not kind:
        kind = "NOTE"
    if title is not None:
        # drop_tree joins the title's tail onto the parent's text, so nothing is lost.
        parent = title.getparent()
        title.drop_tree()
        if (
            parent is not None
            and parent is not element
            and parent.tag == "p"
            and not parent.text_content().strip()
        ):
            parent.drop_tree()
    quote = html.Element("blockquote")
    marker = etree.SubElement(quote, "p")
    marker.text = f"[!{kind}]"
    known = {kind.lower(), label.lower(), *(k for k, v in KINDS.items() if v == kind)}
    keep_label = bool(original) and original.strip().lower() not in known
    if keep_label:
        strong_p = etree.SubElement(quote, "p")
        strong = etree.SubElement(strong_p, "strong")
        strong.text = original.strip()
    body = etree.SubElement(quote, "div")
    body.text = element.text
    for child in list(element):
        body.append(child)
    quote.tail = element.tail
    parent = element.getparent()
    if parent is not None:
        parent.replace(element, quote)
    counts["admonitions"] = counts.get("admonitions", 0) + 1


def transform(content: html.HtmlElement, profile: Profile, counts: dict[str, int]) -> None:
    """Convert every callout the profile describes, innermost first."""
    for spec in profile.admonitions:
        found = select(content, spec.selector)
        for element in reversed(found):
            if element.getparent() is not None:
                convert_one(element, spec, counts)
