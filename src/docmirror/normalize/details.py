"""`<details>`/`<summary>` stay HTML with the inner content converted to Markdown."""

from __future__ import annotations

from typing import TYPE_CHECKING

from lxml import etree

if TYPE_CHECKING:
    from collections.abc import Callable

    from lxml import html

    from docmirror.normalize.islands import Islands


def transform(content: html.HtmlElement, islands: Islands, convert: Callable[[str], str]) -> None:
    """Replace each details element with an island carrying converted inner Markdown."""
    for details in list(content.iter("details")):
        if details.getparent() is None:
            continue
        summary = details.find("summary")
        summary_text = (
            " ".join(summary.text_content().split()) if summary is not None else "Details"
        )
        if summary is not None:
            details.remove(summary)
        inner_html = (details.text or "") + "".join(
            etree.tostring(child, encoding="unicode", method="html") for child in details
        )
        inner = islands.restore(convert(inner_html)).strip()
        open_attr = " open" if details.get("open") is not None else ""
        raw = f"<details{open_attr}>\n<summary>{summary_text}</summary>\n\n{inner}\n\n</details>"
        islands.replace_element(details, raw)
