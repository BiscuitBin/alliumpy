"""Expand every tab panel, in source order; never emit only the active tab.

Languages as labels with one code block per panel become a bold label line and a
tagged fence; anything else becomes a heading one level below the enclosing heading,
followed by the panel body.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from lxml import etree, html

from docmirror.extract.extractor import select
from docmirror.normalize.code_lang import normalize_alias

if TYPE_CHECKING:
    from docmirror.config.models import Profile, TabSpec

HEADINGS = ("h1", "h2", "h3", "h4", "h5", "h6")
LANGUAGE_LABELS = {
    "http",
    "csharp",
    "c#",
    "go",
    "java",
    "javascript",
    "js",
    "php",
    "powershell",
    "python",
    "typescript",
    "ts",
    "ruby",
    "node.js",
    "nodejs",
    "node",
    "kotlin",
    "swift",
    "objective-c",
    "dart",
    "rust",
    "bash",
    "shell",
    "curl",
    "cli",
    "sh",
    "json",
    "yaml",
    "xml",
    "graphql",
    "c++",
    "cpp",
    "c",
    "scala",
    "r",
    "sql",
    "terraform",
    "apps script",
    "google apps script",
    "rest",
    "gapi",
    "gcloud",
    "console",
}


def _enclosing_level(element: html.HtmlElement) -> int:
    for previous in element.itersiblings(preceding=True):
        if previous.tag in HEADINGS:
            return int(previous.tag[1])
    for ancestor in element.iterancestors():
        for previous in ancestor.itersiblings(preceding=True):
            if previous.tag in HEADINGS:
                return int(previous.tag[1])
    return 2


def _text(element: html.HtmlElement) -> str:
    return " ".join(element.text_content().split())


def _panel_label(panel: html.HtmlElement, spec: TabSpec, labels: dict[str, str]) -> str:
    if spec.panel_key:
        key = panel.get(spec.panel_key) or ""
        if key in labels:
            return labels[key]
        key = key.removeprefix("#")
        if key in labels:
            return labels[key]
    if spec.panel_heading:
        for heading in select(panel, spec.panel_heading)[:1]:
            label = _text(heading)
            heading.drop_tree()
            return label
    for child in panel:
        if isinstance(child.tag, str) and child.tag in HEADINGS:
            label = _text(child)
            child.drop_tree()
            return label
    key = panel.get(spec.panel_key or "id") or ""
    return key or "Tab"


def _single_code_block(panel: html.HtmlElement) -> html.HtmlElement | None:
    blocks = list(panel.iter("pre"))
    if len(blocks) != 1:
        return None
    text_outside = _text(panel).replace(_text(blocks[0]), "", 1).strip()
    return blocks[0] if not text_outside else None


def expand_group(group: html.HtmlElement, spec: TabSpec, counts: dict[str, int]) -> None:
    """Replace one tab group with its expanded panels."""
    labels: dict[str, str] = {}
    label_elements = select(group, spec.label) if spec.label else []
    for element in label_elements:
        key = element.get(spec.label_key or "id") or element.get("href") or ""
        key = key.removeprefix("#")
        labels[key] = _text(element)
    panels = [p for p in select(group, spec.panel) if group in p.iterancestors()]
    if not panels:
        return
    counts["tab_panels"] = counts.get("tab_panels", 0) + len(panels)
    items = [(_panel_label(panel, spec, labels), panel) for panel in panels]
    code_only = all(_single_code_block(panel) is not None for _, panel in items)
    languages = all(
        normalize_alias(label) in LANGUAGE_LABELS or label.lower() in LANGUAGE_LABELS
        for label, _ in items
    )
    level = min(_enclosing_level(group) + 1, 6)
    replacement = html.Element("div")
    replacement.set("class", "docmirror-tabs")
    for label, panel in items:
        for name in ("hidden", "aria-hidden", "style"):
            if name in panel.attrib:
                del panel.attrib[name]
        if code_only and languages:
            language = normalize_alias(label)
            pre = _single_code_block(panel)
            if pre is not None and not _has_language(pre):
                pre.set("data-docmirror-tab-lang", language)
            caption = html.Element("p")
            strong = etree.SubElement(caption, "strong")
            strong.text = label
            replacement.append(caption)
        else:
            heading = html.Element(f"h{level}")
            heading.text = label
            replacement.append(heading)
        holder = html.Element("div")
        holder.text = panel.text
        for child in list(panel):
            holder.append(child)
        replacement.append(holder)
        counts["tab_panels_emitted"] = counts.get("tab_panels_emitted", 0) + 1
    replacement.tail = group.tail
    parent = group.getparent()
    if parent is not None:
        parent.replace(group, replacement)


def _has_language(pre: html.HtmlElement) -> bool:
    for node in (pre, *(c for c in pre if c.tag == "code")):
        for cls in (node.get("class") or "").split():
            if cls.lower().startswith(("lang-", "language-")):
                return True
        if node.get("data-lang") or node.get("data-language") or node.get("syntax"):
            return True
    return False


def transform(content: html.HtmlElement, profile: Profile, counts: dict[str, int]) -> None:
    """Expand every tab group the profile describes, innermost first."""
    for spec in profile.tabs:
        groups = select(content, spec.group)
        for group in reversed(groups):
            if group.getparent() is None:
                continue
            expand_group(group, spec, counts)
