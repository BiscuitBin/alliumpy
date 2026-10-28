"""The three-tier fetch ladder and the decision to escalate from HTTP to a browser."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from docmirror.extract.extractor import extract_page
from docmirror.fetch.blocks import BlockVerdict, classify
from docmirror.frontier.urls import host_of, path_pattern

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from docmirror.config.models import Config, Profile
    from docmirror.extract.extractor import Extraction
    from docmirror.fetch.session import FetchResult

LOG = logging.getLogger("docmirror.ladder")
TIERS = ("http", "browser", "stealth")
LARGE_RAW = 5 * 1024


# A render after a soft block must grow the main text this much to replace the HTTP copy.
SOFT_GAIN = 2.0


@dataclass(slots=True)
class LadderOutcome:
    """The result of walking the ladder for one URL."""

    result: FetchResult
    extraction: Extraction | None
    verdict: BlockVerdict
    tier: str
    escalated: bool = False
    render_needed: bool = False
    tiers_tried: list[str] = field(default_factory=list)


def needs_render(
    extraction: Extraction, result: FetchResult, profile: Profile, min_text_chars: int
) -> str:
    """Why a Tier 0 fetch must escalate, or the empty string."""
    meta = extraction.metadata
    if meta.spa_shell:
        return "empty SPA shell"
    if meta.noscript_needs_js:
        return "noscript asks for JavaScript"
    if profile.main_selector and extraction.extractor != "profile":
        return "main selector absent"
    if (
        extraction.extractor != "profile"
        and extraction.text_chars < min_text_chars
        and len(result.body) > LARGE_RAW
    ):
        # A profile match is trusted: short reference pages are short on purpose.
        return (
            f"main text {extraction.text_chars} chars under {min_text_chars} "
            f"with {len(result.body)} bytes of HTML"
        )
    return ""


class FetchLadder:
    """Walks the tiers for a URL, honouring the render mode and the tier cache."""

    def __init__(
        self,
        config: Config,
        profile: Profile,
        tiers: dict[str, Callable[..., Awaitable[FetchResult]]],
        *,
        cached_tier: Callable[[str, str], str | None],
        cache_tier: Callable[[str, str, str], None],
        median_text: Callable[[str], float | None],
        on_outcome: Callable[[str, str, bool], None] | None = None,
    ) -> None:
        """Wire the tier fetchers, the tier cache and the per-attempt outcome hook."""
        self.config = config
        self.profile = profile
        self.tiers = tiers
        self.cached_tier = cached_tier
        self.cache_tier = cache_tier
        self.median_text = median_text
        self.on_outcome = on_outcome

    def available(self) -> list[str]:
        """The tiers that can be used, in order."""
        order = [t for t in TIERS if t in self.tiers]
        stealth = self.config.antibot.stealth
        if stealth == "off":
            order = [t for t in order if t == "http"]
        elif stealth == "patchright":
            order = [t for t in order if t != "stealth"]
        if self.config.render.mode == "never":
            order = [t for t in order if t == "http"]
        return order

    def start_tier(self, url: str, host_tier: str) -> str:
        """Where to start: the cache, the host's escalated tier, or `always`."""
        order = self.available()
        if self.config.render.mode == "always" and len(order) > 1:
            return order[1]
        cached = self.cached_tier(host_of(url), path_pattern(url))
        candidates = [t for t in (cached, host_tier) if t in order]
        if not candidates:
            return order[0] if order else "http"
        return max(candidates, key=order.index)

    def _extract(self, result: FetchResult) -> Extraction:
        return extract_page(
            result.text(),
            result.final_url,
            self.profile,
            fallbacks=tuple(self.config.extract.fallbacks),
        )

    async def fetch(
        self,
        url: str,
        *,
        host_tier: str = "http",
        etag: str | None = None,
        last_modified: str | None = None,
    ) -> LadderOutcome:
        """Fetch through the ladder, escalating while the configuration allows."""
        order = self.available()
        tier = self.start_tier(url, host_tier)
        index = order.index(tier) if tier in order else 0
        outcome: LadderOutcome | None = None
        suspected: LadderOutcome | None = None
        first_reason = ""
        while index < len(order):
            tier = order[index]
            if tier == "http" and (etag or last_modified):
                result = await self.tiers[tier](url, etag=etag, last_modified=last_modified)
            else:
                result = await self.tiers[tier](url)
            tried = [] if outcome is None else outcome.tiers_tried
            tried.append(tier)
            extraction = self._extract(result) if result.ok else None
            verdict = classify(
                result,
                text_chars=extraction.text_chars if extraction else None,
                median_text_chars=self.median_text(host_of(url)) if extraction else None,
            )
            if self.on_outcome is not None and (result.ok or verdict.blocked):
                # Every tier attempt is one outcome for the host's breaker; a soft block is
                # a suspicion recorded on the page, not a block the breaker counts.
                self.on_outcome(host_of(url), tier, verdict.kind in {"hard", "challenge"})
            reason = ""
            if extraction is not None and tier == "http" and not verdict.blocked:
                reason = needs_render(
                    extraction, result, self.profile, self.config.render.min_text_chars
                )
            kind = result.headers.get("content-type", "")
            not_html = bool(kind) and "html" not in kind and "xml" not in kind
            # A PDF or an image is what it is at every tier: never rendered.
            escalate = (bool(reason) or verdict.blocked) and not (result.ok and not_html)
            if reason and not first_reason:
                first_reason = reason
            if (
                suspected is not None
                and suspected.extraction is not None
                and extraction is not None
                and extraction.text_chars < suspected.extraction.text_chars * SOFT_GAIN
            ):
                # Rendering did not add text: the page is small on purpose, so the HTTP
                # copy stands, with the suspicion recorded on it, and the walk ends here.
                suspected.tiers_tried = tried
                suspected.escalated = True
                return suspected
            outcome = LadderOutcome(
                result=result,
                extraction=extraction,
                verdict=verdict,
                tier=tier,
                escalated=index > order.index(order[0])
                or (outcome is not None and outcome.escalated),
                render_needed=bool(reason),
                tiers_tried=tried,
            )
            if not escalate or index + 1 >= len(order):
                if reason and index + 1 >= len(order):
                    LOG.info("%s needs rendering (%s); no further tier is available", url, reason)
                break
            if result.not_modified:
                break
            LOG.info("escalating %s from %s: %s", url, tier, reason or verdict.signature)
            if verdict.kind == "soft" and not reason:
                suspected = outcome
            index += 1
            outcome.escalated = True
        assert outcome is not None  # noqa: S101 - the loop runs at least once
        if (
            outcome.escalated
            and outcome.result.ok
            and not outcome.verdict.blocked
            and first_reason in {"empty SPA shell", "noscript asks for JavaScript"}
        ):
            # Only a structural signal that the site is client-rendered is worth caching
            # for the whole path pattern; a block or a thin page is about one URL.
            self.cache_tier(host_of(url), path_pattern(url), outcome.tier)
        return outcome
