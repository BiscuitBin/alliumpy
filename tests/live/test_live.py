"""Live smoke tests against the target sites and a JavaScript-rendered site (`-m live`)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.live

TARGETS = {
    "graph": "https://learn.microsoft.com/en-us/graph/api/overview",
    "gmail": "https://developers.google.com/workspace/gmail/api/guides",
}
JS_SITE = "https://redocly.github.io/redoc/"
PAGES = 25


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - our own console entry point with fixed arguments
        [sys.executable, "-m", "docmirror.cli.app", *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=1800,
    )


@pytest.mark.parametrize("name", sorted(TARGETS))
def test_crawl_verify_index(tmp_path: Path, name: str) -> None:
    out = tmp_path / name
    assert run("init", TARGETS[name], str(out)).returncode == 0
    crawl = run("crawl", str(out), "--max-pages", str(PAGES))
    assert crawl.returncode == 0, crawl.stderr[-2000:]
    files = [
        p
        for p in out.rglob("*.md")
        if p.name not in {"index.md", "_index.md"} and "_removed" not in p.parts
    ]
    assert len(files) == PAGES
    for name_ in ("index.md", "index.jsonl", "llms.txt", "crawl-report.json"):
        assert (out / name_).is_file()
    verify = run("verify", str(out), "--json")
    payload = json.loads(verify.stdout.strip().splitlines()[-1])
    assert payload["broken_links"] == []
    assert verify.returncode == 0
    assert run("index", str(out)).returncode == 0
    report = json.loads((out / "crawl-report.json").read_text())
    assert report["quality_summary"]["mean_score"] >= 0.95


def test_js_site_escalation(tmp_path: Path) -> None:
    never = tmp_path / "never"
    assert run("init", JS_SITE, str(never)).returncode == 0
    assert run("crawl", str(never), "--max-pages", "3", "--render", "never").returncode == 0
    report = json.loads((never / "crawl-report.json").read_text())
    assert report["totals"]["low_confidence"] > 0
    flags = {f for p in report["low_confidence_pages"] for f in p["flags"]}
    assert "render_needed" in flags
    auto = tmp_path / "auto"
    assert run("init", JS_SITE, str(auto)).returncode == 0
    assert run("crawl", str(auto), "--max-pages", "3", "--render", "auto").returncode == 0
    report = json.loads((auto / "crawl-report.json").read_text())
    assert "browser" in report["per_host"][0]["tiers_used"]
    assert report["totals"]["converted"] >= 1
