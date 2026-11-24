# Copyright 2026 Steven Cutting
"""Console entry point: ``alliumpy gate``, a specification gate over check and analyse.

The gate's policy is its own (decision 0019), outside the parity invariant, which
covers the ``allium`` script only. Typer is imported here and nowhere else, so the
library and the ``allium`` script never load it.
"""

import sys
from collections.abc import Sequence
from typing import Annotated

import typer

from ._alliumpy import AlliumError, Diagnostic, Finding, Report, analyse, check

PASSED = 0
"""Exit status when no file has an error or a warning and every file was read."""
FAILED = 1
"""Exit status when the gate failed."""
USAGE = 2
"""Exit status for a usage error, and when no specification is found."""
NO_REPORT = 3
"""Exit status when the command could not report: it panicked or printed no reports."""

FAILING = frozenset({"error", "warning"})

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
    """Each file's diagnostics from both commands, each once, check's first."""
    files: dict[str, list[Diagnostic]] = {}
    for report in (check_report, analyse_report):
        for file in report.files:
            seen = files.setdefault(file.spec_file, [])
            seen.extend(d for d in file.diagnostics if d not in seen)
    return files


def diagnostic_line(spec_file: str, d: Diagnostic) -> str:
    """One diagnostic as ``file:line:col: severity: message [code]``."""
    code = f" [{d.code}]" if d.code else ""
    return f"{spec_file}:{d.line}:{d.col}: {d.severity}: {d.message}{code}"


def finding_line(spec_file: str, f: Finding) -> str:
    """One finding as ``file: finding type: summary``."""
    return f"{spec_file}: finding {f.type}: {f.summary}"


@app.command()
def gate(
    paths: Annotated[
        list[str],
        typer.Argument(help="Specification files, or directories searched for .allium files."),
    ],
) -> None:
    """Run upstream's check and analyse on PATHS and fail on any error or warning.

    Exit status: 0 passed; 1 an error or warning, or a file that cannot be read;
    2 a usage error or no .allium file found; 3 the checker could not report.
    Findings and info diagnostics are reported but do not fail the gate.
    """
    try:
        check_report = check(paths)
        analyse_report = analyse(paths)
    except AlliumError as error:
        typer.echo(f"alliumpy gate: {error}", err=True)
        raise typer.Exit(NO_REPORT) from None
    if check_report.status == USAGE:
        typer.echo(check_report.stderr, err=True, nl=False)
        raise typer.Exit(USAGE)
    unreadable = check_report.stderr.splitlines()
    for line in unreadable:
        typer.echo(f"error: {line}", err=True)
    diagnostics = merged(check_report, analyse_report)
    findings = {file.spec_file: file.findings for file in analyse_report.files}
    counts = dict.fromkeys(("error", "warning", "info"), 0)
    for spec_file, file_diagnostics in diagnostics.items():
        for d in file_diagnostics:
            counts[d.severity] += 1
            typer.echo(diagnostic_line(spec_file, d))
        for f in findings.get(spec_file, []):
            typer.echo(finding_line(spec_file, f))
    failed = bool(unreadable) or any(counts[severity] for severity in FAILING)
    typer.echo(
        f"alliumpy gate: {len(diagnostics)} files, {counts['error']} errors, "
        f"{counts['warning']} warnings, {counts['info']} info, "
        f"{sum(len(f) for f in findings.values())} findings, "
        f"{len(unreadable)} unreadable: {'failed' if failed else 'passed'}"
    )
    raise typer.Exit(FAILED if failed else PASSED)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ``alliumpy`` command on ``argv`` (default: this process's) and return its status."""
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        app(args=args, prog_name="alliumpy")
    except SystemExit as exit_:
        if exit_.code is None:
            return PASSED
        return exit_.code if isinstance(exit_.code, int) else FAILED
    return PASSED
