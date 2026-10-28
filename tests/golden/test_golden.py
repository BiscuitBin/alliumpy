"""Golden tests: the Markdown and the quality metrics for every captured page.

A changed snapshot is a fidelity change made visible; accept it with
`just py-test-accept` only after reading the diff. Both backends must produce the
same golden output for the constructs the normalizers own.
"""

from __future__ import annotations

import json

from golden_fixtures import Captured  # noqa: TC002 - pytest resolves the parameter type at runtime

from docmirror.config.loader import validate_config
from docmirror.config.models import Config
from docmirror.pipeline import process_page

MIN_MEAN_SCORE = 0.95


def _config(profile: str, backend: str = "html-to-markdown") -> Config:
    data: dict[str, object] = {"site": {"profile": profile}, "convert": {"backend": backend}}
    if profile == "mslearn":
        data["scope"] = {
            "version_param": "view",
            "version_default": "v1.0",
            "version_map": {"graph-rest-1.0": "v1.0", "graph-rest-beta": "beta"},
        }
    return validate_config(data)


def test_markdown_snapshot(captured: Captured, snapshot: object) -> None:
    config = _config(captured.profile)
    page = process_page(captured.html, captured.url, config, config.profile())
    assert page.markdown_body == snapshot


def test_quality_snapshot(captured: Captured, snapshot: object) -> None:
    config = _config(captured.profile)
    page = process_page(captured.html, captured.url, config, config.profile())
    payload = {
        "quality_score": page.quality_score,
        "failed": page.quality_failed,
        "flags": sorted(page.flags),
        "counts": dict(sorted(page.counts.items())),
        "extractor": page.extractor,
        "title": page.title,
        "headings": page.headings,
    }
    assert json.dumps(payload, indent=2, sort_keys=True) == snapshot
