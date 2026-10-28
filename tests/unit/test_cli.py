"""The CLI shell: version, schemas, init, doctor and report."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
from typer.testing import CliRunner

from docmirror import __version__
from docmirror.cli.app import app
from docmirror.cli.init import guess_locale, seed_config
from docmirror.config.loader import load_config
from docmirror.state import open_manifest

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == f"docmirror {__version__}"


def test_schemas_are_draft_2020_12() -> None:
    for name in ("config", "report", "frontmatter", "index"):
        result = runner.invoke(app, ["schema", name])
        assert result.exit_code == 0, result.output
        document = json.loads(result.stdout)
        assert document["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        jsonschema.Draft202012Validator.check_schema(document)
    assert runner.invoke(app, ["schema", "bogus"]).exit_code == 2


def test_init_writes_config_and_manifest(tmp_path: Path) -> None:
    out = tmp_path / "graph-docs"
    url = "https://learn.microsoft.com/en-us/graph/api/overview?view=graph-rest-1.0"
    result = runner.invoke(app, ["init", url, str(out)])
    assert result.exit_code == 0, result.output
    config = load_config(out / "docmirror.toml")
    assert config.site.profile == "mslearn"
    assert config.site.locale == "en-us"
    assert config.site.root_url == "https://learn.microsoft.com/en-us/graph/"
    assert config.site.name == "Microsoft Graph"
    assert config.scope.allowed_hosts == ["learn.microsoft.com"]
    assert config.scope.path_prefixes == ["/en-us/graph/"]
    assert config.scope.version_map == {"graph-rest-1.0": "v1.0", "graph-rest-beta": "beta"}
    with open_manifest(out) as manifest:
        assert manifest.get_meta("root_url") == config.site.root_url
        assert manifest.get_meta("schema_version") == "1"
    again = runner.invoke(app, ["init", url, str(out)])
    assert again.exit_code == 2


def test_init_devsite_and_generic(tmp_path: Path) -> None:
    config = seed_config("https://developers.google.com/workspace/gmail/api/guides")
    assert config.site.profile == "devsite"
    assert config.site.locale == ""
    assert config.scope.path_prefixes == ["/workspace/"]
    assert config.site.name == "Google Workspace"
    generic = seed_config("https://docs.example.org/")
    assert generic.site.profile == "generic"
    assert generic.scope.path_prefixes == ["/"]
    assert guess_locale("/fr-fr/x") == "fr-fr"
    assert guess_locale("/api/x") == ""
    result = runner.invoke(app, ["init", "ftp://x", str(tmp_path / "o")])
    assert result.exit_code == 2


def test_init_json_event(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["init", "https://docs.example.org/a/", str(tmp_path / "o"), "--json"]
    )
    assert result.exit_code == 0
    event = json.loads(result.stdout.strip().splitlines()[-1])
    assert event["event"] == "init"
    assert event["profile"] == "generic"


def test_doctor_runs() -> None:
    result = runner.invoke(app, ["doctor", "--json"])
    payload = json.loads(result.stdout)
    assert payload["event"] == "doctor"
    names = [check["name"] for check in payload["checks"]]
    assert names[:4] == ["python", "curl_cffi", "patchright", "patchright browser"]
    assert result.exit_code in {0, 1}


def test_report_without_a_report_is_usage(tmp_path: Path) -> None:
    result = runner.invoke(app, ["report", str(tmp_path)])
    assert result.exit_code == 2


def test_refused_crawl_still_writes_a_report(tmp_path: Path) -> None:
    (tmp_path / "docmirror.toml").write_text("[site]\nprofile = 'generic'\n", encoding="utf-8")
    result = runner.invoke(app, ["crawl", str(tmp_path)])
    assert result.exit_code == 2
    report = json.loads((tmp_path / "crawl-report.json").read_text(encoding="utf-8"))
    assert report["run"]["exit_code"] == 2
    (tmp_path / "crawl-report.json").unlink()
    result = runner.invoke(app, ["crawl", str(tmp_path), "--max-bytes", "1K"])
    assert result.exit_code == 2
    assert (tmp_path / "crawl-report.json").is_file()
