# Copyright 2026 Steven Cutting
"""Verify the alliumpy gate script's exit policy and output (decision 0019)."""

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import alliumpy
import pytest
from alliumpy import Diagnostic, Finding, Report, _gate

ROOT = Path(__file__).resolve().parents[3]
SMOKE = ROOT / "tests/fixtures/smoke"
OK = str(SMOKE / "ok.allium")
BROKEN = str(SMOKE / "broken.allium")
CORPUS = ROOT / "tests/fixtures/parity"
EDGE_CASES = str(CORPUS / "crates/allium-parser/tests/fixtures/comprehensive-edge-cases.allium")


def run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str, str]:
    """Run the script on argv; return its status, stdout and stderr."""
    status = _gate.run(argv)
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
    """Exit 3 with the error on stderr when the command prints output other than its reports."""
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


# Policy flags and annotations (ticket 03)

GATE = ROOT / "tests/fixtures/gate"
ERROR = str(GATE / "error.allium")
WARNING = str(GATE / "warning.allium")
FINDING = str(GATE / "finding.allium")


@pytest.mark.parametrize(
    ("flags", "expected"),
    [
        # Fixture order: error, warning, info with three findings.
        (["--fail-on", "error"], (1, 0, 0)),
        (["--fail-on", "warning"], (1, 1, 0)),
        ([], (1, 1, 0)),
        (["--fail-on", "info"], (1, 1, 1)),
        (["--fail-on", "error", "--fail-on-findings"], (1, 0, 1)),
    ],
    ids=["error", "warning", "default-is-warning", "info", "error-and-findings"],
)
def test_fail_on_sets_the_threshold(
    capsys: pytest.CaptureFixture[str], flags: list[str], expected: tuple[int, int, int]
) -> None:
    """Fail at or above the chosen severity, and on findings only when asked."""
    statuses = tuple(run(capsys, "gate", *flags, path)[0] for path in (ERROR, WARNING, FINDING))
    assert statuses == expected


def test_an_unreadable_file_fails_under_every_threshold(capsys: pytest.CaptureFixture[str]) -> None:
    """Fail on a file the command cannot read whatever --fail-on says."""
    for threshold in ("error", "warning", "info"):
        assert (
            run(capsys, "gate", "--fail-on", threshold, str(SMOKE / "missing.allium"), OK)[0] == 1
        )


def test_an_unknown_threshold_is_a_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    """Refuse a --fail-on or --format value outside the choices with status 2."""
    assert run(capsys, "gate", "--fail-on", "fatal", OK)[0] == 2
    assert run(capsys, "gate", "--format", "json", OK)[0] == 2


def test_github_format_annotates_each_diagnostic_and_finding(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Print one workflow command per diagnostic, with file, line and column."""
    status, out, _ = run(capsys, "gate", "--format", "github", ERROR, FINDING)
    assert status == 1
    lines = out.splitlines()
    assert lines[0].startswith(f"::error file={ERROR},line=5,col=1::expected declaration")
    assert lines[1] == (
        f"::notice file={FINDING},line=8,col=5::"
        "Field 'Parcel.note' is declared but not referenced elsewhere. [allium.field.unused]"
    )
    findings = [line for line in lines if line.startswith(f"::notice file={FINDING}::finding ")]
    assert len(findings) == 3
    assert lines[-1].endswith(": failed")


def test_github_format_marks_failing_findings_as_errors(capsys: pytest.CaptureFixture[str]) -> None:
    """Annotate a finding as an error when findings fail the gate."""
    _, out, _ = run(capsys, "gate", "--format", "github", "--fail-on-findings", FINDING)
    assert f"::error file={FINDING}::finding missing_producer: " in out


def test_github_format_annotates_an_unreadable_file(capsys: pytest.CaptureFixture[str]) -> None:
    """Report an unreadable file as an error annotation on stdout."""
    missing = str(SMOKE / "missing.allium")
    _, out, err = run(capsys, "gate", "--format", "github", missing, OK)
    assert err == ""
    assert out.startswith(f"::error::{missing}: ")


def test_annotations_escape_workflow_command_syntax() -> None:
    """Escape the data and the properties as GitHub's workflow commands require."""
    assert _gate.annotation("warning", "a%b\r\nc", file="x,y:z.allium", line=1, col=2) == (
        "::warning file=x%2Cy%3Az.allium,line=1,col=2::a%25b%0D%0Ac"
    )
    assert _gate.annotation("notice", "m") == "::notice::m"


def test_a_path_that_is_not_utf8_is_a_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    """Exit 2, not the failed gate's 1, on a surrogate-escaped POSIX path."""
    assert run(capsys, "gate", "\udcff.allium") == (
        2,
        "",
        "alliumpy gate: a path is not valid UTF-8\n",
    )


def test_analyses_repeat_of_a_diagnostic_is_printed_once() -> None:
    """Drop the copy of a check diagnostic that analyse repeats, keeping check's order."""
    checked = alliumpy.check([BROKEN])
    assert _gate.merged(checked, alliumpy.analyse([BROKEN])) == {
        BROKEN: list(checked.files[0].diagnostics)
    }


def test_a_legacy_stdout_encoding_does_not_fail_the_gate() -> None:
    """Pass a clean file whose finding's arrow cp1252 lacks, as on a Windows runner."""
    code = (
        "import sys; from alliumpy._gate import main; "
        "sys.argv = ['alliumpy', 'gate', sys.argv[1]]; sys.exit(main())"
    )
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["PYTHONIOENCODING"] = "cp1252"
    result = subprocess.run(  # noqa: S603 - Fixed interpreter and code.
        [sys.executable, "-P", "-c", code, FINDING], env=env, capture_output=True, check=False
    )
    assert (result.returncode, result.stderr) == (0, b"")
    assert b"\\u2192" in result.stdout


# Copilot's review of PR #51

POSIX_ONLY = pytest.mark.skipif(os.name != "posix", reason="Windows refuses these file names.")


def test_printable_escapes_what_would_break_a_line() -> None:
    """Escape control, separator and surrogate characters; keep printable text."""
    assert _gate.printable("a\nb\r\t\x1b\x7f\N{LINE SEPARATOR}\udcff \N{RIGHTWARDS ARROW}") == (
        "a\\nb\\r\\t\\x1b\\x7f\\u2028\\udcff \N{RIGHTWARDS ARROW}"
    )


@POSIX_ONLY
def test_text_output_cannot_forge_a_workflow_command(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """Escape a newline in a file name, so no text line starts a workflow command."""
    try:
        forged = tmp_path / "x\n::error::forged.allium"
        forged.write_text(Path(BROKEN).read_text(encoding="utf-8"), encoding="utf-8")
    except OSError:
        pytest.skip("the file system refuses a newline in a file name")
    status, out, err = run(capsys, "gate", str(tmp_path))
    assert status == 1
    lines = (out + err).splitlines()
    assert not [line for line in lines if line.startswith("::")]
    assert "x\\n::error::forged.allium:5:9: error: " in out


def analyse_on(monkeypatch: pytest.MonkeyPatch, paths: list[str]) -> None:
    """Make the gate's analyse run on other paths, as when a file changes between runs."""
    monkeypatch.setattr(_gate, "analyse", lambda _: alliumpy.analyse(paths))


def test_a_file_only_analyse_cannot_read_fails(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Fail on a file that check read and analyse could not, naming it once."""
    missing = str(SMOKE / "missing.allium")
    analyse_on(monkeypatch, [missing, OK])
    status, out, err = run(capsys, "gate", OK)
    assert status == 1
    assert err.startswith(f"error: {missing}: ")
    assert len(err.splitlines()) == 1
    assert out.endswith(" 1 unreadable: failed\n")


def test_analyse_finding_no_file_is_status_2(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Exit 2 with analyse's stderr when analyse finds no .allium file though check did."""
    analyse_on(monkeypatch, [])
    assert run(capsys, "gate", OK) == (2, "", "No .allium files found.\n")


@dataclass(frozen=True)
class StandInFile:
    """A file report under a chosen displayed name."""

    spec_file: str
    diagnostics: list[Diagnostic]
    findings: list[Finding]


@dataclass(frozen=True)
class StandInReport:
    """A report whose files share one displayed name."""

    status: int
    files: list[StandInFile]
    stderr: str


def renamed(report: Report, spec_file: str) -> StandInReport:
    """The report with every file displayed as spec_file, as upstream prints two non-UTF-8 names."""
    files = [StandInFile(spec_file, f.diagnostics, f.findings) for f in report.files]
    return StandInReport(report.status, files, report.stderr)


@pytest.mark.parametrize("order", [[FINDING, OK], [OK, FINDING]], ids=["finding-first", "ok-first"])
def test_files_displayed_alike_keep_every_finding(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, order: list[str]
) -> None:
    """Keep both files' diagnostics and findings when their displayed names collide."""
    monkeypatch.setattr(_gate, "check", lambda _: renamed(alliumpy.check(order), "same.allium"))
    monkeypatch.setattr(_gate, "analyse", lambda _: renamed(alliumpy.analyse(order), "same.allium"))
    status, out, _ = run(capsys, "gate", "--fail-on-findings", "x")
    assert status == 1
    assert len([line for line in out.splitlines() if ": finding " in line]) == 3
    assert ", 3 findings," in out


@POSIX_ONLY
@pytest.mark.parametrize(
    "names", [(b"\xff", b"\xfe"), (b"\xfe", b"\xff")], ids=["finding-ff", "finding-fe"]
)
def test_non_utf8_names_that_display_alike_keep_every_finding(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, names: tuple[bytes, bytes]
) -> None:
    """Count every finding when two non-UTF-8 names both print as U+FFFD."""
    directory = os.fsencode(tmp_path)
    try:
        for name, source in zip(names, (FINDING, OK), strict=True):
            with Path(os.fsdecode(directory + b"/" + name + b".allium")).open("wb") as file:
                file.write(Path(source).read_bytes())
    except OSError:
        pytest.skip("the file system refuses a file name that is not UTF-8")
    status, out, _ = run(capsys, "gate", "--fail-on-findings", str(tmp_path))
    assert status == 1
    assert ", 3 findings," in out


# Codex's review of PR #51


def test_text_line_escapes_runner_commands() -> None:
    """Escape a leading ``::`` command, after whitespace too, and ``##[`` anywhere."""
    assert _gate.text_line("::error::a") == "\\x3a:error::a"
    assert _gate.text_line("  ::warning::a") == "  \\x3a:warning::a"
    assert _gate.text_line("a ##[warning]b ###[c") == "a ##\\x5bwarning]b ###\\x5bc"
    assert _gate.text_line("a::b: c") == "a::b: c"


def test_text_output_cannot_run_a_legacy_command(capsys: pytest.CaptureFixture[str]) -> None:
    """Escape ``##[``, which the runner reads anywhere in a line, in an unreadable file's name."""
    status, out, err = run(capsys, "gate", "##[warning]forged.allium", OK)
    assert status == 1
    assert "##[" not in out + err
    assert err.startswith("error: ##\\x5bwarning]forged.allium: ")


@POSIX_ONLY
def test_text_output_cannot_start_with_a_command(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Escape a leading ``::`` when a relative path is a workflow command."""
    name = "::error::forged.allium"
    try:
        (tmp_path / name).write_text(Path(BROKEN).read_text(encoding="utf-8"), encoding="utf-8")
    except OSError:
        pytest.skip("the file system refuses a colon in a file name")
    monkeypatch.chdir(tmp_path)
    status, out, err = run(capsys, "gate", name)
    assert status == 1
    assert not [line for line in (out + err).splitlines() if line.lstrip().startswith("::")]
    assert out.startswith("\\x3a:error::forged.allium:5:9: error: ")


PANICKED = "the allium command panicked (exit status 101)"


def test_analyse_alone_failing_to_report_is_status_3(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Exit 3 when check reports and analyse does not, printing nothing on stdout."""

    def refuse(_: list[str]) -> Report:
        raise alliumpy.AlliumError(PANICKED)

    monkeypatch.setattr(_gate, "analyse", refuse)
    status, out, err = run(capsys, "gate", OK)
    assert (status, out) == (3, "")
    assert err == f"alliumpy gate: {PANICKED}\n"
