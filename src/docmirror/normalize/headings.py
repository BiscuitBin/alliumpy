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


def _named_anchors(content: html.HtmlElement, anchors: list[str], islands: Islands) -> None:
    """Keep the id of an `<a name>`/`<a id>` without href: a javadoc-style anchor.

    The anchor directly before an id-less heading lends it its id; any other travels
    as an empty `<a id>` island, since every converter drops a link without href.
    """
    for anchor in list(content.iter("a")):
        if anchor.get("href"):
            continue
        identifier = anchor.get("id") or anchor.get("name")
        if not identifier:
            continue
        anchors.append(identifier)
        following = anchor.getnext()
        if (
            following is not None
            and following.tag in HEADINGS
            and not following.get("id")
            and not anchor.text_content().strip()
        ):
            following.set("id", identifier)
            anchor.drop_tree()
            continue
        anchor.tag = "span"
        for name in list(anchor.attrib):
            del anchor.attrib[name]
        anchor.text = islands.register(f'<a id="{identifier}"></a>') + (anchor.text or "")


INLINE = frozenset({"span", "code", "a", "strong", "em", "b", "i", "kbd", "mark", "sub", "sup"})
ANCHORED_BLOCKS = frozenset({"blockquote", "figure"})


def _block_anchors(content: html.HtmlElement, anchors: list[str], islands: Islands) -> None:
    """An id on an element Markdown converts away travels as an empty `<a id>` before it.

    Every alert and figure keeps its id; any other element keeps it only when a link
    on the same page points at it, so a reference page with an id on every row does
    not fill with anchors nobody targets.
    """
    # Links were made absolute before this pass, so any fragment on any link counts:
    # only an element on this page with that id gains an anchor.
    targets = {
        a.get("href", "").rsplit("#", 1)[1] for a in content.iter("a") if "#" in a.get("href", "")
    }
    for element in list(content.iter()):
        tag = element.tag
        if not isinstance(tag, str) or tag in HEADINGS or tag == "a":
            continue
        identifier = element.get("id")
        if not identifier or (tag not in ANCHORED_BLOCKS and identifier not in targets):
            continue
        anchors.append(identifier)
        token = islands.register(f'<a id="{identifier}"></a>')
        if tag in INLINE:
            element.text = token + (element.text or "")
            continue
        holder = html.Element("p")
        holder.text = token
        element.addprevious(holder)


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
    _named_anchors(content, anchors, islands)
    _block_anchors(content, anchors, islands)
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
        # The suffix travels as an island so a converter never escapes its underscores.
        suffix = " " + islands.register(f"{{#{identifier}}}")
        if len(heading):
            last = heading[-1]
            last.tail = (last.tail or "") + suffix
        else:
            heading.text = (heading.text or "") + suffix
