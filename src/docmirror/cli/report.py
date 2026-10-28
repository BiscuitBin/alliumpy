"""`docmirror report`: print the last crawl-report.json."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from docmirror.cli.common import Common, fail
from docmirror.exit_codes import ExitCode
from docmirror.report.models import REPORT_FILENAME, CrawlReport


def run_report(out_dir: Path, common: Common) -> ExitCode:
    """Load and print the report."""
    path = out_dir / REPORT_FILENAME
    if not path.is_file():
        fail(f"no {REPORT_FILENAME} in {out_dir}; run docmirror crawl first", ExitCode.USAGE)
    text = path.read_text(encoding="utf-8")
    if common.json_events:
        print(text.rstrip())
        return ExitCode.OK
    report = CrawlReport.model_validate(json.loads(text))
    console = Console()
    for table in _tables(report):
        console.print(table)
    return ExitCode.OK


def _key_values(title: str, rows: dict[str, object]) -> Table:
    table = Table(title=title, show_header=False)
    for key, value in rows.items():
        table.add_row(key, str(value))
    return table


def _rows(title: str, columns: tuple[str, ...], rows: list[tuple[str, ...]]) -> Table:
    table = Table(title=title)
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(*row)
    return table


def _tables(report: CrawlReport) -> list[Table]:
    tables = [
        _key_values(f"Run {report.run.id} ({report.run.command})", report.run.model_dump()),
        _key_values("Totals", report.totals.model_dump()),
        _rows(
            "Hosts",
            ("host", "fetched", "blocked", "block_rate", "tiers_used", "breaker", "robots_ignored"),
            [
                (
                    host.host,
                    str(host.fetched),
                    str(host.blocked),
                    f"{host.block_rate:.2f}",
                    ", ".join(host.tiers_used),
                    str(host.breaker_tripped),
                    str(host.robots_ignored),
                )
                for host in report.per_host
            ],
        ),
        _key_values(
            "Quality",
            {
                "mean_score": f"{report.quality_summary.mean_score:.3f}",
                "p10_score": f"{report.quality_summary.p10_score:.3f}",
                **{
                    f"gate failure: {gate}": count
                    for gate, count in sorted(report.quality_summary.gate_failures.items())
                },
            },
        ),
    ]
    if report.low_confidence_pages:
        tables.append(
            _rows(
                "Low-confidence pages",
                ("path", "score", "flags"),
                [
                    (p.path, f"{p.quality_score:.2f}", ", ".join(p.flags))
                    for p in report.low_confidence_pages
                ],
            )
        )
    if report.blocked_urls:
        tables.append(
            _rows(
                "Blocked URLs",
                ("url", "status", "signature", "tier"),
                [(b.url, str(b.status), b.signature, b.tier) for b in report.blocked_urls],
            )
        )
    if report.broken_links:
        tables.append(
            _rows(
                "Broken links",
                ("from_path", "href", "reason"),
                [(b.from_path, b.href, b.reason) for b in report.broken_links],
            )
        )
    return tables
