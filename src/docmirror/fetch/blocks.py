"""Classify a response: hard block, challenge, soft block, or none, with the signature."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from docmirror.fetch.session import FetchResult

CHALLENGE_BODY = (
    "Just a moment...",
    "/cdn-cgi/challenge-platform",
    "Checking your browser",
    "captcha-delivery.com",
    "Request unsuccessful. Incapsula",
    "_Incapsula_Resource",
    "Pardon Our Interruption",
    "Attention Required! | Cloudflare",
)
_ACCESS_DENIED = re.compile(
    r"Access Denied.{0,400}Reference\s*#?\s*[0-9a-f.]+", re.IGNORECASE | re.DOTALL
)
CHALLENGE_COOKIES = ("_abck", "ak_bmsc", "datadome", "__cf_bm")
TINY_BODY = 4096
HARD_STATUSES = frozenset({401, 403, 429})
SERVICE_UNAVAILABLE = 503
SOFT_RATIO = 0.10


@dataclass(frozen=True, slots=True)
class BlockVerdict:
    """What the classifier concluded."""

    kind: str  # none | hard | challenge | soft
    signature: str

    @property
    def blocked(self) -> bool:
        """Whether this response counts as a block."""
        return self.kind != "none"


def challenge_signature(result: FetchResult) -> str:
    """The matching challenge signature of a response, or the empty string."""
    if result.headers.get("cf-mitigated", "").lower() == "challenge":
        return "header cf-mitigated: challenge"
    text = result.text()[:200_000]
    for needle in CHALLENGE_BODY:
        if needle in text:
            return f"body contains {needle!r}"
    if _ACCESS_DENIED.search(text):
        return "body contains Access Denied with a Reference ID"
    if len(result.body) < TINY_BODY:
        for name in CHALLENGE_COOKIES:
            if name in result.cookies or f"{name}=" in result.headers.get("set-cookie", ""):
                return f"cookie {name} with a tiny body"
    return ""


def classify(
    result: FetchResult,
    *,
    text_chars: int | None = None,
    median_text_chars: float | None = None,
    login_wall: bool = False,
) -> BlockVerdict:
    """Classify one response.

    >>> from docmirror.fetch.session import FetchResult
    >>> classify(FetchResult("u", "u", 403, body=b"x")).kind
    'hard'
    >>> classify(FetchResult("u", "u", 200, body=b"<p>fine</p>")).kind
    'none'
    """
    signature = challenge_signature(result)
    if result.status in HARD_STATUSES:
        return BlockVerdict("hard", signature or f"http {result.status}")
    if result.status == SERVICE_UNAVAILABLE and signature:
        return BlockVerdict("hard", signature)
    if signature:
        return BlockVerdict("challenge", signature)
    if login_wall:
        return BlockVerdict("soft", "login wall")
    if (
        text_chars is not None
        and median_text_chars is not None
        and median_text_chars > 0
        and text_chars < median_text_chars * SOFT_RATIO
    ):
        return BlockVerdict("soft", f"main text {text_chars} chars under 10% of the host median")
    return BlockVerdict("none", "")
