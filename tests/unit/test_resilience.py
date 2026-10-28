"""Block signatures, the circuit breaker, the ladder's escalation and exit 3."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from docmirror.config.loader import validate_config
from docmirror.exit_codes import ExitCode
from docmirror.fetch.blocks import classify
from docmirror.fetch.breaker import HostBreaker
from docmirror.fetch.ladder import FetchLadder
from docmirror.fetch.session import FetchResult
from docmirror.pipeline import Crawler
from docmirror.report.events import EventEmitter
from docmirror.report.models import CrawlReport
from docmirror.state.db import open_manifest

PAGE = "<html><body><main id='main'><h1>T</h1><p>" + "words " * 80 + "</p></main></body></html>"
SHELL = (
    '<html><body><div id="root"></div><noscript>Please enable JavaScript</noscript></body></html>'
    + " " * 6000
)


def test_block_signatures() -> None:
    assert classify(FetchResult("u", "u", 403, body=b"nope")).kind == "hard"
    assert classify(FetchResult("u", "u", 429)).signature == "http 429"
    challenge = FetchResult("u", "u", 503, body=b"<title>Just a moment...</title>")
    assert classify(challenge).kind == "hard"
    assert "Just a moment" in classify(challenge).signature
    header = FetchResult("u", "u", 200, headers={"cf-mitigated": "challenge"}, body=b"x")
    assert classify(header).kind == "challenge"
    denied = FetchResult("u", "u", 200, body=b"<h1>Access Denied</h1> Reference #18.3f")
    assert classify(denied).kind == "challenge"
    cookie = FetchResult("u", "u", 200, body=b"<p>tiny</p>", cookies={"__cf_bm": "x"})
    assert classify(cookie).kind == "challenge"
    big_cookie = FetchResult("u", "u", 200, body=b"x" * 5000, cookies={"__cf_bm": "x"})
    assert classify(big_cookie).kind == "none"
    soft = classify(
        FetchResult("u", "u", 200, body=b"<p>x</p>"), text_chars=10, median_text_chars=1000
    )
    assert soft.kind == "soft"
    assert classify(FetchResult("u", "u", 200, body=b"<p>x</p>"), login_wall=True).kind == "soft"
    assert classify(FetchResult("u", "u", 200, body=b"<p>fine</p>")).kind == "none"


def test_breaker_escalates_then_trips() -> None:
    breaker = HostBreaker(window=50, threshold=0.20, highest_tier="browser")
    actions = [breaker.record(blocked=i % 4 == 0) for i in range(50)]  # 25% blocked
    assert "escalate" in actions
    assert breaker.tier == "browser"
    assert not breaker.tripped
    actions = [breaker.record(blocked=i % 4 == 0) for i in range(50)]
    assert actions[-1] == "trip" or breaker.tripped
    assert breaker.tripped


def test_breaker_stays_calm_under_threshold() -> None:
    breaker = HostBreaker(window=50, threshold=0.20, highest_tier="browser")
    actions = {breaker.record(blocked=i % 10 == 0) for i in range(200)}  # 10% blocked
    assert actions == {"ok"}
    assert breaker.tier == "http"


def test_breaker_trips_at_once_when_no_higher_tier() -> None:
    breaker = HostBreaker(window=10, threshold=0.20, highest_tier="http")
    for _ in range(10):
        breaker.record(blocked=True)
    assert breaker.tripped


def _ladder(config_data: dict[str, object], tiers: dict[str, object]) -> FetchLadder:
    config = validate_config(config_data)
    cache: dict[tuple[str, str], str] = {}
    return FetchLadder(
        config,
        config.profile(),
        tiers,  # type: ignore[arg-type]
        cached_tier=lambda h, p: cache.get((h, p)),
        cache_tier=lambda h, p, t: cache.__setitem__((h, p), t),
        median_text=lambda _: None,
    )


def test_ladder_escalates_shell_to_browser_and_caches() -> None:
    calls: list[str] = []

    async def http(url: str, **_: object) -> FetchResult:
        calls.append("http")
        return FetchResult(
            url, url, 200, headers={"content-type": "text/html"}, body=SHELL.encode()
        )

    async def browser(url: str) -> FetchResult:
        calls.append("browser")
        return FetchResult(
            url, url, 200, headers={"content-type": "text/html"}, body=PAGE.encode(), tier="browser"
        )

    ladder = _ladder({"site": {"profile": "generic"}}, {"http": http, "browser": browser})
    outcome = asyncio.run(ladder.fetch("https://h/docs/api/a"))
    assert outcome.tier == "browser"
    assert outcome.escalated
    assert outcome.tiers_tried == ["http", "browser"]
    assert calls == ["http", "browser"]
    # The tier is cached by the first two path segments, so a sibling skips HTTP.
    second = asyncio.run(ladder.fetch("https://h/docs/api/b"))
    assert second.tiers_tried == ["browser"]


def test_ladder_render_never_flags_without_escalating() -> None:
    async def http(url: str, **_: object) -> FetchResult:
        return FetchResult(
            url, url, 200, headers={"content-type": "text/html"}, body=SHELL.encode()
        )

    async def browser(_url: str) -> FetchResult:
        pytest.fail("the browser tier must not be called")

    ladder = _ladder(
        {"site": {"profile": "generic"}, "render": {"mode": "never"}},
        {"http": http, "browser": browser},
    )
    outcome = asyncio.run(ladder.fetch("https://h/docs/a"))
    assert outcome.tier == "http"
    assert outcome.render_needed
    assert not outcome.escalated


def test_ladder_render_always_starts_in_browser() -> None:
    async def http(_url: str, **_: object) -> FetchResult:
        pytest.fail("the HTTP tier must not be called")

    async def browser(url: str) -> FetchResult:
        return FetchResult(
            url, url, 200, headers={"content-type": "text/html"}, body=PAGE.encode(), tier="browser"
        )

    ladder = _ladder(
        {"site": {"profile": "generic"}, "render": {"mode": "always"}},
        {"http": http, "browser": browser},
    )
    outcome = asyncio.run(ladder.fetch("https://h/docs/a"))
    assert outcome.tiers_tried == ["browser"]


def test_breaker_trips_and_exits_3_with_a_report(tmp_path: Path) -> None:
    out = tmp_path / "out"
    out.mkdir()
    (out / "docmirror.toml").write_text(
        '[site]\nroot_url = "https://blocked.example/docs/"\nstart_urls = ["https://blocked.example/docs/"]\nprofile = "generic"\n'
        '[scope]\nallowed_hosts = ["blocked.example"]\npath_prefixes = ["/docs/"]\nmax_pages = 200\n'
        "[fetch]\nrate_per_host = 1000\nretries = 1\n[antibot]\nwindow = 50\npause_s = 0\n"
    )
    config = validate_config(
        {
            "site": {
                "root_url": "https://blocked.example/docs/",
                "start_urls": ["https://blocked.example/docs/"],
            },
            "scope": {
                "allowed_hosts": ["blocked.example"],
                "path_prefixes": ["/docs/"],
                "max_pages": 200,
            },
            "fetch": {"rate_per_host": 1000, "retries": 1},
            "antibot": {"window": 50, "pause_s": 0},
        }
    )
    counter = {"n": 0}

    def body(index: int) -> str:
        links = "".join(f'<a href="/docs/p{index}-{j}">l</a>' for j in range(3))
        return (
            f"<html><body><main><h1>P{index}</h1><p>{'text ' * 60}</p>{links}</main></body></html>"
        )

    async def tier(url: str, **_: object) -> FetchResult:
        counter["n"] += 1
        if counter["n"] % 3 == 0:  # a third of every tier's answers are 403
            return FetchResult(
                url, url, 403, headers={"content-type": "text/html"}, body=b"forbidden"
            )
        return FetchResult(
            url, url, 200, headers={"content-type": "text/html"}, body=body(counter["n"]).encode()
        )

    async def robots(url: str, **_: object) -> FetchResult:
        return FetchResult(url, url, 404, body=b"")

    with open_manifest(out) as manifest:
        crawler = Crawler(config, out, manifest, EventEmitter(enabled=False), command="crawl")
        crawler.ladder.tiers = {"http": tier, "browser": tier}
        crawler.fetcher.fetch = robots  # type: ignore[method-assign]
        code = asyncio.run(crawler.run())
    assert code == ExitCode.BLOCKED
    report = CrawlReport.model_validate_json((out / "crawl-report.json").read_text())
    assert report.run.exit_code == 3
    host = report.per_host[0]
    assert host.breaker_tripped
    assert host.block_rate > 0.20
    assert "browser" in host.tiers_used
    assert report.totals.blocked > 0
    assert report.totals.converted > 0
    assert any(b.status == 403 for b in report.blocked_urls)
    with open_manifest(out) as manifest:
        assert manifest.frontier_count("skipped_blocked") > 0
