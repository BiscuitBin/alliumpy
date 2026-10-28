"""Run every DOM transform in order and hand the backend a fragment plus the islands."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from lxml import etree

from docmirror.normalize.code_lang import normalize_code_blocks
from docmirror.normalize.headings import normalize_headings
from docmirror.normalize.islands import Islands

if TYPE_CHECKING:
    from collections.abc import Callable

    from lxml import html

    from docmirror.config.models import Profile


@dataclass(slots=True)
class NormalizeResult:
    """The fragment to convert and what the transforms observed."""

    fragment: str
    islands: Islands
    flags: set[str] = field(default_factory=set)
    counts: dict[str, int] = field(default_factory=dict)
    anchors: list[str] = field(default_factory=list)


def _count_tree(root: html.HtmlElement, totals: dict[str, int]) -> None:
    for element in root.iter():
        tag = element.tag
        if not isinstance(tag, str):
            continue
        if tag == "pre":
            totals["code_blocks"] += 1
        elif tag == "table":
            totals["tables"] += 1
        elif tag in {"td", "th"}:
            totals["table_cells"] += 1
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            totals["headings"] += 1
        elif tag == "a" and element.get("href"):
            totals["links"] += 1
        elif tag == "img":
            totals["images"] += 1
        elif tag == "li":
            totals["list_items"] += 1


def expected_counts(content: html.HtmlElement, islands: Islands) -> dict[str, int]:
    """What the Markdown must carry: the normalized tree plus every HTML island."""
    from lxml import html as lxml_html  # noqa: PLC0415

    totals = dict.fromkeys(
        ("code_blocks", "tables", "table_cells", "headings", "links", "images", "list_items"), 0
    )
    _count_tree(content, totals)
    for chunk in islands.chunks:
        if not chunk.lstrip().startswith("<"):
            continue
        try:
            root = lxml_html.fragment_fromstring(chunk, create_parent="div")
        except (ValueError, TypeError):
            continue
        _count_tree(root, totals)
    return totals


def normalize(
    content: html.HtmlElement,
    profile: Profile,
    *,
    title: str = "",
    convert: Callable[[str], str] | None = None,
) -> NormalizeResult:
    """Apply the transforms to `content` in place and serialize it.

    `convert` turns an HTML fragment into Markdown with the configured backend; the
    transforms that keep HTML islands with Markdown inside (details, footnotes) use it.
    """
    islands = Islands()
    flags: set[str] = set()
    counts: dict[str, int] = {}
    from docmirror.normalize.transforms import run_all  # noqa: PLC0415 - keeps the transform list in one module

    if convert is None:
        from docmirror.convert.backends import convert_html  # noqa: PLC0415

        def convert(fragment: str) -> str:
            return convert_html(fragment)

    anchors = run_all(content, profile, islands, flags, counts, convert)
    normalize_code_blocks(content, profile, counts)
    normalize_headings(content, profile, anchors, counts, islands, title=title)
    counts.update(expected_counts(content, islands))
    fragment = etree.tostring(content, encoding="unicode", method="html")
    return NormalizeResult(
        fragment=fragment, islands=islands, flags=flags, counts=counts, anchors=anchors
    )
