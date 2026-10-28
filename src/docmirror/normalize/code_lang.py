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
    return guess_language(pre.text_content() or "")


_SHELL_START = re.compile(
    r"^\s*(\$ |sudo |gem |pip3? |npm |npx |yarn |apt(-get)? |brew |gcloud |curl |wget |git |"
    r"python3? |easy_install |dotnet |mvn |gradle |go (get|run|install) |cargo |composer |pwsh |"
    r"node |ruby |php |java |javac |docker |kubectl |make |mkdir |cd |ls |cat |echo |export |\./)",
    re.IGNORECASE,
)
_JSON_START = re.compile(r'^\s*[\[{]\s*(?:"[^"]*"\s*:|[\[{]|\])')
_MARKUP_START = re.compile(r"^\s*<(?:[a-zA-Z][\w:-]*|!DOCTYPE|\?xml)")
_HTML_TAGS = re.compile(r"<(?:html|head|body|div|span|p|a|script|link|meta|img|br|table|ul|li)\b")
# Each guess is a regex over the first lines and the language it names, most specific first.
_SIGNATURES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"^\s*using [\w.]+;|^\s*namespace [\w.]+", re.MULTILINE), "csharp"),
    (
        re.compile(
            r"^\s*(?:import|package) [\w.]+(?:\.\*)?;|@\w+\s+public |"
            r"public (?:static |final |abstract )*"
            r"(?:class|interface|void|\w+(?:<[^>]*>)?) \w+\s*\(?",
            re.MULTILINE,
        ),
        "java",
    ),
    (
        re.compile(
            r"@(?:interface|implementation|end)\b|UIColor\s*\*|^\s*[-+]\s*\([\w* ]+\)\s*\w+",
            re.MULTILINE,
        ),
        "objectivec",
    ),
    (
        re.compile(
            r"^\s*(?:var|const|let|function|async function)\s+\w+|=>\s*\{|console\.log\(",
            re.MULTILINE,
        ),
        "javascript",
    ),
    (
        re.compile(r"^\s*(?:def \w+\(|from \w[\w.]* import |import \w+$|print\()", re.MULTILINE),
        "python",
    ),
    (re.compile(r"^\s*(?:func \w+\(|package main$)", re.MULTILINE), "go"),
    (re.compile(r"^\s*<\?php|^\s*\$\w+\s*=\s*new ", re.MULTILINE), "php"),
)
_CODE_CHARS = re.compile(r"[;{}<>()=\[\]]")
_TEXT_LINE = re.compile(r"^(?:https?://\S+|[\w .,:'!?/%&+#@|-]*)$")
_HEAD_LINES = 6


def guess_language(text: str) -> str:
    r"""A language from the code itself, or `text` for a block that is not code at all.

    >>> guess_language("GET /me HTTP/1.1"), guess_language("$ pip install x")
    ('http', 'bash')
    >>> guess_language('{"a": 1}'), guess_language('{\n  "kind": "x",\n  ...\n}')
    ('json', 'json')
    >>> guess_language('<entry xmlns="http://www.w3.org/2005/Atom">')
    'xml'
    >>> guess_language("<div>x</div>"), guess_language("var f = function(x) {}")
    ('html', 'javascript')
    >>> guess_language("import com.google.type.Color;\n// ...")
    'java'
    >>> guess_language("Snippet not available"), guess_language("https://sites.google.com/")
    ('text', 'text')
    >>> guess_language("+---+\n| a |\n+---+"), guess_language("x = f(1)")
    ('text', '')
    """
    if _HTTP_START.match(text):
        return "http"
    if _SHELL_START.match(text):
        return "bash"
    stripped = text.strip()
    if _JSON_START.match(stripped):
        return "json"
    if _MARKUP_START.match(stripped):
        return "html" if _HTML_TAGS.search(stripped[:400]) else "xml"
    head = "\n".join(stripped.splitlines()[:_HEAD_LINES])
    for pattern, language in _SIGNATURES:
        if pattern.search(head):
            return language
    lines = [line for line in stripped.splitlines() if line.strip()]
    if lines and not _CODE_CHARS.search(stripped) and all(_TEXT_LINE.match(line) for line in lines):
        # Prose, bare URLs, identifiers and box drawings are text, and say so.
        return "text"
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
