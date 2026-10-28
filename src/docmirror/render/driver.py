"""Tier 1 (Patchright, Chromium) and Tier 2 (Camoufox, Firefox) page renderers.

Each driver keeps one persistent browser context per host under
`<out>/.docmirror/browser/<host>/`, waits for the configured load state with a cap, and
returns the rendered `page.content()` with the cookies the context holds, so the HTTP
tier can reuse them.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

from docmirror.fetch.session import FetchResult
from docmirror.frontier.urls import host_of

if TYPE_CHECKING:
    from docmirror.config.models import Render

LOG = logging.getLogger("docmirror.render")


class BrowserDriver(Protocol):
    """What a browser tier provides."""

    tier: str

    async def fetch(self, url: str) -> FetchResult:
        """Render one page and return its HTML as a fetch result."""

    async def close(self) -> None:
        """Close every browser context."""


class _PlaywrightDriver:
    """Shared machinery for the Playwright-compatible drivers."""

    tier = "browser"
    browser_dir_name = "chromium"

    def __init__(self, state_dir: Path, render: Render, *, locale: str = "") -> None:
        """Remember where contexts live and how long to wait."""
        self.state_dir = state_dir
        self.render = render
        self.locale = locale
        self._playwright: Any = None
        self._contexts: dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def _start(self) -> Any:  # noqa: ANN401 - playwright object
        raise NotImplementedError

    async def _launch(self, playwright: Any, user_data_dir: Path) -> Any:  # noqa: ANN401
        raise NotImplementedError

    async def _context_for(self, host: str) -> Any:  # noqa: ANN401 - playwright context
        async with self._lock:
            context = self._contexts.get(host)
            if context is None:
                if self._playwright is None:
                    self._playwright = await self._start()
                user_data_dir = self.state_dir / "browser" / self.browser_dir_name / host
                user_data_dir.mkdir(parents=True, exist_ok=True)
                context = await self._launch(self._playwright, user_data_dir)
                self._contexts[host] = context
            return context

    async def fetch(self, url: str) -> FetchResult:
        """Navigate, wait, and return the rendered document."""
        host = host_of(url)
        started = time.monotonic()
        try:
            context = await self._context_for(host)
            page = await context.new_page()
            try:
                response = await page.goto(
                    url, wait_until=self.render.wait_until, timeout=self.render.max_wait_s * 1000
                )
                status = int(response.status) if response is not None else 0
                headers = (
                    {k.lower(): v for k, v in (await response.all_headers()).items()}
                    if response is not None
                    else {}
                )
                final_url = str(page.url)
                content = await page.content()
            finally:
                await page.close()
            cookies = {c["name"]: c["value"] for c in await context.cookies()}
        except Exception as error:  # noqa: BLE001 - every driver failure is one outcome
            LOG.debug("%s render of %s failed: %s", self.tier, url, error)
            return FetchResult(
                url=url,
                final_url=url,
                status=0,
                tier=self.tier,
                error=f"{type(error).__name__}: {error}",
                elapsed_s=time.monotonic() - started,
            )
        return FetchResult(
            url=url,
            final_url=final_url,
            status=status or 200,
            headers={
                **headers,
                "content-type": headers.get("content-type", "text/html; charset=utf-8"),
            },
            body=content.encode("utf-8"),
            tier=self.tier,
            elapsed_s=time.monotonic() - started,
            cookies=cookies,
        )

    async def close(self) -> None:
        """Close contexts and stop the driver."""
        for context in self._contexts.values():
            with contextlib.suppress(Exception):
                await context.close()
        self._contexts.clear()
        if self._playwright is not None:
            with contextlib.suppress(Exception):
                await self._playwright.stop()
            self._playwright = None


class PatchrightDriver(_PlaywrightDriver):
    """Tier 1: Patchright's Chromium, headless, with a persistent profile per host."""

    tier = "browser"
    browser_dir_name = "chromium"

    async def _start(self) -> Any:  # noqa: ANN401
        from patchright.async_api import async_playwright  # noqa: PLC0415

        return await async_playwright().start()

    async def _launch(self, playwright: Any, user_data_dir: Path) -> Any:  # noqa: ANN401
        return await playwright.chromium.launch_persistent_context(
            user_data_dir,
            headless=True,
            locale=self.locale or None,
            viewport={"width": 1280, "height": 900},
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )


class CamoufoxDriver(_PlaywrightDriver):
    """Tier 2: Camoufox's Firefox, when the optional extra is installed."""

    tier = "stealth"
    browser_dir_name = "firefox"

    async def _start(self) -> Any:  # noqa: ANN401
        from camoufox.async_api import AsyncCamoufox  # noqa: PLC0415

        self._camoufox = AsyncCamoufox(headless=True, persistent_context=False)
        return await self._camoufox.__aenter__()

    async def _launch(self, playwright: Any, user_data_dir: Path) -> Any:  # noqa: ANN401
        del user_data_dir
        return await playwright.new_context(locale=self.locale or None)

    async def close(self) -> None:
        """Close contexts and the Camoufox browser."""
        for context in self._contexts.values():
            with contextlib.suppress(Exception):
                await context.close()
        self._contexts.clear()
        camoufox = getattr(self, "_camoufox", None)
        if camoufox is not None:
            with contextlib.suppress(Exception):
                await camoufox.__aexit__(None, None, None)
        self._playwright = None


def camoufox_available() -> bool:
    """Whether the optional Camoufox extra is importable."""
    try:
        import camoufox  # noqa: F401, PLC0415
    except ImportError:
        return False
    return True


def driver_for(
    tier: str, state_dir: Path, render: Render, *, locale: str = ""
) -> BrowserDriver | None:
    """A driver for `browser` or `stealth`, or None when the tier is unavailable."""
    if tier == "browser":
        return PatchrightDriver(state_dir, render, locale=locale)
    if tier == "stealth" and camoufox_available():
        return CamoufoxDriver(state_dir, render, locale=locale)
    return None
