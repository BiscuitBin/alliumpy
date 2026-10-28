"""Capture live pages as golden fixtures: `tests/fixtures/<profile>/<slug>/page.html` + `url.txt`.

Usage: `python scripts/capture_fixtures.py <profile> <url>...` from the repository root.
The slug is derived from the URL path and query; an existing fixture is overwritten
only with `--force`, so a re-run never silently moves a golden snapshot. Each host's
robots.txt is read first: a disallowed URL is skipped, and requests to one host are
spaced by its `Crawl-delay`, never less than `MIN_DELAY_S`.
"""

from __future__ import annotations

import asyncio
import re
import sys
import time
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

from docmirror.fetch.session import FetchResult, HttpFetcher
from docmirror.frontier.robots import Robots

ROOT = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
MIN_PAGE_BYTES = 1000
MIN_ARGS = 2
MIN_DELAY_S = 0.6


def slug_for(url: str) -> str:
    """A filesystem-safe name from the URL's path and meaningful query."""
    parts = urlsplit(url)
    segments = [s for s in parts.path.split("/") if s and not re.fullmatch(r"[a-z]{2}-[a-z]{2}", s)]
    text = "-".join(segments[-3:]) if segments else "index"
    query = sorted(parse_qsl(parts.query))
    if query:
        text += "-" + "-".join(f"{key}-{value}" for key, value in query)
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-").lower()
    return text[:80] or "index"


async def capture(profile: str, urls: list[str], *, force: bool) -> int:
    """Fetch every URL and write its fixture directory."""
    fetcher = HttpFetcher(impersonate="chrome", timeout_s=60.0, locale="en-us")
    agent = fetcher.user_agent or "docmirror"
    robots: dict[str, Robots] = {}
    last_request: dict[str, float] = {}

    async def polite_fetch(url: str, host: str, delay: float) -> FetchResult:
        wait = last_request.get(host, float("-inf")) + delay - time.monotonic()
        if wait > 0:
            await asyncio.sleep(wait)
        try:
            return await fetcher.fetch(url)
        finally:
            last_request[host] = time.monotonic()

    failures = 0
    try:
        for url in urls:
            target = ROOT / profile / slug_for(url)
            if target.exists() and not force:
                print(f"skip (exists): {target}")
                continue
            parts = urlsplit(url)
            host = parts.netloc
            if host not in robots:
                answer = await polite_fetch(f"{parts.scheme}://{host}/robots.txt", host, 0.0)
                robots[host] = (
                    Robots.parse(answer.text(), agent) if answer.ok else Robots.absent(agent)
                )
            if not robots[host].allows(url):
                print(f"skip (robots): {url}")
                continue
            delay = max(robots[host].crawl_delay() or 0.0, MIN_DELAY_S)
            result = await polite_fetch(url, host, delay)
            if not result.ok or len(result.body) < MIN_PAGE_BYTES:
                detail = f"status {result.status} {result.error or ''} ({len(result.body)} bytes)"
                print(f"FAIL {url}: {detail}")
                failures += 1
                continue
            target.mkdir(parents=True, exist_ok=True)
            (target / "page.html").write_bytes(result.body)
            (target / "url.txt").write_text(result.final_url + "\n", encoding="utf-8")
            print(f"ok   {target.relative_to(ROOT.parent.parent)}  ({len(result.body)} bytes)")
    finally:
        await fetcher.close()
    return failures


def main(argv: list[str]) -> int:
    """Parse arguments and capture."""
    force = "--force" in argv
    args = [a for a in argv if a != "--force"]
    if len(args) < MIN_ARGS:
        print(__doc__, file=sys.stderr)
        return 2
    profile, urls = args[0], args[1:]
    return 1 if asyncio.run(capture(profile, urls, force=force)) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
