"""`docmirror fetch`: fetch and convert one page to stdout with the configured pipeline."""

from __future__ import annotations

import asyncio
import os
from collections.abc import Awaitable, Callable
from pathlib import Path

from lxml import etree

from docmirror.cli.common import LOG, Common, fail
from docmirror.config.loader import ConfigError, load_config, validate_config
from docmirror.config.models import Config
from docmirror.config.profiles import detect_profile
from docmirror.exit_codes import ExitCode
from docmirror.fetch.ladder import FetchLadder
from docmirror.fetch.session import FetchResult, HttpFetcher
from docmirror.pipeline import process_page
from docmirror.render.driver import BrowserDriver, driver_for


def _config(common: Common, url: str, profile: str | None) -> Config:
    if common.config_path is not None:
        try:
            config = load_config(common.config_path, environ=os.environ, overrides=common.overrides)
        except ConfigError as error:
            fail(str(error), ExitCode.USAGE)
    else:
        config = validate_config(
            {"site": {"profile": profile or detect_profile(url), "start_urls": [url]}}
        )
    if profile:
        config.site.profile = profile
    return config


async def _fetch(
    config: Config, url: str, tier: str | None, state_dir: Path
) -> tuple[str, str, str]:
    profile = config.profile()
    fetcher = HttpFetcher(
        impersonate=config.fetch.impersonate,
        user_agent=config.fetch.user_agent,
        timeout_s=config.fetch.timeout_s,
        locale=config.site.locale,
    )
    drivers: dict[str, BrowserDriver] = {}
    tiers: dict[str, Callable[..., Awaitable[FetchResult]]] = {"http": fetcher.fetch}
    for name in ("browser", "stealth"):
        driver = driver_for(name, state_dir, config.render, locale=config.site.locale)
        if driver is not None:
            drivers[name] = driver
            tiers[name] = driver.fetch
    cache: dict[tuple[str, str], str] = {}
    ladder = FetchLadder(
        config,
        profile,
        tiers,
        cached_tier=lambda h, p: cache.get((h, p)),
        cache_tier=lambda h, p, t: cache.__setitem__((h, p), t),
        median_text=lambda _: None,
    )
    try:
        if tier is not None:
            if tier not in tiers:
                message = f"tier {tier!r} is not available (choose from {', '.join(tiers)})"
                raise RuntimeError(message)
            result = await tiers[tier](url)
            used = tier
        else:
            outcome = await ladder.fetch(url)
            result = outcome.result
            used = outcome.tier
            if outcome.verdict.blocked:
                LOG.warning("blocked at tier %s: %s", used, outcome.verdict.signature)
    finally:
        for driver in drivers.values():
            await driver.close()
        await fetcher.close()
    if not result.ok:
        message = f"fetch failed: status {result.status} {result.error or ''}".strip()
        raise RuntimeError(message)
    page = process_page(result.text(), result.final_url, config, profile)
    from docmirror.extract import extract_page  # noqa: PLC0415

    extraction = extract_page(result.text(), result.final_url, profile)
    html_text = etree.tostring(extraction.content, encoding="unicode", method="html")
    LOG.info(
        "tier %s, extractor %s, quality %.2f, flags %s",
        used,
        page.extractor,
        page.quality_score,
        sorted(page.flags | set(page.quality_failed)),
    )
    return page.markdown_body, html_text, used


def run_fetch(
    url: str, common: Common, *, tier: str | None, dump_html: Path | None, profile: str | None
) -> ExitCode:
    """Fetch one page through the ladder (or a forced tier) and print its Markdown."""
    config = _config(common, url, profile)
    state_dir = Path(os.environ.get("DOCMIRROR_STATE_DIR", Path.home() / ".cache" / "docmirror"))
    try:
        markdown, html_text, used = asyncio.run(_fetch(config, url, tier, state_dir))
    except RuntimeError as error:
        fail(str(error), ExitCode.PARTIAL)
    if dump_html is not None:
        dump_html.write_text(html_text, encoding="utf-8")
    if common.json_events:
        common.emitter.emit("fetch", url=url, tier=used, markdown=markdown)
    else:
        print(markdown, end="")
    return ExitCode.OK
