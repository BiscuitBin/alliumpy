"""404/410 handling: move the file to `_removed/` or delete it (completed in phase 6)."""

from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

from docmirror.state.db import now_iso

if TYPE_CHECKING:
    from docmirror.pipeline import Crawler


def tombstone(crawler: Crawler, url: str, status: int, known: sqlite3.Row) -> None:
    """Record the tombstone; the file move lands with phase 6."""
    crawler.manifest.upsert_page(url, tombstoned_at=now_iso(), http_status=status, status="gone")
    crawler.report.changes.removed.append(str(known["path"]))
    crawler.emitter.emit(
        "page",
        url=url,
        path=known["path"],
        status="gone",
        tier="http",
        quality_score=None,
        flags=[],
    )
