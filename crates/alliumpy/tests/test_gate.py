# Copyright 2026 Steven Cutting
"""Verify the alliumpy gate script's exit policy and output (decision 0019)."""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from alliumpy import _gate

ROOT = Path(__file__).resolve().parents[3]
SMOKE = ROOT / "tests/fixtures/smoke"
OK = str(SMOKE / "ok.allium")
BROKEN = str(SMOKE / "broken.allium")
CORPUS = ROOT / "tests/fixtures/parity"
EDGE_CASES = str(CORPUS / "crates/allium-parser/tests/fixtures/comprehensive-edge-cases.allium")


def run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str, str]:
    """Run the script on argv; return its status, stdout and stderr."""
    status = _gate.main(list(argv))
    out, err = capsys.readouterr()
    return status, out, err


def test_a_clean_file_passes(capsys: pytest.CaptureFixture[str]) -> None:
    """Exit 0 and say so when nothing is reported."""
    status, out, err = run(capsys, "gate", OK)
    assert (status, err) == (0, "")
    assert out == (
        "alliumpy gate: 1 files, 0 errors, 0 warnings, 0 info, 0 findings, 0 unreadable: passed\n"
    )


def test_an_error_fails_and_names_file_line_and_message(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Exit 1, printing the error once although check and analyse both report it."""
    status, out, _ = run(capsys, "gate", BROKEN)
    assert status == 1
    lines = out.splitlines()
    assert lines[0].startswith(f"{BROKEN}:5:9: error: expected declaration")
    assert len(lines) == 2
    assert lines[1].endswith("1 errors, 0 warnings, 0 info, 0 findings, 0 unreadable: failed")


def test_a_warning_fails(capsys: pytest.CaptureFixture[str]) -> None:
    """Fail on a warning alone, as the decided policy says."""
    status, out, _ = run(capsys, "gate", str(ROOT / "tests/fixtures/gate/warning.allium"))
    assert status == 1
    assert ": warning: " in out
    assert " 0 errors, 1 warnings," in out


def test_findings_and_info_report_but_do_not_fail(capsys: pytest.CaptureFixture[str]) -> None:
    """Print findings and info diagnostics and still pass."""
    status, out, _ = run(capsys, "gate", str(ROOT / "tests/fixtures/gate/finding.allium"))
    assert status == 0
    assert ": finding " in out
    assert ": info: " in out
    assert out.endswith(": passed\n")


def test_codes_are_printed(capsys: pytest.CaptureFixture[str]) -> None:
    """End a diagnostic that has a code with it in brackets."""
    _, out, _ = run(capsys, "gate", EDGE_CASES)
    assert any(line.endswith("]") and ": warning: " in line for line in out.splitlines())


def test_an_unreadable_file_fails(capsys: pytest.CaptureFixture[str]) -> None:
    """Fail on a file the command cannot read, though it reports no diagnostic."""
    missing = str(SMOKE / "missing.allium")
    status, out, err = run(capsys, "gate", missing, OK)
    assert status == 1
    assert err.startswith(f"error: {missing}: ")
    assert out.endswith(" 1 unreadable: failed\n")


def test_no_specification_found_is_status_2(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """Exit 2, apart from a failed gate, when no .allium file is found."""
    assert run(capsys, "gate", str(tmp_path)) == (2, "", "No .allium files found.\n")


def test_usage_errors_are_status_2(capsys: pytest.CaptureFixture[str]) -> None:
    """Exit 2 on no paths, an unknown option and an unknown command."""
    for argv in (["gate"], ["gate", "--bogus", OK], ["frobnicate"], []):
        assert run(capsys, *argv)[0] == 2, argv


def test_output_that_is_not_a_report_is_status_3(capsys: pytest.CaptureFixture[str]) -> None:
    """Exit 3 with the error on stderr when the command prints no reports."""
    status, out, err = run(capsys, "gate", "--", "--help")
    assert (status, out) == (3, "")
    assert err == (
        "alliumpy gate: the allium command printed output that is not its JSON reports\n"
    )


def test_help_lists_the_gate_command(capsys: pytest.CaptureFixture[str]) -> None:
    """Keep gate a subcommand, so alliumpy gate PATHS does not read gate as a path."""
    status, out, _ = run(capsys, "--help")
    assert status == 0
    assert "gate" in out
    status, out, _ = run(capsys, "gate", "--help")
    assert status == 0
    assert "PATHS" in out.upper()


def test_the_library_and_allium_script_never_import_typer() -> None:
    """Import alliumpy and the allium script without Typer, which only the gate needs."""
    code = "import sys, alliumpy, alliumpy._cli; sys.exit('typer' in sys.modules)"
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    subprocess.run([sys.executable, "-I", "-c", code], check=True, env=env)  # noqa: S603 - Fixed interpreter and code.
