"""The ordered list of DOM transforms; each module exports one `transform` function."""

from __future__ import annotations

from typing import TYPE_CHECKING

from docmirror.normalize import (
    admonitions,
    custom_elements,
    definition_lists,
    details,
    footnotes,
    images,
    interactive,
    math,
    tables,
    tabs,
    whitespace,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from lxml import html

    from docmirror.config.models import Profile
    from docmirror.normalize.islands import Islands

HEADINGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})


def run_all(
    content: html.HtmlElement,
    profile: Profile,
    islands: Islands,
    flags: set[str],
    counts: dict[str, int],
    convert: Callable[[str], str],
) -> list[str]:
    """Run the transforms in order and return the non-heading anchors found."""
    whitespace.transform(content)
    interactive.transform(content, profile, flags, counts)
    tabs.transform(content, profile, counts)
    admonitions.transform(content, profile, counts)
    custom_elements.transform(content)
    math.transform(content, islands)
    footnotes.transform(content, islands, convert)
    details.transform(content, islands, convert)
    images.transform(content, counts)
    definition_lists.transform(content, islands)
    tables.transform(content, islands, flags, counts)
    return [
        str(element.get("id"))
        for element in content.iter()
        if isinstance(element.tag, str) and element.get("id") and element.tag not in HEADINGS
    ]
