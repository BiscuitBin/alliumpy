"""Select the main content of a fetched page and capture its metadata.

The profile's `main_selector` list wins when any entry matches; otherwise Trafilatura,
then readability-lxml. The chosen subtree is stripped of the profile's `strip_selectors`
and of scripts, styles, noscript, iframes, tiny icon SVGs and hidden-by-attribute
elements, and nothing else: no heuristic strips content.
"""

from __future__ import annotations

import copy
import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

from lxml import etree, html
from lxml.cssselect import CSSSelector

if TYPE_CHECKING:
    from docmirror.config.models import Profile

LOG = logging.getLogger("docmirror.extract")
ICON_SVG_MAX_BYTES = 2048
SHELL_TEXT_MAX = 50
SHELL_BODY_TEXT_MAX = 200
_DISPLAY_NONE = re.compile(r"display\s*:\s*none", re.IGNORECASE)
_NEEDS_JS = re.compile(r"enable\s+javascript|javascript\s+is\s+(required|disabled)", re.IGNORECASE)
_SELECTOR_CACHE: dict[str, CSSSelector] = {}


def selector(expression: str) -> CSSSelector:
    """A compiled CSS selector, cached."""
    compiled = _SELECTOR_CACHE.get(expression)
    if compiled is None:
        compiled = CSSSelector(expression, translator="html")
        _SELECTOR_CACHE[expression] = compiled
    return compiled


def select(root: html.HtmlElement, expression: str) -> list[html.HtmlElement]:
    """Elements under `root` matching a CSS selector list; an invalid selector matches nothing."""
    if not expression.strip():
        return []
    try:
        found: Any = selector(expression)(root)
    except (etree.XPathError, ValueError, TypeError) as error:
        LOG.warning("bad selector %r: %s", expression, error)
        return []
    if not isinstance(found, list):
        return []
    return [item for item in found if isinstance(item, html.HtmlElement)]


def parse_html(text: str, base_url: str) -> html.HtmlElement:
    """Parse an HTML document, with `base_url` as its base."""
    parser = html.HTMLParser(encoding=None, remove_comments=True, remove_pis=True)
    return html.document_fromstring(text or "<html></html>", parser=parser, base_url=base_url)


@dataclass(slots=True)
class PageMetadata:
    """What is captured outside the main content."""

    title: str = ""
    description: str = ""
    og_title: str = ""
    canonical_url: str | None = None
    lang: str = ""
    breadcrumbs: list[str] = field(default_factory=list)
    last_updated: str | None = None
    heading_ids: list[str] = field(default_factory=list)
    noscript_needs_js: bool = False
    spa_shell: bool = False


@dataclass(slots=True)
class Extraction:
    """The selected main content and how it was selected."""

    content: html.HtmlElement
    extractor: str
    metadata: PageMetadata
    text_chars: int


def _text_len(element: html.HtmlElement) -> int:
    return len(" ".join(element.text_content().split()))


def _capture_metadata(document: html.HtmlElement, base_url: str, profile: Profile) -> PageMetadata:
    meta = PageMetadata()
    title = document.find(".//title")
    meta.title = " ".join(title.text_content().split()) if title is not None else ""
    _meta_tags(document, base_url, meta)
    _profile_metadata(document, profile, meta)
    _shell_signals(document, meta)
    return meta


def _meta_tags(document: html.HtmlElement, base_url: str, meta: PageMetadata) -> None:
    for element in document.iter("meta"):
        name = (element.get("name") or element.get("property") or "").lower()
        content = (element.get("content") or "").strip()
        if name == "description" and content:
            meta.description = content
        elif name == "og:title" and content:
            meta.og_title = content
        elif name in {"last_updated", "last-updated", "article:modified_time"} and content:
            meta.last_updated = content
    for element in document.iter("link"):
        rel = (element.get("rel") or "").lower().split()
        if "canonical" in rel and element.get("href"):
            meta.canonical_url = urljoin(base_url, element.get("href"))
    root = document.getroottree().getroot()
    meta.lang = (root.get("lang") or "").strip() if root is not None else ""


def _profile_metadata(document: html.HtmlElement, profile: Profile, meta: PageMetadata) -> None:
    if profile.breadcrumb_selector:
        for crumb_root in select(document, profile.breadcrumb_selector)[:1]:
            items = [" ".join(li.text_content().split()) for li in crumb_root.iter("li")]
            if not items:
                items = [" ".join(a.text_content().split()) for a in crumb_root.iter("a")]
            meta.breadcrumbs = [item for item in items if item]
    if meta.last_updated is None and profile.last_updated_selector:
        for element in select(document, profile.last_updated_selector)[:1]:
            value = element.get("datetime") or " ".join(element.text_content().split())
            meta.last_updated = value or None


def _shell_signals(document: html.HtmlElement, meta: PageMetadata) -> None:
    for element in document.iter("noscript"):
        if re.search(
            r"enable\s+javascript|javascript\s+is\s+(required|disabled)",
            element.text_content(),
            re.IGNORECASE,
        ):
            meta.noscript_needs_js = True
    body = document.find("body")
    if body is not None:
        children = [
            c
            for c in body
            if isinstance(c.tag, str) and c.tag not in {"script", "noscript", "style", "link"}
        ]
        shell_ids = {"root", "app", "__next", "___gatsby", "__nuxt", "q-app"}
        only_shell = (
            len(children) == 1
            and children[0].tag == "div"
            and children[0].get("id") in shell_ids
            and _text_len(children[0]) < SHELL_TEXT_MAX
        )
        next_data = document.find(".//script[@id='__NEXT_DATA__']") is not None
        if only_shell or (next_data and _text_len(body) < SHELL_BODY_TEXT_MAX):
            meta.spa_shell = True


def _strip(content: html.HtmlElement, profile: Profile) -> None:
    doomed: list[html.HtmlElement] = []
    for expression in profile.strip_selectors:
        doomed.extend(select(content, expression))
    for element in content.iter():
        if not isinstance(element.tag, str):
            continue
        tag = element.tag
        if (
            tag in {"style", "noscript", "template"}
            # A MathJax `math/tex` script is the formula itself; the math normalizer reads it.
            or (tag == "script" and not (element.get("type") or "").startswith("math/tex"))
            or (tag == "svg" and len(etree.tostring(element)) < ICON_SVG_MAX_BYTES)
            # `hidden` marks chrome, except on a tab-panel section, which tabs expand.
            or (element.get("hidden") is not None and tag != "section")
            or (element.get("aria-hidden") == "true" and not element.text_content().strip())
            or (
                _DISPLAY_NONE.search(element.get("style") or "")
                and tag
                not in {
                    "section",
                    "div",
                    "pre",
                    "code",
                }
            )
        ):
            doomed.append(element)
    for element in doomed:
        if element is content or element.getparent() is None:
            continue
        element.drop_tree()


def _without_noscript(document: html.HtmlElement) -> str:
    """The document serialized without `<noscript>`, so a fallback never extracts its text."""
    clone = copy.deepcopy(document)
    for element in list(clone.iter("noscript", "script", "style")):
        if element.getparent() is not None:
            element.drop_tree()
    return etree.tostring(clone, encoding="unicode", method="html")


def _profile_content(document: html.HtmlElement, profile: Profile) -> html.HtmlElement | None:
    for expression in profile.main_selector:
        matches = select(document, expression)
        if matches:
            return matches[0]
    return None


def _trafilatura_content(text: str, base_url: str) -> html.HtmlElement | None:
    try:
        from docmirror.extract.fallbacks import trafilatura_html  # noqa: PLC0415 - optional, slow import
    except ImportError:  # pragma: no cover - the dependency is required
        return None
    fragment = trafilatura_html(text, base_url)
    if not fragment:
        return None
    return html.fragment_fromstring(fragment, create_parent="div", base_url=base_url)


def _readability_content(text: str, base_url: str) -> html.HtmlElement | None:
    try:
        from docmirror.extract.fallbacks import readability_html  # noqa: PLC0415 - optional, slow import
    except ImportError:  # pragma: no cover - the dependency is required
        return None
    fragment = readability_html(text, base_url)
    if not fragment:
        return None
    return html.fragment_fromstring(fragment, create_parent="div", base_url=base_url)


def extract_page(
    text: str,
    base_url: str,
    profile: Profile,
    *,
    fallbacks: tuple[str, ...] = ("trafilatura", "readability"),
) -> Extraction:
    """Select, strip and describe the main content of a page."""
    document = parse_html(text, base_url)
    metadata = _capture_metadata(document, base_url, profile)
    content = _profile_content(document, profile)
    used = "profile"
    if content is not None:
        content = copy.deepcopy(content)
    else:
        for name in fallbacks:
            content = (
                _trafilatura_content(text, base_url)
                if name == "trafilatura"
                else _readability_content(text, base_url)
            )
            if content is not None and _text_len(content) > 0:
                used = name
                break
            content = None
    if content is None:
        body = document.find("body")
        content = copy.deepcopy(body) if body is not None else html.Element("div")
        used = "body"
    _strip(content, profile)
    content.make_links_absolute(base_url, resolve_base_href=True)
    # A fallback extractor builds a fresh tree with no base; the normalizers read it to
    # tell a link to this page from a link elsewhere.
    content.getroottree().docinfo.URL = base_url
    metadata.heading_ids = [
        element.get("id") or ""
        for element in content.iter("h1", "h2", "h3", "h4", "h5", "h6")
        if element.get("id")
    ]
    if not metadata.title:
        first = next(iter(content.iter("h1")), None)
        metadata.title = " ".join(first.text_content().split()) if first is not None else base_url
    return Extraction(
        content=content, extractor=used, metadata=metadata, text_chars=_text_len(content)
    )
