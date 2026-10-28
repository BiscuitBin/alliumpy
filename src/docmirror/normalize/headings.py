"""Preserve heading ids and guarantee a single H1."""

from __future__ import annotations

from typing import TYPE_CHECKING

from lxml import html

if TYPE_CHECKING:
    from docmirror.config.models import Profile
    from docmirror.normalize.islands import Islands

HEADINGS = ("h1", "h2", "h3", "h4", "h5", "h6")


def _lift_container_ids(content: html.HtmlElement) -> None:
    """A section or div whose first child is an id-less heading lends it its own id.

    Fragment links to `<section id="x"><h3>` are common; the section itself leaves no
    trace in Markdown, so the heading carries the anchor instead.
    """
    for container in content.iter("section", "div", "article"):
        identifier = container.get("id")
        if not identifier:
            continue
        first = next((c for c in container if isinstance(c.tag, str)), None)
        if first is not None and first.tag in HEADINGS and not first.get("id"):
            first.set("id", identifier)


def normalize_headings(
    content: html.HtmlElement,
    profile: Profile,
    anchors: list[str],
    counts: dict[str, int],
    islands: Islands,
    *,
    title: str = "",
) -> None:
    """Emit `{#id}` (attr style) or an `<a id>` before (inline style); demote to keep one H1."""
    _lift_container_ids(content)
    headings = list(content.iter(*HEADINGS))
    h1s = [h for h in headings if h.tag == "h1"]
    if not h1s and title:
        first = html.Element("h1")
        first.text = title
        content.insert(0, first)
        headings.insert(0, first)
        h1s = [first]
        counts["headings_added"] = 1
    if len(h1s) > 1:
        first = h1s[0]
        for heading in headings:
            if heading is first:
                continue
            level = int(heading.tag[1])
            heading.tag = f"h{min(level + 1, 6)}"
    for heading in headings:
        identifier = heading.get("id")
        if not identifier:
            continue
        anchors.append(identifier)
        if profile.heading_anchor_style == "inline":
            # An empty anchor is dropped by every converter, so it travels as an island.
            holder = html.Element("p")
            holder.text = islands.register(f'<a id="{identifier}"></a>')
            heading.addprevious(holder)
            continue
        suffix = f" {{#{identifier}}}"
        if len(heading):
            last = heading[-1]
            last.tail = (last.tail or "") + suffix
        else:
            heading.text = (heading.text or "") + suffix
