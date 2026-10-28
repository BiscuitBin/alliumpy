"""Main-content extraction: profile selectors, then Trafilatura, then readability."""

from __future__ import annotations

from docmirror.extract.extractor import Extraction, PageMetadata, extract_page, parse_html

__all__ = ["Extraction", "PageMetadata", "extract_page", "parse_html"]
