"""Tier 0: curl_cffi with browser impersonation, one persistent session per host."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from curl_cffi import requests as curl_requests

from docmirror import __version__
from docmirror.frontier.urls import host_of

if TYPE_CHECKING:
    from collections.abc import Mapping

LOG = logging.getLogger("docmirror.fetch")
DEFAULT_USER_AGENT = f"docmirror/{__version__} (+https://github.com/BiscuitBin/alliumpy)"


@dataclass(slots=True)
class FetchResult:
    """What one fetch produced, whatever the tier."""

    url: str
    final_url: str
    status: int
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    tier: str = "http"
    elapsed_s: float = 0.0
    error: str | None = None
    cookies: dict[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        """Whether the fetch returned a 2xx response."""
        return self.error is None and 200 <= self.status < 300  # noqa: PLR2004 - HTTP classes

    @property
    def not_modified(self) -> bool:
        """Whether a conditional request answered 304."""
        return self.status == 304  # noqa: PLR2004 - HTTP status

    def text(self) -> str:
        """The body decoded with the response charset, falling back to UTF-8."""
        content_type = self.headers.get("content-type", "")
        charset = "utf-8"
        if "charset=" in content_type:
            charset = (
                content_type.split("charset=", 1)[1].split(";", 1)[0].strip().strip('"') or "utf-8"
            )
        try:
            return self.body.decode(charset, errors="replace")
        except LookupError:
            return self.body.decode("utf-8", errors="replace")


class HttpFetcher:
    """curl_cffi sessions keyed by host, with impersonation and cookie persistence."""

    def __init__(
        self,
        *,
        impersonate: str = "chrome",
        user_agent: str = "",
        timeout_s: float = 30.0,
        locale: str = "",
    ) -> None:
        """Configure the fetcher; sessions are created lazily per host."""
        self.impersonate = impersonate or None
        self.user_agent = user_agent or (DEFAULT_USER_AGENT if not impersonate else "")
        self.timeout_s = timeout_s
        self.locale = locale
        self._sessions: dict[str, curl_requests.AsyncSession[Any]] = {}
        self._lock = asyncio.Lock()

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self.user_agent:
            headers["User-Agent"] = self.user_agent
        if self.locale:
            headers["Accept-Language"] = f"{self.locale},{self.locale.split('-')[0]};q=0.8,en;q=0.5"
        return headers

    async def session_for(self, host: str) -> curl_requests.AsyncSession[Any]:
        """The persistent session for `host`, created on first use."""
        async with self._lock:
            session = self._sessions.get(host)
            if session is None:
                kwargs: dict[str, Any] = {"timeout": self.timeout_s, "headers": self._headers()}
                if self.impersonate:
                    kwargs["impersonate"] = self.impersonate
                session = curl_requests.AsyncSession(**kwargs)
                self._sessions[host] = session
            return session

    def set_cookies(self, host: str, cookies: Mapping[str, str]) -> None:
        """Copy cookies a browser tier collected into the host's HTTP session."""
        session = self._sessions.get(host)
        if session is None:
            kwargs: dict[str, Any] = {"timeout": self.timeout_s, "headers": self._headers()}
            if self.impersonate:
                kwargs["impersonate"] = self.impersonate
            session = curl_requests.AsyncSession(**kwargs)
            self._sessions[host] = session
        for name, value in cookies.items():
            session.cookies.set(name, value, domain=host)

    async def fetch(
        self,
        url: str,
        *,
        etag: str | None = None,
        last_modified: str | None = None,
        extra_headers: Mapping[str, str] | None = None,
    ) -> FetchResult:
        """One GET, following redirects, with optional conditional headers."""
        host = host_of(url)
        session = await self.session_for(host)
        headers: dict[str, str] = dict(extra_headers or {})
        if etag:
            headers["If-None-Match"] = etag
        if last_modified:
            headers["If-Modified-Since"] = last_modified
        started = time.monotonic()
        try:
            response = await session.get(url, headers=headers or None, allow_redirects=True)
        except Exception as error:  # noqa: BLE001 - every transport failure is one outcome
            LOG.debug("fetch %s failed: %s", url, error)
            return FetchResult(
                url=url,
                final_url=url,
                status=0,
                error=f"{type(error).__name__}: {error}",
                elapsed_s=time.monotonic() - started,
            )
        lowered = {str(k).lower(): str(v) for k, v in response.headers.items()}
        cookies = {c.name: c.value for c in session.cookies.jar if c.value is not None}
        return FetchResult(
            url=url,
            final_url=str(response.url),
            status=int(response.status_code),
            headers=lowered,
            body=bytes(response.content),
            elapsed_s=time.monotonic() - started,
            cookies=cookies,
        )

    async def close(self) -> None:
        """Close every session."""
        for session in self._sessions.values():
            await session.close()
        self._sessions.clear()
