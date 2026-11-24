# Copyright 2026 Steven Cutting
"""Verify check and analyse against the vendored command's own JSON for the same paths."""

import json
import os
from pathlib import Path
from typing import Any

import alliumpy
import pytest
from alliumpy._alliumpy import _run_cli

ROOT = Path(__file__).resolve().parents[3]
SMOKE = ROOT / "tests/fixtures/smoke"
CORPUS = ROOT / "tests/fixtures/parity"
COMMANDS = {"check": alliumpy.check, "analyse": alliumpy.analyse}


def command_output(
    capfd: pytest.CaptureFixture[str], command: str, paths: list[str]
) -> tuple[int, list[dict[str, Any]], str]:
    """Run the command on the process's streams; return its status, objects and stderr."""
    capfd.readouterr()
    status = _run_cli([command, *paths])
    out, err = capfd.readouterr()
    decoder = json.JSONDecoder()
    objects: list[dict[str, Any]] = []
    rest = out.lstrip()
    while rest:
        value, end = decoder.raw_decode(rest)
        objects.append(value)
        rest = rest[end:].lstrip()
    return status, objects, err


def as_command_json(report: alliumpy.Report, command: str) -> list[dict[str, Any]]:
    """Rebuild the command's JSON objects from the API's typed result."""
    return [
        {
            "command": command,
            "spec_file": file.spec_file,
            "diagnostics": [
                {
                    "code": d.code,
                    "severity": d.severity,
                    "message": d.message,
                    "location": {"file": file.spec_file, "line": d.line, "col": d.col},
                }
                for d in file.diagnostics
            ],
            "findings": [json.loads(f.json) for f in file.findings],
        }
        for file in report.files
    ]


@pytest.mark.parametrize("command", COMMANDS)
@pytest.mark.parametrize(
    "paths",
    [
        [str(SMOKE / "ok.allium")],
        [str(SMOKE / "broken.allium")],
        [str(SMOKE)],
        [str(CORPUS)],
        [str(SMOKE / "missing.allium"), str(SMOKE / "ok.allium")],
        [],
    ],
    ids=["ok", "broken", "smoke", "corpus", "unreadable-file", "no-paths"],
)
def test_results_equal_the_commands_json(
    capfd: pytest.CaptureFixture[str], command: str, paths: list[str]
) -> None:
    """Report the command's status, every object it printed, and its stderr."""
    status, objects, err = command_output(capfd, command, paths)
    report = COMMANDS[command](paths)
    assert (report.status, as_command_json(report, command), report.stderr) == (
        status,
        objects,
        err,
    )


def test_status_follows_each_commands_rule() -> None:
    """An error fails check; analyse takes its status from findings alone."""
    broken = [str(SMOKE / "broken.allium")]
    assert alliumpy.check(broken).status == 1
    assert alliumpy.analyse(broken).status == 0
    assert alliumpy.check([]).status == 2


@pytest.mark.skipif(os.name != "posix", reason="directory permissions are POSIX")
def test_an_unreadable_directory_is_skipped(tmp_path: Path) -> None:
    """Skip a directory the command cannot list, so nothing is found."""
    tmp_path.chmod(0)
    try:
        report = alliumpy.check([str(tmp_path)])
    finally:
        tmp_path.chmod(0o700)
    assert (report.status, report.files) == (2, [])


def test_help_raises_allium_error() -> None:
    """Refuse output that is not the command's reports with the stable message."""
    with pytest.raises(
        alliumpy.AlliumError,
        match=r"^the allium command printed output that is not its JSON reports$",
    ):
        alliumpy.check(["--help"])


def test_results_are_frozen_values() -> None:
    """Compare and hash results by value and refuse mutation."""
    paths = [str(CORPUS)]
    first, second = alliumpy.analyse(paths), alliumpy.analyse(paths)
    assert first == second
    assert hash(first) == hash(second)
    finding = next(f for file in first.files for f in file.findings)
    assert hash(finding) == hash(next(f for file in second.files for f in file.findings))
    with pytest.raises(AttributeError):
        first.status = 0  # type: ignore[misc]  # Exercise the read-only boundary.


def test_reprs_show_every_field() -> None:
    """Represent each result with every field in order, using Python quoting."""
    report = alliumpy.check([str(SMOKE / "broken.allium")])
    file = report.files[0]
    assert repr(report) == f"Report(status=1, files=[{file!r}], stderr='')"
    assert repr(file) == (
        f"FileReport(spec_file={file.spec_file!r}, diagnostics=[{file.diagnostics[0]!r}], "
        "findings=[])"
    )
    corpus = alliumpy.analyse([str(CORPUS)])
    finding = next(f for in_file in corpus.files for f in in_file.findings)
    assert repr(finding) == (
        f"Finding(type={finding.type!r}, summary={finding.summary!r}, "
        f"affected_entities={finding.affected_entities!r}, json={finding.json!r})"
    )


def test_list_of_strings_is_required() -> None:
    """Reject a bare string, which would otherwise be read as its characters."""
    with pytest.raises(TypeError):
        alliumpy.check("specs")  # type: ignore[arg-type]  # Exercise runtime conversion.
