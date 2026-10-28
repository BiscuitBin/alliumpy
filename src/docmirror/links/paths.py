"""URL to output path, stable once assigned and collision-free.

The mapping is `{path}` relative to the first matching prefix: a trailing slash becomes
`index.md`, `.html`/`.htm`/`.aspx` are stripped, a meaningful query parameter becomes a
version segment, every character outside `[A-Za-z0-9._-]` becomes `-`, and a collision
or a reserved name gets `-<6 hex of sha256(normalized url)>`.
"""

from __future__ import annotations

import hashlib
import posixpath
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from urllib.parse import parse_qsl, unquote, urlsplit

if TYPE_CHECKING:
    from collections.abc import Callable

RESERVED_FILES = frozenset(
    {"index.md", "index.jsonl", "llms.txt", "crawl-report.json", "docmirror.toml", "_index.md"}
)
RESERVED_DIRS = frozenset({"_removed", ".docmirror"})
WINDOWS_RESERVED = frozenset(
    {
        "con",
        "prn",
        "aux",
        "nul",
        *(f"com{i}" for i in range(1, 10)),
        *(f"lpt{i}" for i in range(1, 10)),
    }
)
MAX_PATH_CHARS = 200
_UNSAFE = re.compile(r"[^A-Za-z0-9._-]")
_STRIP_EXT = (".html", ".htm", ".aspx")


def _segment(raw: str) -> str:
    text = _UNSAFE.sub("-", unquote(raw))
    text = re.sub(r"-{2,}", "-", text).strip("-") or "-"
    if text.split(".")[0].lower() in WINDOWS_RESERVED:
        text = text + "-"
    return text


def url_hash(normalized_url: str) -> str:
    """The six-hex collision suffix for a URL."""
    return hashlib.sha256(normalized_url.encode("utf-8")).hexdigest()[:6]


@dataclass
class PathMapper:
    """Computes candidate paths and resolves collisions through `taken`."""

    path_prefixes: tuple[str, ...]
    version_param: str = ""
    version_default: str = ""
    version_map: dict[str, str] = field(default_factory=dict)
    lowercase: bool = False
    template: str = "{path}"

    def version_of(self, normalized_url: str) -> str | None:
        """The page's version: the mapped parameter value, else the default, else None."""
        segment = self.version_segment(normalized_url)
        if segment is not None:
            return segment
        return self.version_default or None if self.version_param else None

    def version_segment(self, normalized_url: str) -> str | None:
        """The version path segment, only when the URL carries the version parameter.

        A page without the parameter keeps its plain path and reports `version_default`
        in its frontmatter; inserting the default into every path would move every
        conceptual page under a version it does not have.
        """
        if not self.version_param:
            return None
        params = dict(parse_qsl(urlsplit(normalized_url).query, keep_blank_values=True))
        raw = params.get(self.version_param)
        if raw is None:
            return None
        return self.version_map.get(raw, _segment(raw))

    def candidate(self, normalized_url: str) -> str:
        """The path a URL maps to before collision handling.

        >>> m = PathMapper(("/en-us/graph/",), "view", "v1.0", {"graph-rest-1.0": "v1.0"})
        >>> m.candidate("https://h/en-us/graph/api/user-get?view=graph-rest-1.0")
        'api/v1.0/user-get.md'
        >>> m.candidate("https://h/en-us/graph/")
        'index.md'
        """
        parts = urlsplit(normalized_url)
        path = parts.path or "/"
        for prefix in self.path_prefixes:
            if path.startswith(prefix):
                path = path[len(prefix) :]
                break
        else:
            path = path.lstrip("/")
        segments = [s for s in path.split("/") if s]
        trailing = path.endswith("/") or not segments
        if trailing:
            name = "index"
        else:
            name = segments.pop()
            lowered = name.lower()
            for ext in _STRIP_EXT:
                if lowered.endswith(ext):
                    name = name[: -len(ext)]
                    break
        version = self.version_segment(normalized_url)
        if version is not None:
            segments = [*segments, version]
        file_name = _segment(name) + ".md"
        mapped = "/".join([*(_segment(s) for s in segments), file_name])
        if self.lowercase:
            mapped = mapped.lower()
        rendered = self.template.replace("{path}", mapped)
        return posixpath.normpath(rendered)

    def assign(self, normalized_url: str, taken: Callable[[str], bool]) -> str:
        """The final path: the candidate unless taken or reserved, else the hashed form."""
        candidate = self.candidate(normalized_url)
        reserved = (
            candidate in RESERVED_FILES
            or candidate.split("/")[0] in RESERVED_DIRS
            or (candidate.endswith("/_index.md"))
            or len(candidate) > MAX_PATH_CHARS
        )
        if not reserved and not taken(candidate):
            return candidate
        stem = candidate.rpartition(".md")[0]
        base = stem or candidate
        if len(base) > MAX_PATH_CHARS - 10:
            base = base[: MAX_PATH_CHARS - 10]
        hashed = f"{base}-{url_hash(normalized_url)}.md"
        if taken(hashed):
            message = f"path collision cannot be resolved for {normalized_url}: {hashed}"
            raise ValueError(message)
        return hashed


def relative_path(from_path: str, to_path: str) -> str:
    """The POSIX relative path from the directory of `from_path` to `to_path`.

    >>> relative_path("api/v1.0/user-get.md", "api/beta/user-list.md")
    '../beta/user-list.md'
    >>> relative_path("index.md", "guide/start.md")
    'guide/start.md'
    """
    start = posixpath.dirname(from_path) or "."
    return posixpath.relpath(to_path, start)
