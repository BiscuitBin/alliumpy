"""YAML frontmatter with sorted keys and a body hash that ignores volatile values."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
    from collections.abc import Mapping


def body_sha256(body: str) -> str:
    r"""The SHA-256 of the normalized Markdown body alone.

    >>> body_sha256("x\\n")[:8]
    '2d711642'
    """
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def render_frontmatter(fields: Mapping[str, Any]) -> str:
    """A `---` block with keys sorted; keys whose value is None are omitted."""
    present = {key: value for key, value in fields.items() if value is not None}
    dumped = yaml.safe_dump(
        present, sort_keys=True, allow_unicode=True, default_flow_style=None, width=1000
    )
    return "---\n" + dumped + "---\n"


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    r"""The frontmatter mapping and the body of a page file.

    >>> split_frontmatter("---\\ntitle: T\\n---\\n\\nbody\\n")
    ({'title': 'T'}, 'body\\n')
    """
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    loaded = yaml.safe_load(text[4:end]) or {}
    body = text[end + 5 :]
    # A page file is the block, one blank line, then the body; the blank line is the
    # separator, not part of the body the hash covers.
    body = body.removeprefix("\n")
    return (loaded if isinstance(loaded, dict) else {}), body
