"""Capture live pages as golden fixtures: `tests/fixtures/<profile>/<slug>/page.html` + `url.txt`.

Usage: `python scripts/capture_fixtures.py <profile> <url>...` from the repository root.
The slug is derived from the URL path; an existing fixture is overwritten only with
`--force`, so a re-run never silently moves a golden snapshot.
"""

from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

from docmirror.fetch.session import HttpFetcher

ROOT = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
MIN_PAGE_BYTES = 1000
MIN_ARGS = 2


def slug_for(url: str) -> str:
    """A filesystem-safe name from the URL's path and meaningful query."""
    parts = urlsplit(url)
    segments = [s for s in parts.path.split("/") if s and not re.fullmatch(r"[a-z]{2}-[a-z]{2}", s)]
    text = "-".join(segments[-3:]) if segments else "index"
    if "view=graph-rest-beta" in parts.query:
        text += "-beta"
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-").lower()
    return text[:80] or "index"


async def capture(profile: str, urls: list[str], *, force: bool) -> int:
    """Fetch every URL and write its fixture directory."""
    fetcher = HttpFetcher(impersonate="chrome", timeout_s=60.0, locale="en-us")
    failures = 0
    try:
        for url in urls:
            target = ROOT / profile / slug_for(url)
            if target.exists() and not force:
                print(f"skip (exists): {target}")
                continue
            result = await fetcher.fetch(url)
            if not result.ok or len(result.body) < MIN_PAGE_BYTES:
                detail = f"status {result.status} {result.error or ''} ({len(result.body)} bytes)"
                print(f"FAIL {url}: {detail}")
                failures += 1
                continue
            target.mkdir(parents=True, exist_ok=True)
            (target / "page.html").write_bytes(result.body)
            (target / "url.txt").write_text(result.final_url + "\n", encoding="utf-8")
            print(f"ok   {target.relative_to(ROOT.parent.parent)}  ({len(result.body)} bytes)")
            await asyncio.sleep(0.6)
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
