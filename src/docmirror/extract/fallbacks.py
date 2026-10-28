"""The heuristic extractors behind the profile, each wrapped to own its `Any` boundary."""

from __future__ import annotations

from typing import Any, cast

import trafilatura
from readability import Document


def trafilatura_html(text: str, base_url: str) -> str | None:
    """Trafilatura's main content as an HTML fragment, or None."""
    result: Any = trafilatura.extract(
        text,
        url=base_url,
        output_format="html",
        include_tables=True,
        include_links=True,
        include_images=True,
        include_formatting=True,
        include_comments=False,
    )
    return cast("str | None", result) or None


def readability_html(text: str, base_url: str) -> str | None:
    """readability-lxml's summary as an HTML fragment, or None."""
    try:
        document: Any = Document(text, url=base_url)
        summary = document.summary(html_partial=True)
    except Exception:  # noqa: BLE001 - any readability failure means "no content"
        return None
    return cast("str | None", summary) or None
