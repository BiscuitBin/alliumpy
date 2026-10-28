"""Post-processing, frontmatter and the island mechanism."""

from __future__ import annotations

from lxml import html

from docmirror.convert.frontmatter import body_sha256, render_frontmatter, split_frontmatter
from docmirror.convert.postprocess import postprocess
from docmirror.normalize.islands import Islands, sanitize


def test_postprocess_normalizes_whitespace_but_not_code() -> None:
    text = "a  \r\n\n\n\nb\n```py\nx   \n\n\n\ny\n```\n\n\n"
    assert postprocess(text) == "a\n\nb\n\n```py\nx   \n\n\n\ny\n```\n"


def test_postprocess_spaces_quotes() -> None:
    text = "p\n> [!NOTE]\n> a\n> [!TIP]\n> b\nq\n"
    assert postprocess(text) == "p\n\n> [!NOTE]\n> a\n\n> [!TIP]\n> b\n\nq\n"


def test_frontmatter_round_trip_and_hash() -> None:
    block = render_frontmatter({"title": "T", "b": None, "a": [1, 2], "quality_score": 0.5})
    assert block == "---\na: [1, 2]\nquality_score: 0.5\ntitle: T\n---\n"
    fields, body = split_frontmatter(block + "\nbody\n")
    assert fields == {"a": [1, 2], "quality_score": 0.5, "title": "T"}
    assert body == "\nbody\n"
    assert body_sha256("x\n") != body_sha256("x")
    assert split_frontmatter("no frontmatter") == ({}, "no frontmatter")


def test_islands_restore_in_order() -> None:
    islands = Islands()
    first = islands.register("<table></table>")
    second = islands.register("<kbd>K</kbd>")
    assert (
        islands.restore(f"before {first} mid {second} after")
        == "before <table></table> mid <kbd>K</kbd> after"
    )
    assert len(islands) == 2


def test_islands_replace_element_and_sanitize() -> None:
    root = html.fromstring(
        '<div><p>a</p><table class="x" rowspan="2" style="c">'
        '<tr><td colspan="2">v</td></tr></table><p>b</p></div>'
    )
    table = root.find("table")
    islands = Islands()
    islands.replace_element(table, sanitize(table))
    assert [c.tag for c in root] == ["p", "p", "p"]
    token = root[1].text or ""
    assert token.startswith("DOCMIRRORISLAND")
    restored = islands.restore(token)
    assert 'class="x"' not in restored
    assert 'colspan="2"' in restored
    assert 'rowspan="2"' in restored
