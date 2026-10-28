"""Tidy the converter's output without touching fenced code."""

from __future__ import annotations

import re

_FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})")
_BLANK_RUN = re.compile(r"\n{3,}")


def _split_fences(text: str) -> list[tuple[bool, str]]:
    """Alternating (is_code, chunk) pieces, fences kept whole."""
    pieces: list[tuple[bool, str]] = []
    buffer: list[str] = []
    in_code = False
    fence = ""
    for line in text.split("\n"):
        match = _FENCE.match(line)
        if not in_code and match:
            pieces.append((False, "\n".join(buffer)))
            buffer = [line]
            in_code = True
            fence = match.group(2)
            continue
        if in_code:
            buffer.append(line)
            stripped = line.strip()
            if (
                stripped.startswith(fence[0])
                and set(stripped) == {fence[0]}
                and len(stripped) >= len(fence)
            ):
                pieces.append((True, "\n".join(buffer)))
                buffer = []
                in_code = False
            continue
        buffer.append(line)
    pieces.append((in_code, "\n".join(buffer)))
    return pieces


def postprocess(markdown: str) -> str:
    r"""Collapse blank runs, trim trailing whitespace, LF endings, one final newline.

    Fenced code is left exactly as it was.

    >>> postprocess("a  \n\n\n\nb\r\n")
    'a\n\nb\n'
    """
    text = markdown.replace("\r\n", "\n").replace("\r", "\n")
    out: list[str] = []
    for is_code, chunk in _split_fences(text):
        if is_code:
            out.append(chunk)
            continue
        lines = [line.rstrip() for line in chunk.split("\n")]
        prose = _BLANK_RUN.sub("\n\n", "\n".join(_space_quotes(lines))).strip("\n")
        if prose:
            out.append(prose)
    return "\n\n".join(out).strip("\n") + "\n"


_QUOTE = re.compile(r"^\s*>")
_ALERT = re.compile(r"^\s*> \[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]")


def _space_quotes(lines: list[str]) -> list[str]:
    """One blank line around every blockquote, and between two adjacent alerts."""
    spaced: list[str] = []
    for line in lines:
        previous = spaced[-1] if spaced else ""
        starts_quote = bool(_QUOTE.match(line))
        previous_quote = bool(_QUOTE.match(previous))
        if previous.strip() and (
            (starts_quote and not previous_quote)
            or (_ALERT.match(line) and previous_quote)
            or (previous_quote and not starts_quote)
        ):
            spaced.append("")
        spaced.append(line)
    return spaced
