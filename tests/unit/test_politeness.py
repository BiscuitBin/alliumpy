"""Backoff, Retry-After and the host limiter."""

from __future__ import annotations

import asyncio
import random
import time

from docmirror.fetch.politeness import HostLimiter, backoff_delay, retry_after_seconds


def test_backoff_grows_and_caps() -> None:
    rng = random.Random(7)  # noqa: S311 - deterministic jitter for the test
    delays = [backoff_delay(i, rng=rng) for i in range(6)]
    assert 0.75 <= delays[0] <= 1.25
    assert 1.5 <= delays[1] <= 2.5
    assert 3.0 <= delays[2] <= 5.0
    assert all(d <= 16 * 1.25 for d in delays)


def test_retry_after_forms() -> None:
    assert retry_after_seconds("3") == 3.0
    assert retry_after_seconds("Wed, 21 Oct 2015 07:28:00 GMT", now=1445412470.0) == 10.0
    assert retry_after_seconds("later") is None
    assert retry_after_seconds(None) is None


def test_limiter_paces_requests() -> None:
    async def scenario() -> float:
        limiter = HostLimiter(rate=20.0, concurrency=1)
        started = time.monotonic()
        for _ in range(4):
            await limiter.acquire()
            limiter.release()
        return time.monotonic() - started

    elapsed = asyncio.run(scenario())
    # One token is available at once; three refills at 20/s take about 150 ms.
    assert 0.08 <= elapsed <= 1.0


def test_limiter_pause_and_halve() -> None:
    async def scenario() -> float:
        limiter = HostLimiter(rate=100.0, concurrency=2, crawl_delay=0.005)
        limiter.halve_rate()
        limiter.pause_for(0.1)
        started = time.monotonic()
        await limiter.acquire()
        limiter.release()
        return time.monotonic() - started

    assert asyncio.run(scenario()) >= 0.09
