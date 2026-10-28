"""URL normalization and scope rules, applied to every URL before anything else."""

from __future__ import annotations

import fnmatch
import posixpath
import re
from dataclasses import dataclass, field
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_PARAMS = frozenset({"gclid", "fbclid", "ref", "source", "wt.mc_id"})
DEFAULT_PORTS = {"http": "80", "https": "443"}
_LOCALE_SEGMENT = re.compile(r"^[a-z]{2}(?:-[a-z]{2,4})?$", re.IGNORECASE)
_UNRESERVED = "-._~" + "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
_PERCENT = re.compile(r"%([0-9A-Fa-f]{2})")


def host_of(url: str) -> str:
    """The lowercase host of a URL, or the empty string."""
    return (urlsplit(url).hostname or "").lower()


def path_pattern(url: str) -> str:
    """The first two path segments, the key of the tier cache.

    >>> path_pattern("https://h/en-us/graph/api/user-get")
    '/en-us/graph'
    """
    segments = [s for s in urlsplit(url).path.split("/") if s]
    return "/" + "/".join(segments[:2])


def locale_segment(path: str) -> str:
    """The leading locale segment of a path, lowercased, or the empty string."""
    first = path.strip("/").split("/", 1)[0]
    return first.lower() if first and _LOCALE_SEGMENT.match(first) else ""


def _normalize_path(path: str) -> str:
    if not path:
        return "/"
    collapsed = posixpath.normpath(path)
    if path.endswith("/") and not collapsed.endswith("/"):
        collapsed += "/"
    if not collapsed.startswith("/"):
        collapsed = "/" + collapsed
    lowered = collapsed.lower()
    for name in ("/index.html", "/index.htm"):
        if lowered.endswith(name):
            collapsed = collapsed[: -len(name)] + "/"
    return _PERCENT.sub(_decode_unreserved, collapsed)


def _decode_unreserved(match: re.Match[str]) -> str:
    """Decode a percent escape only when it encodes an unreserved character."""
    char = chr(int(match.group(1), 16))
    return char if char in _UNRESERVED else match.group(0).upper()


@dataclass(frozen=True, slots=True)
class UrlNormalizer:
    """Normalizes URLs for identity, keeping only the meaningful query parameters."""

    meaningful_query_params: frozenset[str] = field(default_factory=frozenset)

    def normalize(self, url: str) -> str:
        """The identity form of `url`: no fragment, sorted meaningful params, clean path.

        >>> UrlNormalizer(frozenset({"view"})).normalize(
        ...     "HTTPS://Learn.Microsoft.com:443/en-us/graph/index.html?tabs=http&view=v1&utm_source=x#frag"
        ... )
        'https://learn.microsoft.com/en-us/graph/?view=v1'
        """
        parts = urlsplit(url.strip())
        scheme = parts.scheme.lower()
        host = (parts.hostname or "").lower()
        if parts.port is not None and str(parts.port) != DEFAULT_PORTS.get(scheme):
            host = f"{host}:{parts.port}"
        path = _normalize_path(parts.path)
        kept = sorted(
            (key, value)
            for key, value in parse_qsl(parts.query, keep_blank_values=True)
            if self._keep(key)
        )
        query = urlencode(kept, doseq=True) if kept else ""
        return urlunsplit((scheme, host, path, query, ""))

    def _keep(self, key: str) -> bool:
        lowered = key.lower()
        if lowered.startswith("utm_") or lowered in TRACKING_PARAMS:
            return False
        return key in self.meaningful_query_params

    def split_fragment(self, url: str) -> tuple[str, str]:
        """The normalized URL and the fragment that was on it."""
        fragment = urlsplit(url).fragment
        return self.normalize(url), fragment


def _matcher(pattern: str) -> re.Pattern[str]:
    if pattern.startswith("re:"):
        return re.compile(pattern[3:])
    return re.compile(fnmatch.translate(pattern))


@dataclass(frozen=True, slots=True)
class ScopeRules:
    """Whether a normalized URL belongs to the mirror."""

    allowed_hosts: frozenset[str]
    path_prefixes: tuple[str, ...]
    include: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    locale: str = ""
    max_depth: int = 10
    _include: tuple[re.Pattern[str], ...] = field(init=False, repr=False, compare=False)
    _exclude: tuple[re.Pattern[str], ...] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Compile the glob and regex rules once."""
        object.__setattr__(self, "_include", tuple(_matcher(p) for p in self.include))
        object.__setattr__(self, "_exclude", tuple(_matcher(p) for p in self.exclude))

    def host_allowed(self, url: str) -> bool:
        """Whether the host (with or without its port) is one of the allowed hosts."""
        netloc = urlsplit(url).netloc.lower()
        return netloc in self.allowed_hosts or host_of(url) in self.allowed_hosts

    def in_scope(self, url: str, depth: int = 0) -> bool:
        """Every rule at once: host, prefix, include, exclude, locale and depth.

        >>> rules = ScopeRules(frozenset({"h"}), ("/docs/",), exclude=("re:/docs/old",))
        >>> rules.in_scope("https://h/docs/a"), rules.in_scope("https://h/docs/old/a")
        (True, False)
        """
        if depth > self.max_depth or not self.host_allowed(url):
            return False
        path = urlsplit(url).path or "/"
        if not any(path.startswith(prefix) for prefix in self.path_prefixes):
            return False
        if self.locale:
            segment = locale_segment(path)
            if segment and segment != self.locale:
                return False
        probe = url
        if any(rule.search(probe) for rule in self._exclude_rules()):
            return False
        include = self._include_rules()
        return not include or any(rule.search(probe) for rule in include)

    def _include_rules(self) -> tuple[re.Pattern[str], ...]:
        return self._include

    def _exclude_rules(self) -> tuple[re.Pattern[str], ...]:
        return self._exclude

    def with_locale(self, url: str) -> str:
        """`url` with its locale segment replaced by the pinned locale, when it has one."""
        if not self.locale:
            return url
        parts = urlsplit(url)
        segments = parts.path.split("/")
        if len(segments) > 1 and locale_segment(parts.path) and segments[1].lower() != self.locale:
            segments[1] = self.locale
            return urlunsplit(
                (parts.scheme, parts.netloc, "/".join(segments), parts.query, parts.fragment)
            )
        return url
