"""Accumulate a run's outcomes and write `crawl-report.json`."""

from __future__ import annotations

import hashlib
import json
import statistics
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from docmirror import __version__
from docmirror.report.models import (
    REPORT_FILENAME,
    BlockedUrl,
    BrokenLink,
    Changes,
    CrawlReport,
    FailedUrl,
    HostReport,
    LowConfidencePage,
    QualitySummary,
    RunInfo,
    Totals,
)
from docmirror.state.db import atomic_write_text


def config_hash(config_text: str) -> str:
    """The SHA-256 of the configuration file's text."""
    return hashlib.sha256(config_text.encode("utf-8")).hexdigest()[:16]


def new_run_id(now: datetime | None = None) -> str:
    """`2026-10-28T08-10-00Z-7f3a`."""
    current = now or datetime.now(tz=UTC)
    suffix = hashlib.sha256(str(time.time_ns()).encode()).hexdigest()[:4]
    return current.strftime("%Y-%m-%dT%H-%M-%SZ") + "-" + suffix


@dataclass
class HostStats:
    """Live counters for one host."""

    fetched: int = 0
    blocked: int = 0
    tiers_used: set[str] = field(default_factory=set)
    breaker_tripped: bool = False
    render_escalations: int = 0
    retry_after_honored: int = 0
    outcomes: list[bool] = field(default_factory=list)

    def block_rate(self, window: int) -> float:
        """Share of blocks in the last `window` outcomes."""
        recent = self.outcomes[-window:]
        return (sum(recent) / len(recent)) if recent else 0.0


@dataclass
class ReportBuilder:
    """Everything the report needs, filled in as the run proceeds."""

    command: str
    config_hash: str
    robots_ignored: bool = False
    run_id: str = field(default_factory=new_run_id)
    started: float = field(default_factory=time.time)
    totals: Totals = field(default_factory=Totals)
    hosts: dict[str, HostStats] = field(default_factory=dict)
    blocked_urls: list[BlockedUrl] = field(default_factory=list)
    failed_urls: list[FailedUrl] = field(default_factory=list)
    low_confidence_pages: list[LowConfidencePage] = field(default_factory=list)
    broken_links: list[BrokenLink] = field(default_factory=list)
    changes: Changes = field(default_factory=Changes)
    scores: list[float] = field(default_factory=list)
    gate_failures: dict[str, int] = field(default_factory=dict)
    window: int = 50

    def host(self, name: str) -> HostStats:
        """The counters for a host, created on first use."""
        return self.hosts.setdefault(name, HostStats())

    def record_quality(
        self,
        path: str,
        score: float,
        failed: list[str],
        flags: list[str],
        *,
        low_confidence: bool | None = None,
    ) -> None:
        """Record one page's quality outcome."""
        self.scores.append(score)
        for gate in failed:
            self.gate_failures[gate] = self.gate_failures.get(gate, 0) + 1
        if bool(failed) if low_confidence is None else low_confidence:
            self.totals.low_confidence += 1
            self.low_confidence_pages.append(
                LowConfidencePage(path=path, quality_score=score, flags=flags)
            )

    def build(self, exit_code: int) -> CrawlReport:
        """The report model for the run so far."""
        finished = time.time()
        quality = QualitySummary(
            mean_score=round(statistics.fmean(self.scores), 4) if self.scores else 0.0,
            p10_score=round(_percentile(self.scores, 0.10), 4) if self.scores else 0.0,
            gate_failures=dict(sorted(self.gate_failures.items())),
        )
        per_host = [
            HostReport(
                host=name,
                fetched=stats.fetched,
                blocked=stats.blocked,
                block_rate=round(stats.block_rate(self.window), 4),
                tiers_used=sorted(stats.tiers_used),
                breaker_tripped=stats.breaker_tripped,
                robots_ignored=self.robots_ignored,
                render_escalations=stats.render_escalations,
                retry_after_honored=stats.retry_after_honored,
            )
            for name, stats in sorted(self.hosts.items())
        ]
        return CrawlReport(
            run=RunInfo(
                id=self.run_id,
                command=self.command,
                started_at=_iso(self.started),
                finished_at=_iso(finished),
                duration_s=round(finished - self.started, 3),
                exit_code=exit_code,
                version=__version__,
                config_hash=self.config_hash,
                robots_ignored=self.robots_ignored,
            ),
            totals=self.totals,
            per_host=per_host,
            blocked_urls=self.blocked_urls,
            failed_urls=self.failed_urls,
            low_confidence_pages=sorted(self.low_confidence_pages, key=lambda p: p.path),
            broken_links=self.broken_links,
            changes=Changes(**{k: sorted(v) for k, v in self.changes.model_dump().items()}),
            quality_summary=quality,
            render_escalations=sum(h.render_escalations for h in self.hosts.values()),
            retry_after_honored=sum(h.retry_after_honored for h in self.hosts.values()),
            robots_ignored=self.robots_ignored,
        )

    def write(self, out_dir: Path, exit_code: int) -> CrawlReport:
        """Write `crawl-report.json` and return the model."""
        report = self.build(exit_code)
        atomic_write_text(
            out_dir / REPORT_FILENAME, json.dumps(report.model_dump(), indent=2) + "\n"
        )
        return report

    def counts(self) -> dict[str, Any]:
        """The totals as a plain mapping for the run record."""
        return self.totals.model_dump()


def _iso(stamp: float) -> str:
    return datetime.fromtimestamp(stamp, tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round(fraction * (len(ordered) - 1))))
    return ordered[index]
