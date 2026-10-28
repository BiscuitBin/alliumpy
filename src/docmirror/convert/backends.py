"""The `html-to-markdown` backend and the `markdownify` fallback.

Both receive the same pre-normalized HTML and must pass the same golden set; the fidelity
work lives in `normalize/`, so a backend only has to carry what it is given.
"""

from __future__ import annotations

import re
from importlib.metadata import version
from typing import TYPE_CHECKING, Any

from html_to_markdown import ConversionOptions, convert

if TYPE_CHECKING:
    from docmirror.config.models import Backend

INLINE_HTML_TAGS = ["kbd", "sub", "sup", "mark"]
_SEMVER_MAJOR = re.compile(r"^(\d+)")


def _major(name: str) -> str:
    try:
        match = _SEMVER_MAJOR.match(version(name))
        return match.group(1) if match else "?"
    except Exception:  # noqa: BLE001 - metadata missing in odd installs
        return "?"


CONVERTER_NAMES: dict[str, str] = {
    "html-to-markdown": f"html-to-markdown/{_major('html-to-markdown')}.x",
    "markdownify": f"markdownify/{_major('markdownify')}.x",
}


def _html_to_markdown(fragment: str, bullet: str) -> str:
    options = ConversionOptions(
        heading_style="atx",
        bullets=bullet * 3,
        list_indent_width=2,
        code_block_style="backticks",
        escape_asterisks=True,
        escape_underscores=True,
        escape_misc=False,
        extract_metadata=False,
        wrap=False,
        whitespace_mode="normalized",
        preserve_tags=list(INLINE_HTML_TAGS),
        autolinks=False,
        hidden_content="all",
    )
    return str(convert(fragment, options).content)


class _Markdownify:
    def __init__(self) -> None:
        from markdownify import MarkdownConverter  # noqa: PLC0415 - optional backend

        class Converter(MarkdownConverter):
            def convert_kbd(self, el: Any, text: str, parent_tags: Any) -> str:  # noqa: ANN401, ARG002
                return f"<kbd>{text}</kbd>"

            def convert_sub(self, el: Any, text: str, parent_tags: Any) -> str:  # noqa: ANN401, ARG002
                return f"<sub>{text}</sub>"

            def convert_sup(self, el: Any, text: str, parent_tags: Any) -> str:  # noqa: ANN401, ARG002
                return f"<sup>{text}</sup>"

            def convert_mark(self, el: Any, text: str, parent_tags: Any) -> str:  # noqa: ANN401, ARG002
                return f"<mark>{text}</mark>"

        self._cls = Converter

    def __call__(self, fragment: str, bullet: str) -> str:
        def language(element: Any) -> str:  # noqa: ANN401 - bs4 tag
            candidates = [element, *(element.find_all("code", recursive=False) or [])]
            for node in candidates:
                for cls in node.get("class") or []:
                    for prefix in ("language-", "lang-"):
                        if cls.startswith(prefix):
                            return str(cls[len(prefix) :])
            return ""

        converter = self._cls(
            heading_style="ATX",
            bullets=bullet,
            code_language_callback=language,
            escape_asterisks=True,
            escape_underscores=True,
            escape_misc=False,
            wrap=False,
            newline_style="spaces",
        )
        return str(converter.convert(fragment))


_markdownify: _Markdownify | None = None


def convert_html(fragment: str, backend: Backend = "html-to-markdown", *, bullet: str = "-") -> str:
    """Markdown for a pre-normalized HTML fragment, raw (not yet post-processed)."""
    global _markdownify  # noqa: PLW0603 - one lazily built converter class
    if backend == "markdownify":
        if _markdownify is None:
            _markdownify = _Markdownify()
        return _markdownify(fragment, bullet)
    return _html_to_markdown(fragment, bullet)
