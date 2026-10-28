"""Per-host token bucket with jitter, concurrency cap, pauses and backoff."""

from __future__ import annotations

import asyncio
import random
import time
from email.utils import parsedate_to_datetime

MAX_BACKOFF_S = 16.0


def backoff_delay(attempt: int, *, rng: random.Random | None = None) -> float:
    """Exponential backoff with jitter: 1 s, 2 s, 4 s ... capped, ±25%.

    >>> 0.75 <= backoff_delay(0, rng=random.Random(1)) <= 1.25
    True
    """
    base = min(2.0**attempt, MAX_BACKOFF_S)
    return base * _jitter(rng)


def _jitter(rng: random.Random | None) -> float:
    generator = rng if rng is not None else random
    return 1.0 + generator.uniform(-0.25, 0.25)


def retry_after_seconds(value: str | None, *, now: float | None = None) -> float | None:
    """Seconds to wait from a `Retry-After` header, which is a delay or an HTTP date.

    >>> retry_after_seconds("7")
    7.0
    >>> retry_after_seconds("nonsense") is None
    True
    """
    if value is None:
        return None
    text = value.strip()
    if text.isdigit():
        return float(text)
    try:
        when = parsedate_to_datetime(text)
    except (TypeError, ValueError):
        return None
    current = time.time() if now is None else now
    return max(0.0, when.timestamp() - current)


class HostLimiter:
    """A token bucket plus semaphore for one host.

    `rate` tokens per second refill the bucket up to `burst`; `concurrency` requests may
    be in flight. `pause_for` blocks every caller for a while, and `halve_rate` slows the
    host after blocks.
    """

    def __init__(self, rate: float, concurrency: int, *, crawl_delay: float | None = None) -> None:
        """Create a limiter honouring a robots `Crawl-delay` when it is slower than `rate`."""
        effective = rate
        if crawl_delay is not None and crawl_delay > 0:
            effective = min(rate, 1.0 / crawl_delay)
        self.rate = effective
        self.burst = max(1.0, float(concurrency))
        self._tokens = self.burst
        self._updated = time.monotonic()
        self._semaphore = asyncio.Semaphore(concurrency)
        self._paused_until = 0.0
        self._lock = asyncio.Lock()

    def halve_rate(self) -> None:
        """Slow the host down after a burst of blocks."""
        self.rate = max(self.rate / 2.0, 0.05)

    def pause_for(self, seconds: float) -> None:
        """Hold every request on this host for `seconds`."""
        self._paused_until = max(self._paused_until, time.monotonic() + seconds)

    async def acquire(self) -> None:
        """Wait for a token and a concurrency slot."""
        await self._semaphore.acquire()
        try:
            while True:
                async with self._lock:
                    now = time.monotonic()
                    wait = self._paused_until - now
                    if wait <= 0:
                        self._tokens = min(
                            self.burst, self._tokens + (now - self._updated) * self.rate
                        )
                        self._updated = now
                        if self._tokens >= 1.0:
                            self._tokens -= 1.0
                            return
                        wait = (1.0 - self._tokens) / self.rate
                await asyncio.sleep(max(wait, 0.01) * _jitter(None))
        except BaseException:
            self._semaphore.release()
            raise

    def release(self) -> None:
        """Give the concurrency slot back."""
        self._semaphore.release()
