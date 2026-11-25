# Copyright 2026 Steven Cutting
"""Console entry point: ``alliumpy gate``, a specification gate over check and analyse.

The gate's policy is its own (decision 0019), outside the parity invariant, which
covers the ``allium`` script only. Typer is imported here and nowhere else, so the
library and the ``allium`` script never load it.
"""

import io
import os
import signal
import sys
from collections import Counter, deque
from collections.abc import Sequence
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

from ._alliumpy import AlliumError, Diagnostic, Finding, Report, analyse, check

PASSED = 0
"""Exit status when every file was read and nothing failed the gate."""
FAILED = 1
"""Exit status when the gate failed."""
USAGE = 2
"""Exit status for a usage error, and when no specification is found."""
NO_REPORT = 3
"""Exit status when the command could not report: it panicked or printed something else."""

SEVERITIES = ("error", "warning", "info")
"""Upstream's severities, most severe first."""
ANNOTATION_LEVELS = {"error": "error", "warning": "warning", "info": "notice"}
"""The GitHub workflow command each severity becomes."""


class FailOn(StrEnum):
    """The least severe diagnostic that fails the gate."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class Format(StrEnum):
    """How the gate prints what it found."""

    TEXT = "text"
    GITHUB = "github"


app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    help="Gate Allium specifications with upstream's checker, packaged by alliumpy.",
)


@app.callback()
def root() -> None:
    """Gate Allium specifications with upstream's checker, packaged by alliumpy."""


def merged(check_report: Report, analyse_report: Report) -> dict[str, list[Diagnostic]]:
    """Each file's diagnostics, check's in order, then any of analyse's check lacks.

    Both commands report the parser's diagnostics, so one that analyse repeats is
    printed once; a diagnostic one command reports twice stays twice. Files the
    commands display alike, such as two names that are not UTF-8, share one entry.
    """
    files: dict[str, list[Diagnostic]] = {}
    for file in check_report.files:
        files.setdefault(file.spec_file, []).extend(file.diagnostics)
    repeated: dict[str, list[Diagnostic]] = {}
    for file in analyse_report.files:
        repeated.setdefault(file.spec_file, []).extend(file.diagnostics)
    for spec_file, analysed in repeated.items():
        diagnostics = files.setdefault(spec_file, [])
        unmatched = Counter(diagnostics)
        for d in analysed:
            if unmatched[d]:
                unmatched[d] -= 1
            else:
                diagnostics.append(d)
    return files


def printable(text: str) -> str:
    """Escape each character that is not printable, so a line stays one line.

    A file name may hold a line break; unescaped, the line after it could start
    with ``::`` and run as a GitHub Actions workflow command.
    """
    return "".join(
        c if c.isprintable() else c.encode("unicode_escape").decode("ascii") for c in text
    )


def text_line(text: str) -> str:
    """One line of text output that the GitHub Actions runner cannot read as a command.

    Beyond :func:`printable`, the runner runs ``::command::`` at a line's start after
    leading whitespace, and the legacy ``##[command]`` anywhere in it; their first
    ``:`` and their ``[`` are written as backslash escapes.
    """
    line = printable(text).replace("##[", "##\\x5b")
    stripped = line.lstrip()
    if stripped.startswith("::"):
        indent = len(line) - len(stripped)
        line = f"{line[:indent]}\\x3a{line[indent + 1 :]}"
    return line


def escape_data(text: str) -> str:
    """Escape a workflow command's message."""
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def escape_property(text: str) -> str:
    """Escape a workflow command's property value."""
    return escape_data(text).replace(":", "%3A").replace(",", "%2C")


def annotation(
    level: str,
    message: str,
    *,
    file: str | None = None,
    line: int | None = None,
    col: int | None = None,
) -> str:
    """One GitHub Actions workflow command, such as ``::error file=f,line=1,col=2::message``."""
    properties = [
        f"{key}={escape_property(str(value))}"
        for key, value in (("file", file), ("line", line), ("col", col))
        if value is not None
    ]
    joined = f" {','.join(properties)}" if properties else ""
    return f"::{level}{joined}::{escape_data(message)}"


def diagnostic_line(spec_file: str, d: Diagnostic, output: Format) -> str:
    """One diagnostic as ``file:line:col: severity: message [code]``, or its annotation."""
    message = f"{d.message} [{d.code}]" if d.code else d.message
    if output is Format.GITHUB:
        level = ANNOTATION_LEVELS[d.severity]
        return annotation(level, message, file=spec_file, line=d.line, col=d.col)
    return text_line(f"{spec_file}:{d.line}:{d.col}: {d.severity}: {message}")


def finding_line(spec_file: str, f: Finding, output: Format, *, failing: bool) -> str:
    """One finding as ``file: finding type: summary``, or its file-only annotation."""
    message = f"finding {f.type}: {f.summary}"
    if output is Format.GITHUB:
        return annotation("error" if failing else "notice", message, file=spec_file)
    return text_line(f"{spec_file}: {message}")


def unsearchable(paths: list[str]) -> list[str]:
    """Each directory under paths that cannot be searched, as ``directory: reason``.

    Upstream's command skips a directory it cannot list, or cannot tell is one,
    without a word, so a specification inside would go unchecked. This walks the
    tree as upstream does, following symbolic links to directories, and names
    each. An entry upstream reads as a file, such as an ``.allium`` file it cannot
    stat, is left to the command, which names it if it cannot be read.
    """
    found: list[str] = []
    pending = deque(path for path in paths if Path(path).is_dir())
    while pending:
        directory = pending.popleft()
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    try:
                        if entry.is_dir():
                            pending.append(entry.path)
                    except OSError as error:
                        if Path(entry.name).suffix != ".allium":
                            found.append(not_searched(entry.path, error))
        except FileNotFoundError:
            continue
        except OSError as error:
            found.append(not_searched(directory, error))
    return found


def not_searched(path: str, error: OSError) -> str:
    """Name a directory the gate could not search, and why."""
    return f"{path}: cannot be searched for .allium files: {error.strerror or error}"


def reports(paths: list[str], *, nothing_found_fails: bool) -> tuple[Report, Report] | None:
    """Check's and analyse's reports, or exit as the gate's statuses say.

    None when check found no ``.allium`` file but a directory could not be
    searched: the gate then fails on that directory rather than finding nothing.
    """
    try:
        check_report = check(paths)
        if check_report.status == USAGE:
            if nothing_found_fails:
                return None
            typer.echo(check_report.stderr, err=True, nl=False)
            raise typer.Exit(USAGE)
        analyse_report = analyse(paths)
        if analyse_report.status == USAGE:
            # A file removed between the two runs leaves analyse none to read.
            typer.echo(analyse_report.stderr, err=True, nl=False)
            raise typer.Exit(USAGE)
    except UnicodeEncodeError:
        # A POSIX path that is not UTF-8 reaches Python surrogate-escaped; upstream
        # reads its arguments as UTF-8 and cannot take it.
        typer.echo("alliumpy gate: a path is not valid UTF-8", err=True)
        raise typer.Exit(USAGE) from None
    except AlliumError as error:
        typer.echo(f"alliumpy gate: {error}", err=True)
        raise typer.Exit(NO_REPORT) from None
    return check_report, analyse_report


@app.command()
def gate(
    paths: Annotated[
        list[str],
        typer.Argument(help="Specification files, or directories searched for .allium files."),
    ],
    *,
    fail_on: Annotated[
        FailOn,
        typer.Option(help="The least severe diagnostic that fails the gate."),
    ] = FailOn.WARNING,
    fail_on_findings: Annotated[
        bool,
        typer.Option("--fail-on-findings", help="Fail on any analyse finding too."),
    ] = False,
    output: Annotated[
        Format,
        typer.Option("--format", help="text, or github for GitHub Actions annotations."),
    ] = Format.TEXT,
) -> None:
    """Run upstream's check and analyse on PATHS; by default, fail on any error or warning.

    Exit status:
    0 passed;
    1 a diagnostic at or above --fail-on, a finding under --fail-on-findings,
    or a file or directory that cannot be read;
    2 a usage error, a path that is not UTF-8, or no .allium file found;
    3 the checker could not report.
    """
    unsearched = unsearchable(paths)
    results = reports(paths, nothing_found_fails=bool(unsearched))
    ran = results or ()
    # A file can become unreadable between the runs, so either stderr may name it.
    unreadable = list(
        dict.fromkeys(unsearched + [line for report in ran for line in report.stderr.splitlines()])
    )
    for line in unreadable:
        if output is Format.GITHUB:
            typer.echo(annotation("error", line))
        else:
            typer.echo(text_line(f"error: {line}"), err=True)
    diagnostics = merged(*results) if results else {}
    findings: dict[str, list[Finding]] = {}
    for file in results[1].files if results else []:
        findings.setdefault(file.spec_file, []).extend(file.findings)
    counts = dict.fromkeys(SEVERITIES, 0)
    for spec_file, file_diagnostics in diagnostics.items():
        for d in file_diagnostics:
            counts[d.severity] += 1
            typer.echo(diagnostic_line(spec_file, d, output))
        for f in findings.get(spec_file, []):
            typer.echo(finding_line(spec_file, f, output, failing=fail_on_findings))
    found = sum(len(f) for f in findings.values())
    failing = SEVERITIES[: SEVERITIES.index(fail_on.value) + 1]
    failed = (
        bool(unreadable)
        or any(counts[severity] for severity in failing)
        or (fail_on_findings and found > 0)
    )
    typer.echo(
        f"alliumpy gate: {len(results[0].files) if results else 0} files, "
        f"{counts['error']} errors, "
        f"{counts['warning']} warnings, {counts['info']} info, {found} findings, "
        f"{len(unreadable)} unreadable: {'failed' if failed else 'passed'}"
    )
    raise typer.Exit(FAILED if failed else PASSED)


def run(argv: Sequence[str]) -> int:
    """Run the ``alliumpy`` command on ``argv`` and return its exit status."""
    args = list(argv)
    try:
        app(args=args, prog_name="alliumpy")
    except SystemExit as exit_:
        if exit_.code is None:
            return PASSED
        return exit_.code if isinstance(exit_.code, int) else FAILED
    return PASSED


def main() -> int:
    """Console entry point: run on this process's arguments and return the exit status."""
    # As _cli.py does: the checker runs with the interpreter released, so Python's
    # handler would wait for it and then exit 1, which reads as a failed gate. An
    # inherited SIG_IGN stays ignored.
    if signal.getsignal(signal.SIGINT) is not signal.SIG_IGN:
        signal.signal(signal.SIGINT, signal.SIG_DFL)
    # Upstream's messages are UTF-8 and can hold characters such as an arrow that a
    # legacy console encoding, cp1252 on a Windows runner, lacks; escaping them keeps
    # a passing gate from crashing with status 1.
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(errors="backslashreplace")
    return run(sys.argv[1:])
