"""Rewrite absolute in-manifest links to relative paths (completed in phase 4)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from docmirror.pipeline import Crawler


def rewrite_all(crawler: Crawler) -> None:
    """Phase 4 fills this in; phase 2 leaves links absolute."""
    del crawler
