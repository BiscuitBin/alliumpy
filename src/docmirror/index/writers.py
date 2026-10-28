"""`index.md`, `index.jsonl`, `llms.txt` and `_index.md` (completed in phase 4)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from docmirror.config.models import Config
    from docmirror.report.builder import ReportBuilder
    from docmirror.state.db import Manifest


def write_indexes(config: Config, out_dir: Path, manifest: Manifest, report: ReportBuilder) -> None:
    """Phase 4 fills this in."""
    del config, out_dir, manifest, report
