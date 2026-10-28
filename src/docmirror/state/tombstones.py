"""404/410 handling: tombstone the page and move its file to `_removed/`, or delete it."""

from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

from docmirror.state.db import now_iso

if TYPE_CHECKING:
    from docmirror.pipeline import Crawler

REMOVED_DIR = "_removed"


def tombstone(crawler: Crawler, url: str, status: int, known: sqlite3.Row) -> None:
    """Record the tombstone and move (or prune) the page file; inbound links are rewritten later."""
    path = str(known["path"])
    source = crawler.out_dir / path
    moved_to: str | None = None
    if source.is_file():
        if crawler.config.update.prune:
            source.unlink()
        else:
            target = crawler.out_dir / REMOVED_DIR / path
            target.parent.mkdir(parents=True, exist_ok=True)
            source.replace(target)
            moved_to = f"{REMOVED_DIR}/{path}"
    crawler.manifest.upsert_page(url, tombstoned_at=now_iso(), http_status=status, status="gone")
    crawler.report.changes.removed.append(path)
    crawler.emitter.emit(
        "page",
        url=url,
        path=moved_to or path,
        status="gone",
        tier="http",
        quality_score=None,
        flags=[],
    )
