"""Interactive explorers, embedded frames and videos become a one-line placeholder."""

from __future__ import annotations

from typing import TYPE_CHECKING

from lxml import etree, html

from docmirror.extract.extractor import select

if TYPE_CHECKING:
    from docmirror.config.models import Profile

EMBED_TAGS = ("iframe", "video", "embed", "object", "audio")


def transform(
    content: html.HtmlElement, profile: Profile, flags: set[str], counts: dict[str, int]
) -> None:
    """Replace each interactive element with `> [!NOTE] Interactive content omitted: ...`."""
    targets: list[html.HtmlElement] = list(content.iter(*EMBED_TAGS))
    for expression in profile.interactive_selectors:
        targets.extend(select(content, expression))
    done: set[int] = set()
    for element in targets:
        if id(element) in done or element.getparent() is None:
            continue
        if any(id(a) in done for a in element.iterancestors()):
            continue
        done.add(id(element))
        label = (
            element.get("src")
            or element.get("data-src")
            or element.get("href")
            or element.get("title")
            or element.get("aria-label")
            or element.tag
        )
        source = element.find(".//source")
        if source is not None and source.get("src"):
            label = source.get("src") or label
        quote = html.Element("blockquote")
        paragraph = etree.SubElement(quote, "p")
        paragraph.text = f"[!NOTE] Interactive content omitted: {label}"
        quote.tail = element.tail
        element.getparent().replace(element, quote)
        flags.add("interactive_omitted")
        counts["interactive_omitted"] = counts.get("interactive_omitted", 0) + 1
