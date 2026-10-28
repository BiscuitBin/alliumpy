"""Reports: `crawl-report.json`, NDJSON progress events and the human table."""

from __future__ import annotations

from docmirror.report.events import EventEmitter
from docmirror.report.models import (
    REPORT_FILENAME,
    BlockedUrl,
    BrokenLink,
    Changes,
    CrawlReport,
    FailedUrl,
    Frontmatter,
    HostReport,
    IndexEntry,
    LowConfidencePage,
    QualitySummary,
    RunInfo,
    Totals,
)

__all__ = [
    "REPORT_FILENAME",
    "BlockedUrl",
    "BrokenLink",
    "Changes",
    "CrawlReport",
    "EventEmitter",
    "FailedUrl",
    "Frontmatter",
    "HostReport",
    "IndexEntry",
    "LowConfidencePage",
    "QualitySummary",
    "RunInfo",
    "Totals",
]
