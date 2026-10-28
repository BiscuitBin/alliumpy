"""Sitemap streaming, child ranking, llms.txt links and page links."""

from __future__ import annotations

from docmirror.extract.extractor import parse_html
from docmirror.frontier.discovery import (
    canonical_of,
    page_links,
    parse_llms_txt,
    parse_sitemap,
    rank_child_sitemaps,
)

NS = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'


def test_parse_sitemap_and_index() -> None:
    urlset = f"<urlset {NS}><url><loc> https://h/a </loc><lastmod>2026-01-02</lastmod></url><url><loc>https://h/b</loc></url></urlset>"
    entries = list(parse_sitemap(urlset.encode()))
    assert [(e.loc, e.lastmod, e.is_index) for e in entries] == [
        ("https://h/a", "2026-01-02", False),
        ("https://h/b", None, False),
    ]
    index = f"<sitemapindex {NS}><sitemap><loc>https://h/s1.xml</loc></sitemap></sitemapindex>"
    assert [(e.loc, e.is_index) for e in parse_sitemap(index.encode())] == [
        ("https://h/s1.xml", True)
    ]
    assert list(parse_sitemap(b"<not xml")) == []


def test_rank_child_sitemaps() -> None:
    children = [
        "https://h/_s/graph_fr-fr_1.xml",
        "https://h/_s/dotnet_en-us_1.xml",
        "https://h/_s/graph_en-us_1.xml",
        "https://h/sitemap_1_of_2.xml",
    ]
    assert rank_child_sitemaps(children, ("/en-us/graph/",), "en-us") == [
        "https://h/_s/graph_en-us_1.xml",
        "https://h/_s/dotnet_en-us_1.xml",
        "https://h/sitemap_1_of_2.xml",
    ]
    assert rank_child_sitemaps(children, ("/workspace/",), "") == children


def test_parse_llms_txt() -> None:
    text = (
        "# Site\n\n> summary\n\n- [A](/docs/a.md): first\n"
        '- [B](https://h/b "t")\n- [A again](/docs/a.md)'
    )
    assert parse_llms_txt(text, "https://h/") == ["https://h/docs/a.md", "https://h/b"]


def test_page_links_and_canonical() -> None:
    markup = (
        '<html><head><link rel="canonical" href="/c"><link rel="next" href="/n"></head>'
        '<body><a href="/a#x">a</a><a href="javascript:void(0)">j</a>'
        '<a href="mailto:x@y">m</a></body></html>'
    )
    document = parse_html(markup, "https://h/base/")
    links = page_links(document, "https://h/base/")
    assert [(link.url, link.kind) for link in links] == [
        ("https://h/c", "canonical"),
        ("https://h/n", "next"),
        ("https://h/a#x", "a"),
    ]
    assert canonical_of(document, "https://h/base/") == "https://h/c"
