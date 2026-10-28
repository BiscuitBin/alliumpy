"""The update algorithm against a fake server: 200, 304, 301, 404 and stability."""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer
from werkzeug.wrappers import Request, Response

from docmirror.config.loader import validate_config
from docmirror.convert.frontmatter import split_frontmatter
from docmirror.exit_codes import ExitCode
from docmirror.pipeline import Crawler
from docmirror.report.events import EventEmitter
from docmirror.report.models import CrawlReport
from docmirror.state.db import open_manifest


class FakeSite:
    """A tiny documentation site whose pages can change, vanish or move between runs."""

    def __init__(self, server: HTTPServer) -> None:
        self.server = server
        self.pages: dict[str, str] = {}
        self.redirects: dict[str, str] = {}
        self.gone: set[str] = set()
        self.hits: list[tuple[str, str | None]] = []
        self.server.expect_request("/robots.txt").respond_with_data("", status=404)
        server.expect_request("/sitemap.xml").respond_with_data("", status=404)
        server.expect_request("/sitemap_index.xml").respond_with_data("", status=404)
        server.expect_request("/llms.txt").respond_with_data("", status=404)
        for name in ("home", "a", "b", "c"):
            self.pages[f"/docs/{name}"] = self._html(name)
            server.expect_request(f"/docs/{name}").respond_with_handler(
                self._handler(f"/docs/{name}")
            )
        server.expect_request("/docs/moved").respond_with_handler(self._handler("/docs/moved"))

    @staticmethod
    def _html(name: str, version: int = 1) -> str:
        links = " ".join(
            f'<a href="/docs/{other}#sec">{other}</a>'
            for other in ("home", "a", "b", "c")
            if other != name
        )
        return (
            f"<html><head><title>{name}</title></head><body><main><h1>{name.title()}</h1>"
            f"<p>Content of {name}, version {version}. {'words ' * 40}</p><h2 id='sec'>Section</h2>"
            f"<p>{links}</p></main></body></html>"
        )

    def _handler(self, path: str):  # type: ignore[no-untyped-def]  # noqa: ANN202
        def handle(request: Request) -> Response:
            self.hits.append((path, request.headers.get("If-None-Match")))
            if path in self.gone:
                return Response("gone", status=404)
            if path in self.redirects:
                return Response(
                    "", status=301, headers={"Location": self.server.url_for(self.redirects[path])}
                )
            body = self.pages[path]
            etag = '"' + hashlib.sha1(body.encode()).hexdigest()[:12] + '"'  # noqa: S324 - not security
            if request.headers.get("If-None-Match") == etag:
                return Response("", status=304, headers={"ETag": etag})
            return Response(
                body, status=200, headers={"ETag": etag, "Content-Type": "text/html; charset=utf-8"}
            )

        return handle

    @property
    def root(self) -> str:
        return self.server.url_for("/docs/")


def _config(site: FakeSite) -> object:
    host = site.server.host
    return validate_config(
        {
            "site": {
                "root_url": site.root,
                "start_urls": [site.server.url_for("/docs/home")],
                "profile": "generic",
            },
            "scope": {
                "allowed_hosts": [f"{host}:{site.server.port}"],
                "path_prefixes": ["/docs/"],
                "max_pages": 50,
            },
            "fetch": {"rate_per_host": 1000, "retries": 1, "impersonate": "", "user_agent": "test"},
            "render": {"mode": "never"},
        }
    )


def _run(site: FakeSite, out: Path, command: str = "crawl", **flags: object) -> CrawlReport:
    config = _config(site)
    if flags:
        for key, value in flags.items():
            section, field = key.split("__")
            setattr(getattr(config, section), field, value)
    with open_manifest(out) as manifest:
        crawler = Crawler(config, out, manifest, EventEmitter(enabled=False), command=command)  # type: ignore[arg-type]
        crawler.robots = {}
        code = asyncio.run(crawler.run())
    report = CrawlReport.model_validate_json((out / "crawl-report.json").read_text())
    assert report.run.exit_code == int(code)
    return report


def _snapshot(out: Path) -> dict[str, bytes]:
    return {
        p.relative_to(out).as_posix(): p.read_bytes()
        for p in out.rglob("*")
        if p.is_file() and ".docmirror" not in p.parts and p.name != "crawl-report.json"
    }


@pytest.fixture
def site(httpserver: HTTPServer) -> FakeSite:
    return FakeSite(httpserver)


def test_first_crawl_then_unchanged_update_is_byte_identical(
    site: FakeSite, tmp_path: Path
) -> None:
    out = tmp_path / "out"
    out.mkdir()
    report = _run(site, out)
    assert report.run.exit_code == ExitCode.OK
    assert report.totals.converted == 4
    first_quality = report.quality_summary
    assert (
        sorted(report.changes.added) == ["a.md", "b.md", "c.md", "index.md"]
        or len(report.changes.added) == 4
    )
    before = _snapshot(out)
    assert any(name.endswith(".md") for name in before)
    site.hits.clear()
    report = _run(site, out, command="update")
    assert report.run.exit_code == ExitCode.OK
    assert report.totals.skipped_unchanged == 4
    assert report.totals.converted == 0
    assert report.quality_summary == first_quality
    assert all(
        etag is not None
        for path, etag in site.hits
        if path.startswith("/docs/") and path != "/docs/moved"
    )
    assert _snapshot(out) == before


def test_update_handles_change_removal_and_redirect(site: FakeSite, tmp_path: Path) -> None:
    out = tmp_path / "out"
    out.mkdir()
    _run(site, out)
    before = _snapshot(out)
    paths = {p for p in before if p.endswith(".md")}
    assert {"a.md", "b.md", "c.md"} <= paths
    site.pages["/docs/a"] = FakeSite._html("a", version=2)  # noqa: SLF001 - test helper
    site.gone.add("/docs/c")
    site.redirects["/docs/b"] = "/docs/moved"
    site.pages["/docs/moved"] = FakeSite._html("moved")  # noqa: SLF001
    report = _run(site, out, command="update")
    assert report.run.exit_code == ExitCode.OK
    assert "a.md" in report.changes.changed
    assert "c.md" in report.changes.removed
    after = _snapshot(out)
    assert after["a.md"] != before["a.md"]
    assert "version 2" in after["a.md"].decode()
    assert "c.md" not in after
    assert "_removed/c.md" in after
    home_body = split_frontmatter(after["home.md"].decode())[1]
    assert "](c.md#sec)" not in home_body
    assert site.server.url_for("/docs/c") + "#sec" in home_body
    frontmatter = split_frontmatter(after["home.md"].decode())[0]
    assert "dangling_inbound" in frontmatter["quality_flags"]
    assert "b.md" in after
    assert "Moved" in after["b.md"].decode()
    with open_manifest(out) as manifest:
        moved = manifest.get_page(site.server.url_for("/docs/moved"))
        assert moved is not None
        assert moved["path"] == "b.md"
        old = manifest.get_page(site.server.url_for("/docs/b"))
        assert old is not None
        assert old["redirect_to"] == site.server.url_for("/docs/moved")
        assert manifest.resolve_alias(site.server.url_for("/docs/b")) == site.server.url_for(
            "/docs/moved"
        )
    jsonl = [json.loads(line) for line in (out / "index.jsonl").read_text().splitlines()]
    assert sorted(entry["path"] for entry in jsonl) == ["a.md", "b.md", "home.md"]


def test_prune_deletes_instead_of_moving(site: FakeSite, tmp_path: Path) -> None:
    out = tmp_path / "out"
    out.mkdir()
    _run(site, out)
    site.gone.add("/docs/c")
    _run(site, out, command="update", update__prune=True)
    after = _snapshot(out)
    assert "c.md" not in after
    assert "_removed/c.md" not in after


def test_max_age_forces_refetch(site: FakeSite, tmp_path: Path) -> None:
    out = tmp_path / "out"
    out.mkdir()
    _run(site, out)
    site.hits.clear()
    _run(site, out, command="update", update__max_age="0s")
    conditional = [etag for path, etag in site.hits if path != "/docs/moved"]
    assert conditional
    assert all(etag is None for etag in conditional)


def test_tombstoned_page_that_returns_is_restored(site: FakeSite, tmp_path: Path) -> None:
    out = tmp_path / "out"
    out.mkdir()
    _run(site, out)
    site.gone.add("/docs/c")
    _run(site, out, command="update")
    assert "_removed/c.md" in _snapshot(out)
    with open_manifest(out) as manifest:
        first = manifest.get_page(site.server.url_for("/docs/c"))
    again = _run(site, out, command="update")
    assert "c.md" not in again.changes.removed
    assert "_removed/c.md" in _snapshot(out)
    with open_manifest(out) as manifest:
        still = manifest.get_page(site.server.url_for("/docs/c"))
    assert first is not None
    assert still is not None
    assert still["tombstoned_at"] == first["tombstoned_at"]
    site.gone.discard("/docs/c")
    report = _run(site, out, command="update")
    after = _snapshot(out)
    assert "c.md" in after
    assert "_removed/c.md" not in after
    assert "c.md" in report.changes.added
    with open_manifest(out) as manifest:
        row = manifest.get_page(site.server.url_for("/docs/c"))
        assert row is not None
        assert row["tombstoned_at"] is None


def test_deferred_recheck_runs_last_unless_rediscovered(tmp_path: Path) -> None:
    with open_manifest(tmp_path) as manifest:
        for url in ("https://h/gone", "https://h/back", "https://h/a", "https://h/b"):
            manifest.enqueue(url, depth=2, discovered_from=None, discovered_via="link")
        manifest.frontier_set_status("https://h/gone", "gone")
        manifest.frontier_defer("https://h/back")
        manifest.enqueue("https://h/gone", depth=0, discovered_from=None, discovered_via="link")
        order = [entry.url for entry in manifest.frontier_pending(10)]
        assert order == ["https://h/a", "https://h/b", "https://h/back"]
        manifest.enqueue(
            "https://h/back", depth=1, discovered_from=None, discovered_via="sitemap", priority=50
        )
        order = [entry.url for entry in manifest.frontier_pending(10)]
        assert order == ["https://h/back", "https://h/a", "https://h/b"]
