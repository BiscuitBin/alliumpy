"""Orchestrate a crawl: discovery, the frontier loop, one page through the stages, the report.

Every stage after fetching is synchronous and runs in a worker thread; the loop is
asyncio with a per-host limiter. `crawl-report.json` is written in a `finally` block so
exits 1 and 3 always carry it.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin, urlsplit, urlunsplit

from docmirror.convert import (
    CONVERTER_NAMES,
    body_sha256,
    convert_html,
    postprocess,
    render_frontmatter,
)
from docmirror.exit_codes import ExitCode, highest
from docmirror.extract import extract_page
from docmirror.fetch.breaker import HostBreaker
from docmirror.fetch.ladder import FetchLadder, LadderOutcome
from docmirror.fetch.politeness import HostLimiter, backoff_delay, retry_after_seconds
from docmirror.fetch.session import FetchResult, HttpFetcher
from docmirror.frontier.discovery import (
    page_links,
    parse_llms_txt,
    parse_sitemap,
    rank_child_sitemaps,
)
from docmirror.frontier.robots import Robots
from docmirror.frontier.urls import ScopeRules, UrlNormalizer, host_of, locale_segment
from docmirror.links.paths import PathMapper
from docmirror.normalize import normalize
from docmirror.quality import measure_quality
from docmirror.quality.metrics import GATE_NAMES
from docmirror.render.driver import BrowserDriver, driver_for
from docmirror.report.builder import ReportBuilder, config_hash
from docmirror.report.models import BlockedUrl, FailedUrl
from docmirror.state.db import FrontierEntry, Manifest, atomic_write_text, now_iso

if TYPE_CHECKING:
    from docmirror.config.models import Config, Profile
    from docmirror.report.events import EventEmitter

LOG = logging.getLogger("docmirror.pipeline")
SITEMAP_CANDIDATES = ("sitemap.xml", "sitemap_index.xml")
# Sitemap entries queue one hop below the start pages' own links, so a small crawl
# stays near the start URL instead of sampling the whole sitemap.
SITEMAP_DEPTH = 2
HTTP_OK = 200
INCOMPLETE_FLAGS = frozenset({"render_needed", "empty_content"})
HTTP_MULTIPLE = 300
HTTP_NOT_MODIFIED = 304
HTTP_NOT_FOUND = 404
HTTP_GONE = 410
HTTP_FORBIDDEN = 403
HTTP_TOO_MANY = 429
HTTP_SERVER_ERROR = 500
HTTP_UNAVAILABLE = 503


@dataclass(slots=True)
class ProcessedPage:
    """One page after extraction, normalization and conversion."""

    markdown_body: str
    title: str
    description: str
    extractor: str
    canonical_url: str | None
    breadcrumbs: list[str]
    last_updated: str | None
    lang: str
    anchors: list[str]
    links: list[tuple[str, str]]
    quality_score: float
    quality_failed: list[str]
    flags: set[str]
    headings: list[str]
    word_count: int
    text_chars: int
    render_needed: bool
    counts: dict[str, int] = field(default_factory=dict)


def process_page(text: str, url: str, config: Config, profile: Profile) -> ProcessedPage:
    """Run the pure stages: extract, normalize, convert, post-process, measure."""
    extraction = extract_page(text, url, profile, fallbacks=tuple(config.extract.fallbacks))
    meta = extraction.metadata
    dom_for_quality = _copy(extraction.content)
    first_h1 = next(iter(extraction.content.iter("h1")), None)
    h1_text = " ".join(first_h1.text_content().split()) if first_h1 is not None else ""
    title = h1_text or meta.og_title or meta.title
    backend = config.convert.backend
    bullet = config.convert.bullet

    def convert(fragment: str) -> str:
        return postprocess(convert_html(fragment, backend, bullet=bullet))

    normalized = normalize(extraction.content, profile, title=title, convert=convert)
    raw = convert_html(normalized.fragment, backend, bullet=bullet)
    body = postprocess(normalized.islands.restore(raw))
    quality = measure_quality(dom_for_quality, body, normalized.counts)
    flags = set(normalized.flags)
    if extraction.extractor != "profile":
        flags.add("extractor_fallback")
    if extraction.text_chars == 0:
        flags.add("empty_content")
    links = [(link.url, link.kind) for link in page_links(dom_for_quality, url)]
    headings = [
        " ".join(h.text_content().split()).removesuffix("}").rsplit(" {#", 1)[0]
        for h in dom_for_quality.iter("h2")
    ]
    render_needed = (
        meta.noscript_needs_js
        or meta.spa_shell
        or (extraction.text_chars < config.render.min_text_chars and len(text) > 5000)  # noqa: PLR2004 - spec threshold
    )
    description = meta.description or _first_paragraph(body)
    return ProcessedPage(
        markdown_body=body,
        title=title,
        description=description,
        extractor=f"profile:{config.site.profile}"
        if extraction.extractor == "profile"
        else extraction.extractor,
        canonical_url=meta.canonical_url,
        breadcrumbs=meta.breadcrumbs,
        last_updated=meta.last_updated,
        lang=meta.lang,
        anchors=normalized.anchors,
        links=links,
        quality_score=quality.score,
        quality_failed=quality.failed,
        flags=flags,
        headings=headings,
        word_count=len(body.split()),
        text_chars=extraction.text_chars,
        render_needed=render_needed,
        counts=normalized.counts,
    )


def _copy(element: Any) -> Any:  # noqa: ANN401 - lxml element
    import copy  # noqa: PLC0415

    return copy.deepcopy(element)


def _first_paragraph(body: str, limit: int = 200) -> str:
    for block in body.split("\n\n"):
        line = " ".join(block.split())
        if not line or line.startswith(("#", "```", "|", "<", ">", "-", "*", "!")):
            continue
        if len(line) <= limit:
            return line
        cut = line[:limit].rsplit(" ", 1)[0]
        return cut + "…"
    return ""


class Crawler:
    """One crawl or update run over an output directory."""

    def __init__(
        self,
        config: Config,
        out_dir: Path,
        manifest: Manifest,
        emitter: EventEmitter,
        *,
        command: str = "crawl",
        config_text: str = "",
        resume: bool = True,
        dry_run: bool = False,
    ) -> None:
        """Wire the helpers from the configuration."""
        self.config = config
        self.out_dir = out_dir
        self.manifest = manifest
        self.emitter = emitter
        self.command = command
        self.resume = resume
        self.dry_run = dry_run
        self.profile = config.profile()
        meaningful = set(config.scope.meaningful_query_params) | set(
            self.profile.meaningful_query_params
        )
        if config.scope.version_param:
            meaningful.add(config.scope.version_param)
        self.normalizer = UrlNormalizer(frozenset(meaningful))
        start = config.site.start_urls[0] if config.site.start_urls else config.site.root_url
        self.scheme = urlsplit(start).scheme or "https"
        hosts = set(config.scope.allowed_hosts) or {urlsplit(start).netloc.lower()}
        prefixes = tuple(config.scope.path_prefixes) or (_directory(start),)
        self.scope = ScopeRules(
            frozenset(h.lower() for h in hosts),
            prefixes,
            tuple(config.scope.include),
            tuple(config.scope.exclude),
            locale=config.site.locale,
            max_depth=config.scope.max_depth,
        )
        self.mapper = PathMapper(
            prefixes,
            config.scope.version_param,
            config.scope.version_default,
            dict(config.scope.version_map),
            lowercase=self.profile.lowercase_paths,
            template=config.links.path_template,
        )
        self.fetcher = HttpFetcher(
            impersonate=config.fetch.impersonate,
            user_agent=config.fetch.user_agent,
            timeout_s=config.fetch.timeout_s,
            locale=config.site.locale,
        )
        self.report = ReportBuilder(
            command=command,
            config_hash=config_hash(config_text),
            robots_ignored=config.fetch.robots == "ignore",
            window=config.antibot.window,
        )
        self.limiters: dict[str, HostLimiter] = {}
        self.robots: dict[str, Robots] = {}
        self.bytes_total = 0
        self.fetched_pages = 0
        self.exit_code = ExitCode.OK
        self.written_paths: set[str] = set()
        self._stop = False
        self.must_fetch: set[str] = set()
        self.breakers: dict[str, HostBreaker] = {}
        self.drivers: dict[str, BrowserDriver] = {}
        self.text_lengths: dict[str, list[int]] = {}
        self.ladder = FetchLadder(
            config,
            self.profile,
            self._tier_fetchers(),
            cached_tier=manifest.cached_tier,
            cache_tier=manifest.cache_tier,
            median_text=self._median_text,
            on_outcome=self._record_outcome,
        )

    # -- helpers -----------------------------------------------------------------

    def limiter(self, host: str) -> HostLimiter:
        """The limiter for a host, honouring its crawl delay."""
        limiter = self.limiters.get(host)
        if limiter is None:
            delay = self.robots[host].crawl_delay() if host in self.robots else None
            limiter = HostLimiter(
                self.config.fetch.rate_per_host,
                self.config.fetch.concurrency_per_host,
                crawl_delay=delay,
            )
            self.limiters[host] = limiter
        return limiter

    def breaker(self, host: str) -> HostBreaker:
        """The circuit breaker for a host."""
        breaker = self.breakers.get(host)
        if breaker is None:
            available = self.ladder.available()
            breaker = HostBreaker(
                window=self.config.antibot.window,
                threshold=self.config.antibot.block_rate_threshold,
                highest_tier=available[-1] if available else "http",
            )
            self.breakers[host] = breaker
        return breaker

    def _median_text(self, host: str) -> float | None:
        lengths = self.text_lengths.get(host)
        if not lengths or len(lengths) < 5:  # noqa: PLR2004 - a median of fewer pages means little
            return None
        ordered = sorted(lengths)
        return float(ordered[len(ordered) // 2])

    def _tier_fetchers(self) -> dict[str, Any]:
        tiers: dict[str, Any] = {"http": self.polite_fetch}
        stealth = self.config.antibot.stealth
        if stealth != "off" and self.config.render.mode != "never":
            tiers["browser"] = self._browser_fetcher("browser")
            if stealth == "camoufox":
                tiers["stealth"] = self._browser_fetcher("stealth")
        return tiers

    def _browser_fetcher(self, tier: str) -> Any:  # noqa: ANN401 - an async callable
        async def fetch(url: str) -> FetchResult:
            driver = self.drivers.get(tier)
            if driver is None:
                created = driver_for(
                    tier,
                    self.out_dir / ".docmirror",
                    self.config.render,
                    locale=self.config.site.locale,
                )
                if created is None:
                    return FetchResult(
                        url=url,
                        final_url=url,
                        status=0,
                        tier=tier,
                        error=f"{tier} tier unavailable",
                    )
                self.drivers[tier] = created
                driver = created
            limiter = self.limiter(host_of(url))
            await limiter.acquire()
            try:
                result = await driver.fetch(url)
            finally:
                limiter.release()
            if result.ok and result.cookies:
                self.fetcher.set_cookies(host_of(url), result.cookies)
            return result

        return fetch

    async def robots_for(self, host: str) -> Robots:
        """Fetch and cache a host's robots.txt."""
        if host in self.robots:
            return self.robots[host]
        respect = self.config.fetch.robots == "respect"
        agent = self.fetcher.user_agent or "docmirror"
        result = await self.fetcher.fetch(f"{self.scheme}://{host}/robots.txt")
        robots = (
            Robots.parse(result.text(), agent, respect=respect)
            if result.ok
            else Robots.absent(agent, respect=respect)
        )
        self.robots[host] = robots
        return robots

    async def polite_fetch(
        self, url: str, *, etag: str | None = None, last_modified: str | None = None
    ) -> FetchResult:
        """Fetch with the host limiter, retries with backoff and `Retry-After`."""
        host = host_of(url)
        limiter = self.limiter(host)
        attempts = self.config.fetch.retries
        result = FetchResult(url=url, final_url=url, status=0, error="not attempted")
        for attempt in range(attempts):
            await limiter.acquire()
            try:
                result = await self.fetcher.fetch(url, etag=etag, last_modified=last_modified)
            finally:
                limiter.release()
            stats = self.report.host(host)
            retry = (
                result.error is not None
                or result.status in {HTTP_TOO_MANY, HTTP_UNAVAILABLE}
                or result.status >= HTTP_SERVER_ERROR
            )
            if not retry:
                return result
            delay = backoff_delay(attempt)
            after = retry_after_seconds(result.headers.get("retry-after"))
            if after is not None and result.status in {HTTP_TOO_MANY, HTTP_UNAVAILABLE}:
                delay = max(delay, min(after, 120.0))
                stats.retry_after_honored += 1
            if attempt + 1 < attempts:
                self.emitter.emit(
                    "host_backoff",
                    host=host,
                    url=url,
                    status=result.status,
                    delay_s=round(delay, 2),
                )
                limiter.pause_for(delay)
                await asyncio.sleep(delay)
        return result

    # -- discovery ---------------------------------------------------------------

    async def discover(self) -> None:
        """Seed the frontier: start URLs, sitemaps, llms.txt."""
        starts = self.config.site.start_urls or [self.config.site.root_url]
        with self.manifest.transaction():
            for url in starts:
                normalized = self.normalizer.normalize(url)
                self.manifest.enqueue(
                    normalized, depth=0, discovered_from=None, discovered_via="start", priority=100
                )
        for host in sorted(self.scope.allowed_hosts):
            robots = await self.robots_for(host)
            candidates = list(robots.sitemaps) + [
                f"{self.scheme}://{host}/{name}" for name in SITEMAP_CANDIDATES
            ]
            await self._walk_sitemaps(candidates, host)
            await self._llms_txt(host)

    async def _walk_sitemaps(self, candidates: list[str], host: str) -> None:
        seen: set[str] = set()
        queue = [c for c in candidates if host_of(c) == host]
        cap = self.config.scope.max_pages * 4
        children_budget = self.config.scope.sitemap_max_children
        found = 0
        while queue and found < cap:
            sitemap_url = queue.pop(0)
            if sitemap_url in seen:
                continue
            seen.add(sitemap_url)
            result = await self.polite_fetch(sitemap_url)
            if not result.ok or not result.body:
                continue
            children: list[str] = []
            with self.manifest.transaction():
                for entry in parse_sitemap(result.body):
                    if entry.is_index:
                        children.append(entry.loc)
                        continue
                    normalized = self.normalizer.normalize(entry.loc)
                    added = self.scope.in_scope(normalized, 1) and self.manifest.enqueue(
                        normalized,
                        depth=SITEMAP_DEPTH,
                        discovered_from=sitemap_url,
                        discovered_via="sitemap",
                        sitemap_lastmod=entry.lastmod,
                        priority=50,
                    )
                    if added:
                        found += 1
                    if found >= cap:
                        break
            if children:
                ranked = rank_child_sitemaps(children, self.scope.path_prefixes, self.scope.locale)
                chosen = [c for c in ranked if c not in seen][:children_budget]
                children_budget -= len(chosen)
                LOG.info(
                    "sitemap index %s: reading %d of %d children",
                    sitemap_url,
                    len(chosen),
                    len(children),
                )
                queue.extend(chosen)

    async def _llms_txt(self, host: str) -> None:
        result = await self.polite_fetch(f"{self.scheme}://{host}/llms.txt")
        if not result.ok or "text/html" in result.headers.get("content-type", ""):
            return
        with self.manifest.transaction():
            for url in parse_llms_txt(result.text(), f"{self.scheme}://{host}/"):
                normalized = self.normalizer.normalize(url)
                if self.scope.in_scope(normalized, 1):
                    self.manifest.enqueue(
                        normalized,
                        depth=1,
                        discovered_from=f"{self.scheme}://{host}/llms.txt",
                        discovered_via="llms.txt",
                        priority=40,
                    )

    # -- the loop ----------------------------------------------------------------

    async def run(self) -> ExitCode:
        """Run the whole crawl and return the exit code; the report is always written."""
        run_args = {"command": self.command, "resume": self.resume, "dry_run": self.dry_run}
        self.manifest.start_run(self.report.run_id, self.command, run_args)
        self.emitter.emit(
            "start", run_id=self.report.run_id, command=self.command, out_dir=str(self.out_dir)
        )
        exit_code = ExitCode.PARTIAL
        try:
            if not self.resume:
                self.manifest.frontier_bulk_status("in_progress", "pending")
            else:
                self.manifest.frontier_bulk_status("in_progress", "pending")
            if self.command == "update":
                self._requeue_known_pages()
            await self.discover()
            self.report.totals.discovered = self.manifest.frontier_count()
            if self.dry_run:
                for entry in self.manifest.frontier_rows():
                    via = entry.discovered_via
                    print(f"{entry.status:>8}  depth={entry.depth}  via={via}  {entry.url}")
                total = self.report.totals.discovered
                print(f"{total} URLs in the frontier (dry run; nothing fetched)")
                exit_code = ExitCode.OK
                return exit_code
            await self._loop()
            self._finish_pages()
            exit_code = self._final_exit_code()
        except (KeyboardInterrupt, asyncio.CancelledError):
            LOG.warning("interrupted; frontier state is consistent and --resume continues it")
            self.manifest.frontier_bulk_status("in_progress", "pending")
            exit_code = ExitCode.PARTIAL
        finally:
            for driver in self.drivers.values():
                with contextlib.suppress(Exception):
                    await driver.close()
            with contextlib.suppress(Exception):
                await self.fetcher.close()
            report = self.report.write(self.out_dir, int(exit_code))
            self.manifest.finish_run(self.report.run_id, int(exit_code), self.report.counts())
            self.emitter.emit(
                "done",
                run_id=self.report.run_id,
                exit_code=int(exit_code),
                totals=report.totals.model_dump(),
            )
        return exit_code

    def _final_exit_code(self) -> ExitCode:
        code = self.exit_code
        if self.report.totals.failed or self.report.totals.blocked:
            code = highest(code, ExitCode.PARTIAL)
        if any(h.breaker_tripped for h in self.report.hosts.values()):
            code = highest(code, ExitCode.BLOCKED)
        if self.config.report.fail_on_low_quality and self.report.totals.low_confidence:
            code = highest(code, ExitCode.QUALITY)
        return code

    def _requeue_known_pages(self) -> None:
        """Queue every written page for a re-check: conditional GET, or a full fetch when forced."""
        max_age = self.config.update.max_age_delta
        now = datetime.now(tz=UTC)
        with self.manifest.transaction():
            for row in self.manifest.pages(written_only=True):
                url = str(row["normalized_url"])
                forced = False
                if max_age is not None and row["last_seen"]:
                    seen = datetime.strptime(str(row["last_seen"]), "%Y-%m-%dT%H:%M:%SZ").replace(
                        tzinfo=UTC
                    )
                    forced = now - seen > max_age
                self.manifest.enqueue(
                    url, depth=0, discovered_from=None, discovered_via="recheck", priority=90
                )
                self.manifest.frontier_set_status(url, "pending")
                if forced:
                    self.must_fetch.add(url)

    def _written_total(self) -> int:
        return len(self.manifest.pages(written_only=True))

    async def _loop(self) -> None:
        concurrency = max(
            1, self.config.fetch.concurrency_per_host * max(1, len(self.scope.allowed_hosts))
        )
        while not self._stop:
            if self.bytes_total >= self.config.scope.max_bytes_int:
                self.manifest.frontier_bulk_status("pending", "skipped_limit")
                break
            remaining = self.config.scope.max_pages - self._written_total()
            batch = self.manifest.frontier_pending(concurrency * 4)
            if not batch:
                break
            batch = [entry for entry in batch if not self.breaker(host_of(entry.url)).tripped]
            if not batch:
                self.manifest.frontier_bulk_status("pending", "skipped_blocked")
                break
            known = {str(r["normalized_url"]) for r in self.manifest.pages(written_only=True)}
            chosen: list[FrontierEntry] = []
            for entry in batch:
                if entry.url in known:
                    chosen.append(entry)
                elif remaining > 0:
                    chosen.append(entry)
                    remaining -= 1
                if len(chosen) >= concurrency:
                    break
            if not chosen:
                self.manifest.frontier_bulk_status("pending", "skipped_limit")
                break
            batch = chosen
            shallowest = batch[0].depth
            if shallowest == 0:
                # Start pages go alone, so their links are queued before anything deeper.
                batch = [entry for entry in batch if entry.depth == 0]
            with self.manifest.transaction():
                for entry in batch:
                    self.manifest.frontier_set_status(entry.url, "in_progress")
            await asyncio.gather(
                *(
                    self._handle(
                        entry.url, entry.depth, entry.discovered_via, entry.sitemap_lastmod
                    )
                    for entry in batch
                )
            )

    async def _handle(
        self, url: str, depth: int, via: str | None, sitemap_lastmod: str | None
    ) -> None:
        host = host_of(url)
        breaker = self.breaker(host)
        if breaker.tripped:
            self.manifest.frontier_set_status(url, "skipped_blocked")
            return
        robots = await self.robots_for(host)
        if not robots.allows(url):
            self.manifest.frontier_set_status(url, "skipped_robots")
            self.emitter.emit(
                "page",
                url=url,
                path=None,
                status="skipped_robots",
                tier=None,
                quality_score=None,
                flags=[],
            )
            return
        known = self.manifest.get_page(url)
        etag, last_modified = self._conditional_headers(url, known, sitemap_lastmod)
        outcome = await self.ladder.fetch(
            url, host_tier=breaker.tier, etag=etag, last_modified=last_modified
        )
        result = outcome.result
        stats = self.report.host(host)
        stats.tiers_used.add(outcome.tier)
        if outcome.escalated:
            stats.render_escalations += 1
        if result.error is not None or result.status == 0:
            self._fail(url, result.error or "no response", self.config.fetch.retries)
            return
        self.bytes_total += len(result.body)
        if result.not_modified and known is not None:
            self._unchanged(url, known, outcome.tier)
            return
        if result.status in {HTTP_NOT_FOUND, HTTP_GONE}:
            self._tombstone(url, result.status, known)
            return
        verdict = outcome.verdict
        if verdict.blocked and verdict.kind != "soft":
            self._blocked(url, outcome)
            return
        if not result.ok:
            self._fail(url, f"http {result.status}", 1)
            return
        stats.fetched += 1
        self.fetched_pages += 1
        self.report.totals.fetched += 1
        raw_sha = body_sha256(result.text())
        if known is not None and known["status"] == "written" and known["raw_sha256"] == raw_sha:
            self._unchanged(url, known, outcome.tier)
            return
        content_type = result.headers.get("content-type", "")
        if content_type and "html" not in content_type and "xml" not in content_type:
            self.manifest.frontier_set_status(url, "skipped_not_html")
            self.emitter.emit(
                "page",
                url=url,
                path=None,
                status="skipped_not_html",
                tier=outcome.tier,
                quality_score=None,
                flags=[],
            )
            return
        try:
            page = await asyncio.to_thread(
                process_page, result.text(), result.final_url, self.config, self.profile
            )
        except Exception as error:
            LOG.exception("processing %s failed", url)
            self._fail(url, f"{type(error).__name__}: {error}", 1)
            return
        self.text_lengths.setdefault(host, []).append(page.text_chars)
        if outcome.render_needed and outcome.tier == "http":
            page.flags.add("render_needed")
        if verdict.kind == "soft":
            page.flags.add("soft_block_suspected")
        self._store(url, result, page, depth, via, sitemap_lastmod, tier=outcome.tier)

    def _conditional_headers(
        self, url: str, known: sqlite3.Row | None, sitemap_lastmod: str | None
    ) -> tuple[str | None, str | None]:
        """`If-None-Match` and `If-Modified-Since` for a known page, unless a fetch is forced.

        A page is fetched unconditionally when `--max-age` forced it, or when the sitemap's
        `lastmod` is newer than the one stored.
        """
        if known is None or known["status"] != "written" or url in self.must_fetch:
            return None, None
        stored = known["sitemap_lastmod"]
        if sitemap_lastmod and stored and str(sitemap_lastmod) > str(stored):
            return None, None
        return known["etag"], known["last_modified"]

    def _unchanged(self, url: str, known: sqlite3.Row, tier: str) -> None:
        self.manifest.upsert_page(url, last_seen=now_iso())
        self.manifest.frontier_set_status(url, "unchanged")
        self.report.totals.skipped_unchanged += 1
        self.report.changes.unchanged.append(str(known["path"]))
        # The quality summary describes the mirror, not the run: an unchanged page
        # keeps the score it was measured with, so an update that converts nothing
        # still reports the mean and the low-confidence pages the mirror holds.
        flags: list[str] = json.loads(known["flags_json"] or "[]")
        if known["quality_score"] is not None:
            self.report.record_quality(
                str(known["path"]),
                float(known["quality_score"]),
                [flag for flag in flags if flag in GATE_NAMES],
                flags,
                low_confidence=bool(known["low_confidence"]),
            )
        self.emitter.emit(
            "page",
            url=url,
            path=known["path"],
            status="unchanged",
            tier=tier,
            quality_score=known["quality_score"],
            flags=flags,
        )

    def _blocked(self, url: str, outcome: LadderOutcome) -> None:
        stats = self.report.host(host_of(url))
        stats.blocked += 1
        self.report.totals.blocked += 1
        self.report.blocked_urls.append(
            BlockedUrl(
                url=url,
                status=outcome.result.status,
                signature=outcome.verdict.signature,
                tier=outcome.tier,
            )
        )
        self.manifest.frontier_set_status(url, "blocked")
        self.emitter.emit(
            "page",
            url=url,
            path=None,
            status="blocked",
            tier=outcome.tier,
            quality_score=None,
            flags=[],
        )

    def _record_outcome(self, host: str, tier: str, blocked: bool) -> None:  # noqa: FBT001 - the outcome is the argument
        """Feed the breaker with one tier attempt; pause, slow and escalate, or trip."""
        del tier
        self.report.host(host).outcomes.append(blocked)
        breaker = self.breaker(host)
        action = breaker.record(blocked=blocked)
        limiter = self.limiter(host)
        if action == "escalate":
            limiter.halve_rate()
            limiter.pause_for(self.config.antibot.pause_s)
            self.emitter.emit(
                "host_backoff",
                host=host,
                reason="block rate",
                block_rate=round(breaker.block_rate, 3),
                pause_s=self.config.antibot.pause_s,
                tier=breaker.tier,
            )
            LOG.warning(
                "%s: block rate %.0f%%, pausing %.0fs and escalating to %s",
                host,
                breaker.block_rate * 100,
                self.config.antibot.pause_s,
                breaker.tier,
            )
        elif action == "trip":
            self.report.host(host).breaker_tripped = True
            skipped = self.manifest.frontier_bulk_status("pending", "skipped_blocked", host=host)
            self.emitter.emit(
                "breaker_tripped",
                host=host,
                block_rate=round(breaker.block_rate, 3),
                skipped=skipped,
            )
            LOG.error("%s: circuit breaker tripped; %d pending URLs skipped", host, skipped)

    def _fail(self, url: str, error: str, attempts: int, *, blocked: bool = False) -> None:
        self.manifest.frontier_set_status(url, "blocked" if blocked else "failed")
        self.report.totals.failed += 1
        self.report.failed_urls.append(FailedUrl(url=url, error=error, attempts=attempts))
        self.report.changes.failed.append(url)
        self.emitter.emit(
            "page",
            url=url,
            path=None,
            status="blocked" if blocked else "failed",
            tier="http",
            quality_score=None,
            flags=[],
        )

    def _tombstone(self, url: str, status: int, known: sqlite3.Row | None) -> None:
        self.manifest.frontier_set_status(url, "gone")
        if known is None or not known["path"]:
            self.emitter.emit(
                "page", url=url, path=None, status="gone", tier="http", quality_score=None, flags=[]
            )
            return
        from docmirror.state.tombstones import tombstone  # noqa: PLC0415

        tombstone(self, url, status, known)

    def _store(
        self,
        url: str,
        result: FetchResult,
        page: ProcessedPage,
        depth: int,
        via: str | None,
        sitemap_lastmod: str | None,
        *,
        tier: str = "http",
    ) -> None:
        identity = url
        final_normalized = self.normalizer.normalize(result.final_url)
        if final_normalized != url:
            self.manifest.add_alias(url, final_normalized)
            if self.scope.in_scope(final_normalized, depth):
                identity = final_normalized
                self.manifest.upsert_page(url, redirect_to=identity)
        if page.canonical_url:
            canonical = self.normalizer.normalize(page.canonical_url)
            if canonical != identity and self.scope.in_scope(canonical, depth):
                self.manifest.add_alias(identity, canonical)
                identity = canonical
        existing = self.manifest.get_page(identity)
        old_row = self.manifest.get_page(url) if identity != url else None
        if existing is not None and existing["path"]:
            path = str(existing["path"])
        elif old_row is not None and old_row["path"] and old_row["status"] == "written":
            # A page that moved keeps its path: the old URL becomes an alias of the new
            # identity and the file stays where every inbound link already points.
            path = str(old_row["path"])
            self.manifest.upsert_page(url, path=None, status="redirected", redirect_to=identity)
            existing = old_row
        else:
            path = self.mapper.assign(identity, self.manifest.path_taken)
        if identity != url:
            self.manifest.frontier_set_status(url, "alias")
        if path in self.written_paths:
            self.manifest.frontier_set_status(url, "duplicate")
            self.emitter.emit(
                "page",
                url=url,
                path=path,
                status="duplicate",
                tier="http",
                quality_score=None,
                flags=[],
            )
            return
        body = page.markdown_body
        fetched_at = now_iso()
        flags = sorted(page.flags | set(page.quality_failed))
        # A gate failure, or a flag that says the content is known to be incomplete,
        # makes the page low-confidence.
        low_confidence = bool(page.quality_failed) or bool(set(flags) & INCOMPLETE_FLAGS)
        version = self.mapper.version_of(identity)
        locale = self.config.site.locale or locale_segment(urlsplit(identity).path) or None
        frontmatter: dict[str, Any] = {
            "breadcrumbs": page.breadcrumbs or None,
            "canonical_url": page.canonical_url,
            "converter": CONVERTER_NAMES[self.config.convert.backend],
            "description": page.description or None,
            "etag": result.headers.get("etag"),
            "extractor": page.extractor,
            "last_modified": iso_timestamp(
                page.last_updated or result.headers.get("last-modified")
            ),
            "locale": locale,
            "low_confidence": low_confidence,
            "profile": self.config.site.profile,
            "quality_flags": flags,
            "quality_score": page.quality_score,
            "render": tier,
            "sitemap_lastmod": sitemap_lastmod,
            "source_url": result.final_url,
            "title": page.title,
            "version": version,
        }
        self._write_page(identity, path, body, frontmatter, fetched_at, existing)
        with self.manifest.transaction():
            self.manifest.upsert_page(
                identity,
                canonical_url=page.canonical_url,
                path=path,
                title=page.title,
                status="written",
                http_status=result.status,
                etag=result.headers.get("etag"),
                last_modified=result.headers.get("last-modified"),
                sitemap_lastmod=sitemap_lastmod,
                raw_sha256=body_sha256(result.text()),
                redirect_to=None,
                render_tier=tier,
                extractor=page.extractor,
                quality_score=page.quality_score,
                low_confidence=int(low_confidence),
                flags=flags,
                last_seen=fetched_at,
                discovered_via=via,
                description=page.description,
                headings=page.headings,
                version=version,
                locale=locale,
                word_count=page.word_count,
                tombstoned_at=None,
            )
            self.manifest.replace_anchors(identity, page.anchors)
            self.manifest.frontier_set_status(url, "done")
            self._enqueue_links(identity, page, depth)
        self.written_paths.add(path)
        self.report.totals.converted += 1
        self.report.record_quality(
            path, page.quality_score, page.quality_failed, flags, low_confidence=low_confidence
        )
        self.emitter.emit(
            "page",
            url=identity,
            path=path,
            status="written",
            tier=tier,
            quality_score=page.quality_score,
            flags=flags,
        )

    def _write_page(
        self,
        identity: str,
        path: str,
        body: str,
        frontmatter: dict[str, Any],
        fetched_at: str,
        existing: sqlite3.Row | None,
    ) -> None:
        """Write the page unless its pre-rewrite body is unchanged since the last run."""
        prewrite = body_sha256(body)
        previous = existing["prewrite_sha256"] if existing is not None else None
        target = self.out_dir / path
        if previous == prewrite and target.is_file():
            self.manifest.upsert_page(identity, last_seen=fetched_at)
            self.report.changes.unchanged.append(path)
            self.report.totals.skipped_unchanged += 1
            return
        keywords = None
        if existing is not None and existing["frontmatter_json"]:
            keywords = json.loads(existing["frontmatter_json"]).get("keywords")
        frontmatter = {
            **frontmatter,
            "content_sha256": prewrite,
            "fetched_at": fetched_at,
            "keywords": keywords or None,
        }
        atomic_write_text(target, render_frontmatter(frontmatter) + "\n" + body)
        self.manifest.upsert_page(
            identity,
            prewrite_sha256=prewrite,
            content_sha256=prewrite,
            fetched_at=fetched_at,
            last_changed=fetched_at,
            frontmatter=frontmatter,
        )
        if previous is None:
            self.report.changes.added.append(path)
        else:
            self.report.changes.changed.append(path)

    def _enqueue_links(self, identity: str, page: ProcessedPage, depth: int) -> None:
        rows: list[tuple[str, str, str, str | None]] = []
        for raw, _kind in page.links:
            normalized, fragment = self.normalizer.split_fragment(raw)
            if normalized == identity:
                continue
            if self.scope.in_scope(normalized, depth + 1):
                self.manifest.enqueue(
                    normalized, depth=depth + 1, discovered_from=identity, discovered_via="link"
                )
                rows.append((normalized, fragment, "internal", None))
            elif self.scope.host_allowed(normalized):
                rows.append((normalized, fragment, "uncrawled", None))
            else:
                rows.append((normalized, fragment, "external", None))
        self.manifest.replace_links(identity, rows)

    def _finish_pages(self) -> None:
        """Post-passes once every page is known: link rewriting and indexes (later phases)."""
        from docmirror.index.writers import write_indexes  # noqa: PLC0415
        from docmirror.links.rewriter import rewrite_all  # noqa: PLC0415

        rewrite_all(self)
        write_indexes(self.config, self.out_dir, self.manifest, self.report)


def iso_timestamp(value: str | None) -> str | None:
    """An ISO-8601 UTC timestamp from an HTTP date or an ISO string; other text unchanged.

    >>> iso_timestamp("Fri, 09 Oct 2026 18:35:12 GMT")
    '2026-10-09T18:35:12Z'
    """
    if not value:
        return None
    from datetime import UTC, datetime  # noqa: PLC0415
    from email.utils import parsedate_to_datetime  # noqa: PLC0415

    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        parsed = None
    if parsed is None:
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return value
    if parsed.tzinfo is None:
        return parsed.strftime("%Y-%m-%dT%H:%M:%SZ")
    return parsed.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _directory(url: str) -> str:
    parts = urlsplit(url)
    path = parts.path or "/"
    if not path.endswith("/"):
        path = path.rsplit("/", 1)[0] + "/"
    return path


def absolute(base: str, href: str) -> str:
    """Resolve `href` against `base` (helper for callers outside lxml)."""
    return urljoin(base, href)


def strip_fragment(url: str) -> str:
    """`url` without its fragment."""
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))
