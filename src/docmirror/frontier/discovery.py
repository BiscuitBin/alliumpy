"""Seeds: sitemaps (streamed and scope-filtered), llms.txt links and in-page links."""

from __future__ import annotations

import re
from dataclasses import dataclass
from io import BytesIO
from typing import TYPE_CHECKING
from urllib.parse import urljoin

from lxml import etree, html

if TYPE_CHECKING:
    from collections.abc import Iterator

SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
_MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


@dataclass(frozen=True, slots=True)
class SitemapEntry:
    """One `<url>` or `<sitemap>` of a sitemap document."""

    loc: str
    lastmod: str | None
    is_index: bool


def parse_sitemap(body: bytes) -> Iterator[SitemapEntry]:
    """Stream the entries of a sitemap or sitemap index without building the whole tree.

    >>> doc = b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://h/a</loc><lastmod>2026-01-02</lastmod></url></urlset>'
    >>> [(e.loc, e.lastmod, e.is_index) for e in parse_sitemap(doc)]
    [('https://h/a', '2026-01-02', False)]
    """
    try:
        iterator = etree.iterparse(
            BytesIO(body),
            events=("end",),
            tag=(SITEMAP_NS + "url", SITEMAP_NS + "sitemap"),
            recover=True,
        )
        for _, element in iterator:
            loc = element.findtext(SITEMAP_NS + "loc")
            lastmod = element.findtext(SITEMAP_NS + "lastmod")
            if loc:
                yield SitemapEntry(
                    loc.strip(),
                    lastmod.strip() if lastmod else None,
                    element.tag.endswith("sitemap"),
                )
            element.clear()
    except etree.XMLSyntaxError:
        return


def parse_llms_txt(text: str, base_url: str) -> list[str]:
    r"""The absolute link targets of an `llms.txt` document, in order, deduplicated.

    >>> parse_llms_txt("# T\\n- [A](/docs/a.md): x\\n- [B](https://h/b)", "https://h/")
    ['https://h/docs/a.md', 'https://h/b']
    """
    seen: dict[str, None] = {}
    for match in _MD_LINK.finditer(text):
        seen.setdefault(urljoin(base_url, match.group(1)), None)
    return list(seen)


_LOCALE_TOKEN = re.compile(r"(?<![a-z])([a-z]{2}-[a-z]{2,4})(?![a-z])", re.IGNORECASE)


def rank_child_sitemaps(children: list[str], prefixes: tuple[str, ...], locale: str) -> list[str]:
    """Order child sitemaps by how likely they cover the scope, dropping other locales.

    A child whose URL carries a token of a path prefix (`graph` for `/en-us/graph/`) ranks
    first, then one carrying the pinned locale, then the rest; a child naming a different
    locale is dropped. Nothing here knows a site: the tokens come from the scope.

    >>> rank_child_sitemaps(
    ...     ["https://h/_s/graph_fr-fr_1.xml", "https://h/_s/dotnet_en-us_1.xml",
    ...      "https://h/_s/graph_en-us_1.xml", "https://h/s_1_of_2.xml"],
    ...     ("/en-us/graph/",), "en-us")
    ['https://h/_s/graph_en-us_1.xml', 'https://h/_s/dotnet_en-us_1.xml', 'https://h/s_1_of_2.xml']
    """
    pinned = locale.lower()
    tokens = {
        segment.lower()
        for prefix in prefixes
        for segment in prefix.split("/")
        if segment and not _LOCALE_TOKEN.fullmatch(segment)
    }
    ranked: list[tuple[int, int, str]] = []
    for index, child in enumerate(children):
        lowered = child.lower()
        locales = {m.lower() for m in _LOCALE_TOKEN.findall(lowered)}
        if pinned and locales and pinned not in locales:
            continue
        score = 0
        if any(token in lowered for token in tokens):
            score += 2
        if pinned and pinned in locales:
            score += 1
        ranked.append((-score, index, child))
    return [child for _, _, child in sorted(ranked)]


@dataclass(frozen=True, slots=True)
class PageLink:
    """One link found on a fetched page."""

    url: str
    kind: str


def page_links(document: html.HtmlElement, base_url: str) -> list[PageLink]:
    """`<a href>`, `<link rel=next>` and `<link rel=canonical>` targets, absolute."""
    links: list[PageLink] = []
    for element in document.iter("link"):
        rel = (element.get("rel") or "").lower().split()
        href = element.get("href")
        if href and ("next" in rel or "canonical" in rel):
            links.append(
                PageLink(urljoin(base_url, href), "next" if "next" in rel else "canonical")
            )
    for element in document.iter("a"):
        href = element.get("href")
        if not href or href.startswith(("javascript:", "mailto:", "tel:", "data:")):
            continue
        links.append(PageLink(urljoin(base_url, href), "a"))
    return links


def canonical_of(document: html.HtmlElement, base_url: str) -> str | None:
    """The `<link rel=canonical>` target, absolute, if present."""
    for element in document.iter("link"):
        rel = (element.get("rel") or "").lower().split()
        href = element.get("href")
        if href and "canonical" in rel:
            return urljoin(base_url, str(href))
    return None
