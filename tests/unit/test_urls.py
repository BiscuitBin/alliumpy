"""URL normalization, scope rules and locale handling."""

from __future__ import annotations

import pytest

from docmirror.frontier.urls import ScopeRules, UrlNormalizer, locale_segment, path_pattern

NORMALIZER = UrlNormalizer(frozenset({"view"}))


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (
            "HTTPS://Learn.Microsoft.com:443/en-us/graph/",
            "https://learn.microsoft.com/en-us/graph/",
        ),
        ("https://h/a/./b/../c/index.html#frag", "https://h/a/c/"),
        ("https://h/a?utm_source=x&gclid=1&WT.mc_id=2&ref=3", "https://h/a"),
        ("https://h/a?view=v1&tabs=http&b=2", "https://h/a?view=v1"),
        ("https://h/a?view=b&view=a", "https://h/a?view=a&view=b"),
        ("https://h/a%7Eb%2Fc", "https://h/a~b%2Fc"),
        ("https://h:8080/x", "https://h:8080/x"),
        ("https://h", "https://h/"),
        ("https://h/Index.htm", "https://h/"),
    ],
)
def test_normalize(raw: str, expected: str) -> None:
    assert NORMALIZER.normalize(raw) == expected


def test_split_fragment() -> None:
    assert NORMALIZER.split_fragment("https://h/a?x=1#sec") == ("https://h/a", "sec")


def test_scope_rules() -> None:
    rules = ScopeRules(
        frozenset({"h"}),
        ("/en-us/graph/",),
        include=(),
        exclude=("re:/graph/(changelog|whats-new)", "**/toc.json"),
        locale="en-us",
        max_depth=3,
    )
    assert rules.in_scope("https://h/en-us/graph/api/overview")
    assert not rules.in_scope("https://h/en-us/graph/changelog/")
    assert not rules.in_scope("https://h/en-us/graph/x/toc.json")
    assert not rules.in_scope("https://other/en-us/graph/api")
    assert not rules.in_scope("https://h/fr-fr/graph/api/overview")
    assert not rules.in_scope("https://h/en-us/azure/")
    assert not rules.in_scope("https://h/en-us/graph/api/overview", depth=4)
    assert rules.with_locale("https://h/fr-fr/graph/api/x#f") == "https://h/en-us/graph/api/x#f"
    assert rules.with_locale("https://h/en-us/graph/api/x") == "https://h/en-us/graph/api/x"


def test_include_restricts() -> None:
    rules = ScopeRules(frozenset({"h"}), ("/docs/",), include=("*/docs/api/*",))
    assert rules.in_scope("https://h/docs/api/one")
    assert not rules.in_scope("https://h/docs/guide/one")


def test_helpers() -> None:
    assert path_pattern("https://h/en-us/graph/api/x") == "/en-us/graph"
    assert path_pattern("https://h/") == "/"
    assert locale_segment("/en-us/graph") == "en-us"
    assert locale_segment("/workspace/gmail") == ""
