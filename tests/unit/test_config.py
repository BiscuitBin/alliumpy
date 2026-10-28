"""Configuration: defaults, precedence, unknown keys, units and profiles."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pytest

from docmirror.config import BUILTIN_PROFILES, ConfigError, detect_profile, load_config
from docmirror.config.loader import env_overrides, render_toml, validate_config
from docmirror.config.units import parse_duration, parse_size


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "docmirror.toml"
    path.write_text(text, encoding="utf-8")
    return path


def test_defaults_match_the_specification(tmp_path: Path) -> None:
    config = load_config(write(tmp_path, '[site]\nroot_url = "https://example.org/docs/"\n'))
    assert config.scope.max_depth == 10
    assert config.scope.max_pages == 5000
    assert config.scope.max_bytes_int == 2 * 1024**3
    assert config.fetch.rate_per_host == 2.0
    assert config.fetch.concurrency_per_host == 4
    assert config.fetch.retries == 5
    assert config.fetch.robots == "respect"
    assert config.render.mode == "auto"
    assert config.render.min_text_chars == 200
    assert config.antibot.window == 50
    assert config.antibot.block_rate_threshold == 0.20
    assert config.convert.backend == "html-to-markdown"
    assert config.index.hierarchical_threshold == 200
    assert config.update.max_age_delta is None


def test_unknown_key_names_its_path(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match=r"unknown key: scope\.max_pagez"):
        load_config(write(tmp_path, "[scope]\nmax_pagez = 3\n"))


def test_nested_unknown_key_names_its_path() -> None:
    with pytest.raises(ConfigError, match=r"unknown key: extract\.profiles\.x\.bogus"):
        validate_config({"extract": {"profiles": {"x": {"bogus": 1}}}})


def test_precedence_flags_over_env_over_toml(tmp_path: Path) -> None:
    path = write(tmp_path, "[scope]\nmax_pages = 10\nmax_depth = 3\n[fetch]\nrobots = 'respect'\n")
    environ = {"DOCMIRROR_SCOPE__MAX_PAGES": "20", "DOCMIRROR_FETCH__ROBOTS": "ignore"}
    config = load_config(path, environ=environ, overrides={"scope.max_pages": 30})
    assert config.scope.max_pages == 30
    assert config.fetch.robots == "ignore"
    assert config.scope.max_depth == 3


def test_env_overrides_parse_lists_and_booleans() -> None:
    env = {
        "DOCMIRROR_SCOPE__ALLOWED_HOSTS": "a.example, b.example",
        "DOCMIRROR_UPDATE__PRUNE": "true",
        "DOCMIRROR_SITE__LOCALE": "en-us",
        "DOCMIRROR_NOSECTION": "ignored",
    }
    assert env_overrides(env) == {
        "scope": {"allowed_hosts": ["a.example", "b.example"]},
        "update": {"prune": True},
        "site": {"locale": "en-us"},
    }


def test_missing_file_is_a_config_error(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "nope.toml")


def test_provider_section_is_reserved(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="reserved"):
        load_config(write(tmp_path, "[fetch.provider]\nname = 'x'\n"))


@pytest.mark.parametrize(
    ("text", "expected"),
    [("2GiB", 2**31), ("500MB", 500_000_000), ("1024", 1024), ("1.5 KiB", 1536)],
)
def test_parse_size(text: str, expected: int) -> None:
    assert parse_size(text) == expected


@pytest.mark.parametrize("text", ["1K", "2Ki", "3i", "MB"])
def test_parse_size_rejects_unknown_units(text: str) -> None:
    with pytest.raises(ValueError, match="not a size"):
        parse_size(text)
    with pytest.raises(ConfigError, match="max_bytes"):
        validate_config({"scope": {"max_bytes": text}})


def test_parse_duration() -> None:
    assert parse_duration("7d") == timedelta(days=7)
    assert parse_duration("1h30m") == timedelta(hours=1, minutes=30)
    assert parse_duration("") is None
    with pytest.raises(ValueError, match="duration"):
        parse_duration("soon")


def test_builtin_profiles_and_detection() -> None:
    assert set(BUILTIN_PROFILES) == {"generic", "mslearn", "devsite"}
    assert detect_profile("https://learn.microsoft.com/en-us/graph/api/overview") == "mslearn"
    assert detect_profile("https://developers.google.com/workspace/gmail/api/guides") == "devsite"
    assert detect_profile("https://docs.example.org/") == "generic"
    assert BUILTIN_PROFILES["mslearn"].meaningful_query_params == ["view"]


def test_profile_override_merges_under_builtin() -> None:
    config = validate_config(
        {
            "site": {"profile": "mslearn"},
            "extract": {"profiles": {"mslearn": {"strip_selectors": [".custom"]}}},
        }
    )
    profile = config.profile()
    assert profile.strip_selectors == [".custom"]
    assert profile.main_selector == BUILTIN_PROFILES["mslearn"].main_selector
    assert profile.tabs == BUILTIN_PROFILES["mslearn"].tabs


def test_flat_tab_keys_fold_into_tab_specs() -> None:
    config = validate_config(
        {
            "site": {"profile": "custom"},
            "extract": {
                "profiles": {
                    "custom": {
                        "tab_group": ".tabs",
                        "tab_label": "a[data-tab]",
                        "tab_panel": "section[data-tab]",
                        "admonition": "div.note",
                        "admonition_title": "p.title",
                    }
                }
            },
        }
    )
    profile = config.profile()
    assert [t.group for t in profile.tabs] == [".tabs"]
    assert [a.selector for a in profile.admonitions] == ["div.note"]


def test_render_toml_round_trips(tmp_path: Path) -> None:
    config = validate_config(
        {
            "site": {"root_url": "https://example.org/docs/", "name": "Example"},
            "scope": {"version_map": {"graph-rest-1.0": "v1.0"}},
        }
    )
    text = render_toml(config)
    assert text.startswith("[site]\n")
    assert '"graph-rest-1.0" = "v1.0"' in text
    assert load_config(write(tmp_path, text)) == config
