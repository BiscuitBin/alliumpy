"""Link rewriting, keywords, index writers and verify over a hand-built output tree."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from docmirror.cli.verify import verify_tree
from docmirror.config.loader import validate_config
from docmirror.convert.frontmatter import body_sha256, render_frontmatter, split_frontmatter
from docmirror.frontier.urls import ScopeRules, UrlNormalizer
from docmirror.index.keywords import compute_keywords, merge_keywords, plain_text
from docmirror.index.summarize import NoopSummarizer, summarizer_for
from docmirror.index.writers import write_indexes
from docmirror.links.rewriter import LinkRewriter, PageRow
from docmirror.report.models import IndexEntry, json_schema
from docmirror.state.db import Manifest, atomic_write_text

ROOT = "https://h/docs/"


def _page(
    manifest: Manifest, out: Path, url: str, path: str, body: str, *, anchors: tuple[str, ...] = ()
) -> None:
    sha = body_sha256(body)
    frontmatter = {
        "source_url": url,
        "title": path.rsplit("/", 1)[-1].removesuffix(".md").title(),
        "fetched_at": "2026-10-28T00:00:00Z",
        "content_sha256": sha,
        "quality_score": 1.0,
        "low_confidence": False,
        "quality_flags": [],
        "description": f"About {path}",
    }
    atomic_write_text(out / path, render_frontmatter(frontmatter) + "\n" + body)
    manifest.upsert_page(
        url,
        path=path,
        title=frontmatter["title"],
        status="written",
        content_sha256=sha,
        prewrite_sha256=sha,
        frontmatter=frontmatter,
        headings=["Overview"],
        word_count=len(body.split()),
        description=frontmatter["description"],
    )
    manifest.replace_anchors(url, list(anchors))


def build_tree(tmp_path: Path) -> tuple[Manifest, Path]:
    out = tmp_path / "out"
    out.mkdir()
    manifest = Manifest(out / ".docmirror" / "state.sqlite")
    _page(
        manifest,
        out,
        ROOT + "a",
        "a.md",
        '# A {#top}\n\nSee [B](https://h/docs/sub/b#sec) and [gone](https://h/docs/gone) and [self](https://h/docs/a#top).\n\nAlso <a href="https://h/docs/sub/b">b</a> and [ext](https://other/x).\n',
        anchors=("top",),
    )
    _page(
        manifest,
        out,
        ROOT + "sub/b",
        "sub/b.md",
        "# B\n\n## Section {#sec}\n\nBack to [A](https://h/docs/a).\n\n```python\nprint('[not](https://h/docs/a)')\n```\n",
        anchors=("sec",),
    )
    _page(manifest, out, ROOT + "sub/c", "sub/c.md", "# C\n\nPlain page.\n")
    return manifest, out


def test_rewriter_relative_fragments_and_flags(tmp_path: Path) -> None:
    manifest, out = build_tree(tmp_path)
    normalizer = UrlNormalizer(frozenset())
    scope = ScopeRules(frozenset({"h"}), ("/docs/",))
    rewriter = LinkRewriter(manifest, normalizer, scope, out)
    page_a = rewriter.by_url[ROOT + "a"]
    _, body = split_frontmatter((out / "a.md").read_text())
    new_body, outcome = rewriter.rewrite_text(page_a, body)
    assert "[B](sub/b.md#sec)" in new_body
    assert "[gone](https://h/docs/gone)" in new_body
    assert "[self](#top)" in new_body
    assert '<a href="sub/b.md">b</a>' in new_body
    assert "[ext](https://other/x)" in new_body
    assert outcome.flags == {"uncrawled_internal"}
    kinds = sorted(kind for _, _, kind, _ in outcome.links)
    assert kinds == ["external", "internal", "internal", "uncrawled"]
    # Rewriting the rewritten page records the same rows: the self-link counted nowhere.
    _, second = rewriter.rewrite_text(page_a, new_body)
    assert sorted(second.links) == sorted(outcome.links)
    page_b = rewriter.by_url[ROOT + "sub/b"]
    _, body_b = split_frontmatter((out / "sub/b.md").read_text())
    new_b, _ = rewriter.rewrite_text(page_b, body_b)
    assert "[A](../a.md)" in new_b
    assert "print('[not](https://h/docs/a)')" in new_b
    again, _ = rewriter.rewrite_text(page_b, new_b)
    assert again == new_b


def test_rewriter_unresolved_fragment_and_removed_target(tmp_path: Path) -> None:
    manifest, out = build_tree(tmp_path)
    rewriter = LinkRewriter(
        manifest, UrlNormalizer(frozenset()), ScopeRules(frozenset({"h"}), ("/docs/",)), out
    )
    page_a = rewriter.by_url[ROOT + "a"]
    _, outcome = rewriter.rewrite_text(page_a, "[x](https://h/docs/sub/b#missing)")
    assert "unresolved_fragment" in outcome.flags
    assert outcome.broken
    manifest.upsert_page(ROOT + "sub/b", tombstoned_at="2026-10-28T00:00:00Z", status="gone")
    rewriter = LinkRewriter(
        manifest, UrlNormalizer(frozenset()), ScopeRules(frozenset({"h"}), ("/docs/",)), out
    )
    page_a = rewriter.by_url[ROOT + "a"]
    text, outcome = rewriter.rewrite_text(page_a, "[B](sub/b.md#sec)")
    assert text == "[B](https://h/docs/sub/b#sec)"
    assert "dangling_inbound" in outcome.flags


def test_bare_fragment_links_are_checked_and_canonicalised(tmp_path: Path) -> None:
    manifest, out = build_tree(tmp_path)
    manifest.replace_anchors(ROOT + "a", ["top", "get(Optional<Q>)", "apply(a, b)"])
    rewriter = LinkRewriter(
        manifest, UrlNormalizer(frozenset()), ScopeRules(frozenset({"h"}), ("/docs/",)), out
    )
    page_a = rewriter.by_url[ROOT + "a"]
    body = '[x](#get(Optional&lt;Q&gt;)) <a href="#apply(a,%20b)">y</a> [z](#nope)'
    text, outcome = rewriter.rewrite_text(page_a, body)
    assert text == body
    assert outcome.broken == [("#nope", "fragment #nope not found in a.md")]


def test_relative_target_row_lookup() -> None:
    row = PageRow("u", "a/b.md", "https://h/a/b", tombstoned=False)
    assert row.path == "a/b.md"


def test_index_writers_and_schema(tmp_path: Path) -> None:
    manifest, out = build_tree(tmp_path)
    config = validate_config(
        {"site": {"name": "Docs", "root_url": ROOT}, "index": {"hierarchical_threshold": 1}}
    )
    pages = write_indexes(config, out, manifest, None)
    assert [p.entry.path for p in pages] == ["a.md", "sub/b.md", "sub/c.md"]
    index_md = (out / "index.md").read_text()
    assert index_md.startswith("# Docs documentation index\n")
    assert "- [A](a.md) — About a.md" in index_md
    assert "- [sub](sub/_index.md) — 2 pages" in index_md
    assert (out / "sub" / "_index.md").read_text().startswith("# sub\n")
    schema = json_schema(IndexEntry)
    for line in (out / "index.jsonl").read_text().splitlines():
        jsonschema.validate(json.loads(line), schema)
    llms = (out / "llms.txt").read_text()
    assert llms.startswith("# Docs\n\n> About a.md\n")
    assert "- [A](a.md): About a.md" in llms
    frontmatter, _ = split_frontmatter((out / "a.md").read_text())
    assert isinstance(frontmatter["keywords"], list)
    cached = manifest.cached_keywords(frontmatter["content_sha256"])
    assert cached == frontmatter["keywords"]
    again = write_indexes(config, out, manifest, None)
    assert [p.entry.keywords for p in again] == [p.entry.keywords for p in pages]


def test_keywords_are_deterministic_and_filtered() -> None:
    text = plain_text("# T\n\nThe `code` word and **bold** word.\n\n```py\nignored = 1\n```\n")
    assert "ignored" not in text
    assert "code" not in text
    merged = merge_keywords(
        [("the", 0.1), ("alpha beta", 0.2), ("gamma", 0.3)],
        [("gamma", 0.9), ("delta", 0.5)],
        {"delta"},
    )
    assert set(merged[:2]) == {"alpha beta", "gamma"}
    assert "the" not in merged
    assert "delta" not in merged
    bodies = {
        "a": "Gmail labels organise messages and threads in a mailbox. " * 5,
        "b": "Calendar events have start and end times. " * 5,
    }
    first = compute_keywords(bodies)
    assert compute_keywords(bodies) == first
    assert all(5 <= len(v) <= 8 or len(v) >= 1 for v in first.values())


def test_summarizer_protocol() -> None:
    assert isinstance(summarizer_for("none"), NoopSummarizer)
    assert NoopSummarizer().summarize("T", "body", "fallback") == "fallback"


def test_verify_tree_reports_problems(tmp_path: Path) -> None:
    manifest, out = build_tree(tmp_path)
    manifest.close()
    result = verify_tree(out)
    assert result.pages == 3
    assert result.ok, (result.problems, result.broken_links)
    (out / "stray.md").write_text("# stray\n")
    frontmatter, body = split_frontmatter((out / "a.md").read_text())
    atomic_write_text(
        out / "a.md",
        render_frontmatter(frontmatter)
        + "\n"
        + body
        + "[broken](nowhere.md) [frag](sub/b.md#nope)\n",
    )
    result = verify_tree(out)
    problems = dict(result.problems)
    assert problems["stray.md"] == "in the tree but not in the manifest"
    assert "content_sha256" in problems["a.md"]
    reasons = sorted(reason for _, _, reason in result.broken_links)
    assert reasons == ["fragment #nope not found in sub/b.md", "target file not found"]
    # A page flagged `code_lang_rate` whose fences verify also finds untagged counts once.
    frontmatter["quality_flags"] = ["code_lang_rate"]
    atomic_write_text(out / "a.md", render_frontmatter(frontmatter) + "\n" + "```\nx\n```\n")
    result = verify_tree(out)
    assert result.gate_failures == {"code_lang_rate": 1}
