# Copyright 2026 Steven Cutting
# ruff: noqa: INP001  A standalone script run by path with -I, never imported as a package.
"""Compare the wheel's allium command with upstream's, byte for byte."""

import argparse
import difflib
import os
import re
import shlex
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

DIFFERENCES = 1
HARNESS_ERROR = 2
# Upstream's check exits 1 on an error or warning; 2 means no inputs and proves nothing.
REJECTED = 1
TIMEOUT_SECONDS = 120
COMMANDS = ("check", "analyse", "parse", "plan", "model")
SINGLE_FILE_COMMANDS = ("parse", "plan", "model")
# Built from scratch so nothing in the caller's environment reaches either binary.
ENVIRONMENT = {"PATH": "/usr/bin:/bin", "TZ": "UTC", "LC_ALL": "C"}
# A `use` of a local file: the path upstream resolves against the importer's directory.
# Upstream's lexer skips whitespace, newlines and `--` comments between `use` and its string.
LOCAL_USE = re.compile(r'\buse(?:\s|--[^\n]*)*"([^"]+\.allium)"')


class HarnessError(Exception):
    """The harness cannot produce a trustworthy verdict."""


@dataclass(frozen=True)
class Outcome:
    """What one binary did with one argument list."""

    status: int
    stdout: bytes
    stderr: bytes


@dataclass(frozen=True)
class Comparison:
    """The reference's and the candidate's outcomes for one row of the matrix."""

    label: str
    reference: Outcome | None
    candidate: Outcome | None
    error: str | None

    @property
    def differs(self) -> bool:
        """Whether stdout bytes or the exit status differ, or the run failed."""
        if self.reference is None or self.candidate is None:
            return True
        return (
            self.reference.stdout != self.candidate.stdout
            or self.reference.status != self.candidate.status
        )


def check_binary(role: str, path: Path) -> Path:
    """Return a binary's resolved path, or fail closed naming its role."""
    if not path.is_absolute():
        msg = f"{role} must be an absolute path: {path}"
        raise HarnessError(msg)
    if not path.is_file() or not os.access(path, os.X_OK):
        msg = f"{role} is not an executable file: {path}"
        raise HarnessError(msg)
    return path.resolve()


def check_distinct(reference: Path, candidate: Path) -> None:
    """Refuse a candidate that is the reference by resolved path or by inode."""
    if reference == candidate or reference.samefile(candidate):
        msg = f"candidate is the reference: {candidate}"
        raise HarnessError(msg)


def corpus_files(corpus: Path) -> list[str]:
    """Return the corpus's specification files, relative and sorted; fail closed."""
    if not corpus.is_dir():
        msg = f"corpus directory does not exist: {corpus}"
        raise HarnessError(msg)
    files = []
    for path in corpus.rglob("*"):
        relative = path.relative_to(corpus).as_posix()
        # A symlink leads outside the corpus (rglob does not follow one, upstream's walk
        # does); a FIFO or a device blocks with no timeout.
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            msg = f"not a regular file or directory inside the corpus: {relative}"
            raise HarnessError(msg)
        if path.is_file() and path.suffix == ".allium":
            files.append(relative)
    if not files:
        msg = f"empty corpus: no .allium file under {corpus}"
        raise HarnessError(msg)
    return sorted(files)


def import_pairs(corpus: Path, files: list[str]) -> list[tuple[str, str]]:
    """Each (importer, target) where a corpus file `use`s another corpus file, read as text."""
    root = corpus.resolve()
    pairs = set()
    for name in files:
        text = (corpus / name).read_text(encoding="utf-8", errors="replace")
        for use in LOCAL_USE.findall(text):
            target = ((corpus / name).parent / use).resolve()
            if target.is_file() and target.is_relative_to(root) and target != root / name:
                pairs.add((name, target.relative_to(root).as_posix()))
    return sorted(pairs)


def matrix(
    files: list[str], pairs: list[tuple[str, str]], corpus: Path, empty: Path
) -> list[list[str]]:
    """Every argument list both binaries run, in order; T13's README tabulates it."""
    first, last = files[0], files[-1]
    rows = [[command, name] for name in files for command in COMMANDS]
    for command in ("check", "analyse"):
        rows += [
            [command, corpus.name],
            [command, first, last],
            [command, corpus.name, first],
            [command, str(corpus.parent / first)],
        ]
        for importer, target in pairs:
            rows += [[command, importer, target], [command, target, importer]]
    rows += [
        ["check"],
        ["analyse"],
        ["check", "does-not-exist.allium"],
        ["analyse", "does-not-exist.allium"],
        ["check", "does-not-exist.txt"],
        ["check", str(empty)],
        ["analyse", str(empty)],
        [],
        ["help"],
        ["-h"],
        ["--help"],
        ["-V"],
        ["--version"],
        ["--version", "extra"],
        ["frobnicate"],
        ["help", "frobnicate"],
    ]
    rows += [["help", command] for command in COMMANDS]
    rows += [[command, flag] for command in COMMANDS for flag in ("--help", "-h")]
    rows += [[command, first, "--help"] for command in COMMANDS]
    for command in SINGLE_FILE_COMMANDS:
        rows += [[command], [command, first, last], [command, "does-not-exist.allium"]]
    return rows


def placeholder(arg: str, corpus: Path, empty: Path) -> str:
    """One argument as a label shows it, independent of where the corpus lives."""
    if arg == str(empty):
        return "<empty directory>"
    if arg.startswith(f"{corpus}/"):
        return "<absolute corpus>/" + arg.removeprefix(f"{corpus}/")
    if arg == corpus.name:
        return "<corpus>"
    if arg.startswith(f"{corpus.name}/"):
        return "<corpus>/" + arg.removeprefix(f"{corpus.name}/")
    return arg


def label(args: list[str], corpus: Path, empty: Path) -> str:
    """How a row is named in the output, with the corpus and the empty directory as placeholders."""
    shown = [placeholder(arg, corpus, empty) for arg in args]
    return " ".join(shown) if shown else "(no arguments)"


def execute(binary: Path, args: list[str], workdir: Path) -> Outcome:
    """Run one binary from the corpus's parent, never inside it, with no input and a fixed env."""
    completed = subprocess.run(  # noqa: S603  The binary is a validated absolute path; no shell.
        [str(binary), *args],
        cwd=workdir,
        env=ENVIRONMENT,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        timeout=TIMEOUT_SECONDS,
        check=False,
    )
    return Outcome(completed.returncode, completed.stdout, completed.stderr)


def compare(
    reference: Path, candidate: Path, args: list[str], workdir: Path, name: str
) -> Comparison:
    """Run both binaries on one row; any failure to run counts as a difference."""
    try:
        return Comparison(
            name,
            execute(reference, args, workdir),
            execute(candidate, args, workdir),
            None,
        )
    except Exception as error:  # noqa: BLE001  Any failure is reported as a difference, never skipped.
        return Comparison(name, None, None, f"{type(error).__name__}: {error}")


def notes(comparison: Comparison) -> list[str]:
    """What differed in one comparison, in the order the line prints it."""
    ref, cand = comparison.reference, comparison.candidate
    if ref is None or cand is None:
        return [f"could not run: {comparison.error}"]
    found = []
    if ref.stdout != cand.stdout:
        found.append("stdout differs")
    if ref.status != cand.status:
        found.append(f"exit status: reference {ref.status}, candidate {cand.status}")
    if ref.stderr != cand.stderr:
        found.append("stderr differs, reported only")
    return found


def report(comparison: Comparison) -> None:
    """Print one line for one comparison."""
    verdict = "DIFFER" if comparison.differs else "same"
    ref = comparison.reference
    observed = f" [reference: exit {ref.status}, stdout {len(ref.stdout)} bytes]" if ref else ""
    found = notes(comparison)
    suffix = f" ({'; '.join(found)})" if found else ""
    sys.stdout.write(f"{verdict:<8}{comparison.label}{observed}{suffix}\n")


def positive_control(reference: Path, files: list[str], workdir: Path) -> str:
    """The first corpus file the reference's check rejects, observed now; fail closed."""
    for name in files:
        try:
            status = execute(reference, ["check", name], workdir).status
        except (OSError, subprocess.SubprocessError) as error:
            msg = f"positive control: the reference could not run: {error}"
            raise HarnessError(msg) from error
        if status == REJECTED:
            return name
    msg = (
        "positive control: the reference's check exits 1 on no corpus file;"
        " copy tests/fixtures/smoke/broken.allium into <corpus>/alliumpy/ and rerun"
    )
    raise HarnessError(msg)


def show_first_difference(comparisons: list[Comparison]) -> None:
    """Print a unified diff of the first differing stdout pair, decoded for display only."""
    for comparison in comparisons:
        ref, cand = comparison.reference, comparison.candidate
        if ref is None or cand is None or ref.stdout == cand.stdout:
            continue
        diff = difflib.unified_diff(
            ref.stdout.decode(errors="replace").splitlines(keepends=True),
            cand.stdout.decode(errors="replace").splitlines(keepends=True),
            fromfile=f"reference: {comparison.label}",
            tofile=f"candidate: {comparison.label}",
        )
        sys.stdout.writelines(diff)
        return


def wrapper(directory: Path, name: str, candidate: Path, tail: str) -> Path:
    """Write an executable script that runs the candidate, then the given shell lines."""
    path = directory / name
    path.write_text(f'#!/bin/sh\n{shlex.quote(str(candidate))} "$@"\n{tail}', encoding="utf-8")
    path.chmod(0o755)
    return path


def negative_controls(
    reference: Path, candidate: Path, control: str, workdir: Path, name: str
) -> list[str]:
    """Prove the comparison sees a wrong stdout and a wrong exit status; fail closed.

    Returns the lines to print, so that nothing else is printed before both fired.
    """
    fired_lines = []
    with tempfile.TemporaryDirectory() as scratch:
        directory = Path(scratch)
        controls = (
            (
                "candidate plus one byte",
                wrapper(
                    directory, "plus-one-byte", candidate, 'status=$?\nprintf x\nexit "$status"\n'
                ),
                "stdout differs",
            ),
            (
                "candidate forced to exit 0",
                wrapper(directory, "exit-zero", candidate, "exit 0\n"),
                "exit status: ",
            ),
        )
        for title, script, expected in controls:
            comparison = compare(reference, script, ["check", control], workdir, name)
            found = notes(comparison)
            heading = f"negative control: {title}, {comparison.label}"
            if not comparison.differs or not any(note.startswith(expected) for note in found):
                msg = f"{heading}: did not fire ({'; '.join(found) or 'no difference'})"
                raise HarnessError(msg)
            fired = next(note for note in found if note.startswith(expected))
            fired_lines.append(f"{heading}: fired ({fired})\n")
    return fired_lines


def run(reference: Path, candidate: Path, corpus: Path) -> int:
    """Run the matrix, print the result and return the exit status."""
    names = corpus_files(corpus)
    files = [f"{corpus.name}/{name}" for name in names]
    pairs = [
        (f"{corpus.name}/{importer}", f"{corpus.name}/{target}")
        for importer, target in import_pairs(corpus, names)
    ]
    workdir = corpus.parent
    with tempfile.TemporaryDirectory() as scratch:
        empty = Path(scratch)
        control = positive_control(reference, files, workdir)
        control_label = label(["check", control], corpus, empty)
        sys.stdout.write(f"positive control: {control_label} exits 1 under the reference\n")
        comparisons = [
            compare(reference, candidate, args, workdir, label(args, corpus, empty))
            for args in matrix(files, pairs, corpus, empty)
        ]
    if not comparisons:
        msg = "zero comparisons: nothing was compared"
        raise HarnessError(msg)
    fired = negative_controls(reference, candidate, control, workdir, control_label)
    for comparison in comparisons:
        report(comparison)
    differ = sum(comparison.differs for comparison in comparisons)
    sys.stdout.write(f"{len(comparisons)} compared, {differ} differ\n")
    show_first_difference(comparisons)
    sys.stdout.writelines(fired)
    return DIFFERENCES if differ else 0


def main(argv: list[str]) -> int:
    """Run the parity comparison and return the process exit status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--corpus", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        reference = check_binary("reference", args.reference)
        candidate = check_binary("candidate", args.candidate)
        check_distinct(reference, candidate)
        return run(reference, candidate, args.corpus.resolve())
    except HarnessError as error:
        sys.stderr.write(f"parity: {error}\n")
        return HARNESS_ERROR


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
