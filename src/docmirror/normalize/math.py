"""TeX math from MathML annotations, MathJax scripts, KaTeX and `data-tex`; else keep HTML."""

from __future__ import annotations

from typing import TYPE_CHECKING

from docmirror.normalize.islands import sanitize

if TYPE_CHECKING:
    from lxml import html

    from docmirror.normalize.islands import Islands

MATHML = "{http://www.w3.org/1998/Math/MathML}"


def _tex_of(element: html.HtmlElement) -> str | None:
    tex = element.get("data-tex") or element.get("alttext")
    if tex:
        return str(tex)
    for annotation in element.iter("annotation", MATHML + "annotation"):
        if (annotation.get("encoding") or "").lower() == "application/x-tex" and annotation.text:
            return str(annotation.text).strip()
    return None


def _display(element: html.HtmlElement) -> bool:
    return (
        (element.get("display") or "").lower() == "block"
        or "display" in (element.get("class") or "")
        or (element.get("type") or "").endswith("mode=display")
    )


def transform(content: html.HtmlElement, islands: Islands) -> None:
    """Replace each math construct with `$...$`, `$$...$$`, or the sanitized HTML."""
    candidates: list[html.HtmlElement] = []
    for element in content.iter():
        tag = element.tag
        if not isinstance(tag, str):
            continue
        if (
            tag in {"math", MATHML + "math"}
            or (tag == "script" and (element.get("type") or "").startswith("math/tex"))
            or "katex" in (element.get("class") or "").split()
            or element.get("data-tex")
        ):
            candidates.append(element)
    for element in candidates:
        if element.getparent() is None or any(a in candidates for a in element.iterancestors()):
            continue
        display = _display(element)
        if element.tag == "script":
            tex: str | None = (element.text or "").strip()
        else:
            tex = _tex_of(element)
        if tex:
            raw = f"$${tex}$$" if display else f"${tex}$"
        else:
            raw = sanitize(element, {"display", "class", "id"})
        islands.replace_element(element, raw, block=display)
