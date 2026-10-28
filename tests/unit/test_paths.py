"""URL to output path mapping, collisions and reserved names."""

from __future__ import annotations

import pytest

from docmirror.links.paths import PathMapper, relative_path

GRAPH = PathMapper(
    ("/en-us/graph/",),
    version_param="view",
    version_default="v1.0",
    version_map={"graph-rest-1.0": "v1.0", "graph-rest-beta": "beta"},
)


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://h/en-us/graph/api/user-get?view=graph-rest-1.0", "api/v1.0/user-get.md"),
        ("https://h/en-us/graph/api/user-get?view=graph-rest-beta", "api/beta/user-get.md"),
        ("https://h/en-us/graph/api/user-get?view=other", "api/other/user-get.md"),
        ("https://h/en-us/graph/overview", "overview.md"),
        ("https://h/en-us/graph/", "index.md"),
        ("https://h/en-us/graph/auth/", "auth/index.md"),
        ("https://h/en-us/graph/x/page.aspx", "x/page.md"),
        ("https://h/en-us/graph/a%20b/c%3Fd.html", "a-b/c-d.md"),
        ("https://h/en-us/graph/con/aux", "con-/aux-.md"),
    ],
)
def test_candidate(url: str, expected: str) -> None:
    assert GRAPH.candidate(url) == expected


def test_version_values() -> None:
    assert GRAPH.version_of("https://h/en-us/graph/overview") == "v1.0"
    assert GRAPH.version_of("https://h/en-us/graph/api/x?view=graph-rest-beta") == "beta"
    assert PathMapper(("/d/",)).version_of("https://h/d/x") is None


def test_collisions_and_reserved() -> None:
    taken = {"api/v1.0/user-get.md"}
    url = "https://h/en-us/graph/api/user-get?view=graph-rest-1.0"
    hashed = GRAPH.assign(url, taken.__contains__)
    assert hashed.startswith("api/v1.0/user-get-")
    assert hashed.endswith(".md")
    assert len(hashed) == len("api/v1.0/user-get-.md") + 6
    assert GRAPH.assign(url, lambda _: False) == "api/v1.0/user-get.md"
    plain = PathMapper(("/",))
    assert plain.assign("https://h/llms.txt", lambda _: False) != "llms.txt"
    assert plain.assign("https://h/_removed/x", lambda _: False).startswith("_removed/x-")
    long_url = "https://h/" + "a" * 250
    assert len(plain.assign(long_url, lambda _: False)) <= 200


def test_lowercase_and_template() -> None:
    mapper = PathMapper(("/Docs/",), lowercase=True, template="pages/{path}")
    assert mapper.candidate("https://h/Docs/API/Get.html") == "pages/api/get.md"


def test_relative_path() -> None:
    assert relative_path("api/v1.0/user-get.md", "api/beta/user-list.md") == "../beta/user-list.md"
    assert relative_path("index.md", "guide/start.md") == "guide/start.md"
    assert relative_path("a/b/c.md", "a/b/c.md") == "c.md"
