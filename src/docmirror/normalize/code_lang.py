"""Fence info strings from the source's language markers, with alias normalization."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from lxml import html

if TYPE_CHECKING:
    from docmirror.config.models import Profile

ALIASES = {
    "cs": "csharp",
    "c#": "csharp",
    "js": "javascript",
    "ts": "typescript",
    "sh": "bash",
    "shell": "bash",
    "console": "bash",
    "zsh": "bash",
    "ps": "powershell",
    "ps1": "powershell",
    "pwsh": "powershell",
    "azurepowershell": "powershell",
    "azurecli": "bash",
    "yml": "yaml",
    "py": "python",
    "rb": "ruby",
    "objc": "objectivec",
    "kt": "kotlin",
    "plaintext": "text",
    "txt": "text",
    "none": "text",
    "http-request": "http",
    "httprequest": "http",
    "msgraph-interactive": "http",
    "hcl": "terraform",
    "bash session": "bash",
    "terminal": "bash",
    "shell session": "bash",
    "text/html": "html",
    "proto": "protobuf",
    "msgraph": "http",
}
_HTTP_START = re.compile(
    r"^\s*((GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+\S+|HTTP/\d(\.\d)?\s+\d{3})", re.IGNORECASE
)
_LINE_NUMBER_CLASSES = ("line-number", "linenos", "lineno", "line-numbers", "hljs-ln-numbers")


def normalize_alias(language: str) -> str:
    """The canonical info string for a language marker.

    >>> normalize_alias("cs"), normalize_alias("Lang-JS"), normalize_alias("HTTP")
    ('csharp', 'javascript', 'http')
    """
    text = language.strip().lower()
    for prefix in ("lang-", "language-"):
        text = text.removeprefix(prefix)
    return ALIASES.get(text, text)


def _language_from(element: html.HtmlElement, attrs: list[str]) -> str:
    for spec in attrs:
        if spec.startswith("class:"):
            prefix = spec[len("class:") :]
            for cls in (element.get("class") or "").split():
                if cls.lower().startswith(prefix):
                    return normalize_alias(cls[len(prefix) :])
        else:
            value = element.get(spec)
            if value:
                return normalize_alias(value)
    return ""


def detect_language(pre: html.HtmlElement, attrs: list[str]) -> str:
    """The language of a `<pre>` from itself, its `<code>`, its ancestors or its content."""
    hint = pre.get("data-docmirror-tab-lang")
    if hint:
        return normalize_alias(hint)
    code = pre.find("code")
    if code is not None and "devsite-terminal" in (code.get("class") or "").split():
        return "bash"
    for candidate in [code, pre] if code is not None else [pre]:
        language = _language_from(candidate, attrs)
        if language:
            return language
    for ancestor in pre.iterancestors():
        if ancestor.tag in {"devsite-code", "div", "section", "figure"}:
            language = _language_from(ancestor, attrs)
            if language:
                return language
            hint = ancestor.get("data-docmirror-tab-lang")
            if hint:
                return normalize_alias(hint)
        if ancestor.tag in {"article", "main", "body"}:
            break
    if _HTTP_START.match(pre.text_content() or ""):
        return "http"
    return ""


def _unwrap_links(pre: html.HtmlElement) -> None:
    """A fence cannot carry a link, so anchors inside code become their text."""
    for anchor in list(pre.iter("a")):
        anchor.drop_tag()


def _strip_gutters(pre: html.HtmlElement) -> None:
    doomed = [
        node
        for node in pre.iter()
        if isinstance(node.tag, str)
        and any(cls in _LINE_NUMBER_CLASSES for cls in (node.get("class") or "").split())
    ]
    for node in doomed:
        if node.getparent() is not None:
            node.drop_tree()


def normalize_code_blocks(
    content: html.HtmlElement, profile: Profile, counts: dict[str, int]
) -> None:
    """Put the detected language on each `<pre><code>` as `class="language-X"`."""
    tagged = 0
    total = 0
    for pre in list(content.iter("pre")):
        total += 1
        _strip_gutters(pre)
        _unwrap_links(pre)
        language = detect_language(pre, profile.code_lang_attrs)
        code = pre.find("code")
        if code is None:
            code = html.Element("code")
            code.text = pre.text or ""
            for child in list(pre):
                code.append(child)
            pre.text = None
            pre.append(code)
        for node in (pre, code):
            classes = [
                c
                for c in (node.get("class") or "").split()
                if not c.lower().startswith(("lang-", "language-"))
            ]
            if node is code and language:
                classes.append(f"language-{language}")
            if classes:
                node.set("class", " ".join(classes))
            elif "class" in node.attrib:
                del node.attrib["class"]
        if language:
            tagged += 1
    counts["code_blocks"] = total
    counts["code_blocks_tagged"] = tagged
