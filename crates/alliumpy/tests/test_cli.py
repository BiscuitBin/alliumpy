# Copyright 2026 Steven Cutting
"""Verify the installed allium command where the parity corpus cannot reach.

Runs under `just parity`, which sets ALLIUMPY_SMOKE_BIN to the smoke venv's allium.
Nothing here imports alliumpy: every Python-side value comes from the smoke venv's own
interpreter, as JSON. Each expectation is the reference allium-cli 3.6.1's, and cites
the S01 note that records it (tickets/S01-cli-strategy-spike.md).
"""

import errno
import hashlib
import json
import os
import select
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

# POSIX-only, as parity is; on Windows the module skips instead of failing to collect.
pty = pytest.importorskip("pty")

ROOT = Path(__file__).resolve().parents[3]
SMOKE = ROOT / "tests/fixtures/smoke"
CORPUS = ROOT / "tests/fixtures/parity"
LIFECYCLE = "tests/fixtures/parity/crates/allium-parser/tests/fixtures/v3-lifecycle.allium"
BINARY = os.environ.get("ALLIUMPY_SMOKE_BIN")
TIMEOUT_SECONDS = 120
# A Rust program whose main panicked, as upstream's does on a failed write (S01:1072-1076).
PANIC_STATUS = 101
DiagnosticValue = tuple[int, int, str, str, str | None]

pytestmark = pytest.mark.skipif(BINARY is None, reason="ALLIUMPY_SMOKE_BIN unset; run just parity")


def binary() -> str:
    """The command under test; the module's skip mark guarantees it is set."""
    assert BINARY is not None
    return BINARY


def run(args: list[str | bytes]) -> subprocess.CompletedProcess[bytes]:
    """Run the command from the repository root with no input."""
    return subprocess.run(  # noqa: S603  The command under test, by path; no shell.
        [binary(), *args],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        timeout=TIMEOUT_SECONDS,
        check=False,
    )


def run_shell(script: str, args: list[str]) -> subprocess.CompletedProcess[bytes]:
    """Run a fixed bash script whose positional parameters are the command and args."""
    return subprocess.run(  # noqa: S603  A fixed script; the command is a positional parameter.
        ["/bin/bash", "-c", script, "bash", binary(), *args],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        timeout=TIMEOUT_SECONDS,
        check=False,
    )


def smoke_python(code: str, *args: str) -> object:
    """Run code in the smoke venv's interpreter and return the JSON it prints."""
    python = Path(binary()).parent / "python"
    completed = subprocess.run(  # noqa: S603  The smoke venv's interpreter, isolated with -I.
        [str(python), "-I", "-c", code, *args],
        capture_output=True,
        timeout=TIMEOUT_SECONDS,
        check=True,
    )
    return json.loads(completed.stdout)


def no_traceback(stderr: bytes) -> bool:
    """Whether stderr is free of a Python traceback."""
    return b"Traceback" not in stderr


# Exit status and version (S01:1109-1112)


@pytest.mark.parametrize(
    ("args", "status"),
    [
        (["check", "tests/fixtures/smoke/ok.allium"], 0),
        (["check", "tests/fixtures/smoke/broken.allium"], 1),
        ([], 2),
    ],
    ids=["ok", "broken", "no-arguments"],
)
def test_exit_status_is_upstreams(args: list[str | bytes], status: int) -> None:
    """Exit 0 on a clean file, 1 on an error and 2 with no arguments."""
    assert run(args).returncode == status


# Every corpus file parses cleanly, so the parity matrix never sees the parser-error
# status of these commands; T13 measured each on the reference allium-cli 3.6.1
# (`analyse` reports no parser error and exits 0).
@pytest.mark.parametrize(
    ("command", "status"),
    [("parse", 1), ("plan", 1), ("model", 1), ("analyse", 0)],
)
def test_a_parser_error_gives_upstreams_status(command: str, status: int) -> None:
    """On a file with a parser error, each command exits with the reference's status."""
    result = run([command, "tests/fixtures/smoke/broken.allium"])
    assert (result.returncode, no_traceback(result.stderr)) == (status, True)


def test_an_empty_directory_exits_2(tmp_path: Path) -> None:
    """A directory with no specification is "no inputs", exit 2."""
    result = run(["check", str(tmp_path)])
    assert (result.returncode, result.stdout) == (2, b"")


@pytest.mark.parametrize("flag", ["-V", "--version"])
def test_version_prints_the_version_string(flag: str) -> None:
    """Both version flags print ALLIUM_VERSION_STRING, read from the wheel, and exit 0."""
    code = (
        "import json\n"
        "from alliumpy._alliumpy import ALLIUM_VERSION_STRING\n"
        "print(json.dumps(ALLIUM_VERSION_STRING))\n"
    )
    expected = f"{smoke_python(code)}\n".encode()
    result = run([flag])
    assert (result.returncode, result.stdout, result.stderr) == (0, expected, b"")


# Failed writes (S01:981-1006, 1072-1082)


def test_a_closed_pipe_exits_101_with_upstreams_panic_line() -> None:
    """`check <corpus> | head -c 1` panics on EPIPE as upstream does, never a traceback."""
    script = '"$1" check "$2" | head -c 1 >/dev/null; exit "${PIPESTATUS[0]}"'
    result = run_shell(script, ["tests/fixtures/parity"])
    assert result.returncode == PANIC_STATUS
    assert b"failed printing to stdout: Broken pipe (os error 32)" in result.stderr
    assert no_traceback(result.stderr)


@pytest.mark.skipif(
    sys.platform != "linux",
    reason=(
        "/dev/full exists only on Linux; S01 measured on macOS, so the parity CI job on Linux"
        " is where this runs"
    ),
)
@pytest.mark.parametrize("args", [["-V"], ["check", LIFECYCLE]], ids=["version", "check"])
def test_a_full_device_exits_101_with_upstreams_panic_line(args: list[str]) -> None:
    """Writing to /dev/full panics on ENOSPC, as T13 measured the reference on Linux."""
    with Path("/dev/full").open("wb") as full:
        result = subprocess.run(  # noqa: S603  The command under test, by path; no shell.
            [binary(), *args],
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=full,
            stderr=subprocess.PIPE,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    assert result.returncode == PANIC_STATUS
    assert b"failed printing to stdout: No space left on device (os error 28)" in result.stderr
    assert no_traceback(result.stderr)


@pytest.mark.parametrize(
    ("args", "status"),
    [
        (["-V"], 0),
        (["check", "tests/fixtures/smoke/ok.allium"], 0),
        (["check", "tests/fixtures/smoke/broken.allium"], 1),
    ],
    ids=["version", "check-ok", "check-broken"],
)
def test_a_closed_stdout_writes_nowhere(args: list[str], status: int) -> None:
    """With stdout closed (`>&-`), the status is the reference's and stderr is empty (S01:1116)."""
    result = run_shell('"$@" >&-', args)
    assert (result.returncode, result.stderr) == (status, b"")


# Arguments, signals and terminals (S01:1008-1015, 1083, 1113-1118)


def test_an_argument_that_is_not_utf8_exits_101() -> None:
    """Upstream's `std::env::args` panics on such an argument; exit 101, no traceback."""
    result = run([b"check", b"\xff.allium"])
    assert (result.returncode, result.stdout) == (PANIC_STATUS, b"")
    assert b'called `Result::unwrap()` on an `Err` value: "\\xFF.allium"' in result.stderr
    assert no_traceback(result.stderr)


def release(fifo: Path) -> None:
    """Open the FIFO for writing and close it, so that a reader still blocked ends."""
    try:
        descriptor = os.open(fifo, os.O_WRONLY | os.O_NONBLOCK)
    except OSError as error:
        # No reader: the child has already ended, which is the passing case.
        if error.errno != errno.ENXIO:
            raise
    else:
        os.close(descriptor)


def test_sigint_during_a_blocked_read_kills_the_command(tmp_path: Path) -> None:
    """SIGINT two seconds in, while `check` blocks opening a FIFO, kills it at once."""
    fifo = tmp_path / "blocked.allium"
    os.mkfifo(fifo)
    child = subprocess.Popen(  # noqa: S603  The command under test, by path; no shell.
        [binary(), "check", str(fifo)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        # _cli.py restores SIGINT's default only once main() runs (T13 step 5).
        time.sleep(2)
        child.send_signal(signal.SIGINT)
        _, stderr = child.communicate(timeout=6)
        assert (child.returncode, stderr) == (-signal.SIGINT, b"")
    finally:
        release(fifo)
        if child.poll() is None:
            child.kill()
        child.communicate()


def test_sigint_inherited_as_ignored_stays_ignored(tmp_path: Path) -> None:
    """Started with SIGINT ignored, `check` survives it and ends as the reference does.

    The reference measured on PR #26: alive after the signal, then exit 0, empty stderr.
    """
    fifo = tmp_path / "blocked.allium"
    os.mkfifo(fifo)
    child = subprocess.Popen(  # noqa: S603  A fixed script; the command is a positional parameter.
        ["/bin/sh", "-c", 'trap "" INT; exec "$0" check "$1"', binary(), str(fifo)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        time.sleep(2)
        child.send_signal(signal.SIGINT)
        time.sleep(1)
        assert child.poll() is None
        descriptor = os.open(fifo, os.O_WRONLY | os.O_NONBLOCK)
        os.write(descriptor, b"-- allium: 3\n")
        os.close(descriptor)
        _, stderr = child.communicate(timeout=6)
        assert (child.returncode, stderr) == (0, b"")
    finally:
        if child.poll() is None:
            release(fifo)
            child.kill()
        child.communicate()


def on_a_terminal(args: list[str]) -> tuple[int, bytes]:
    """Run the command with stdout and stderr on one pseudo-terminal; return all it wrote."""
    primary, secondary = pty.openpty()
    try:
        child = subprocess.Popen(  # noqa: S603  The command under test, by path; no shell.
            [binary(), *args],
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=secondary,
            stderr=secondary,
        )
    finally:
        os.close(secondary)
    chunks = []
    deadline = time.monotonic() + TIMEOUT_SECONDS
    try:
        # A command that hangs with the terminal open would block os.read for ever.
        while select.select([primary], [], [], max(deadline - time.monotonic(), 0))[0]:
            chunk = os.read(primary, 65536)
            if not chunk:
                break
            chunks.append(chunk)
        else:
            child.kill()
            child.wait()
            pytest.fail(f"no end of output within {TIMEOUT_SECONDS} s; killed the command")
    except OSError as error:
        # Linux reports the closed terminal as EIO, macOS as end of file.
        if error.errno != errno.EIO:
            raise
    finally:
        os.close(primary)
    return child.wait(timeout=TIMEOUT_SECONDS), b"".join(chunks)


# What the reference wrote through on_a_terminal, recorded by T13 (S01:1008-1015 found
# the order; S01's bytes came through `script`, so they are not reused here).
TERMINAL_LENGTH = 11908
TERMINAL_SHA256 = "b6ef8035569611cd7c1a5c5340102dbcd35e3e8f650603dbde00fc9f2ad7559a"


def test_both_streams_on_a_terminal_arrive_in_the_references_order() -> None:
    """A read error on stderr, then the JSON on stdout, byte for byte as the reference."""
    status, output = on_a_terminal(["check", "does-not-exist.allium", LIFECYCLE])
    assert status == 1
    assert output.startswith(b"does-not-exist.allium: No such file or directory (os error 2)\r\n{")
    digest = hashlib.sha256(output).hexdigest()
    assert (len(output), digest) == (TERMINAL_LENGTH, TERMINAL_SHA256)


# The Python API against upstream's own conversion (T13 step 5)

PARSE_FILES = [*sorted(CORPUS.rglob("*.allium")), SMOKE / "broken.allium"]
PARSE_CODE = (
    "import json, sys\n"
    "from pathlib import Path\n"
    "from alliumpy import parse\n"
    "text = Path(sys.argv[1]).read_bytes().decode('utf-8')\n"
    "print(json.dumps([[d.line, d.col, d.severity, d.message, d.code] for d in parse(text)]))\n"
)


def api_diagnostics(path: Path) -> list[DiagnosticValue]:
    """`alliumpy.parse` of the file's bytes, decoded, in the smoke venv's interpreter."""
    values = smoke_python(PARSE_CODE, str(path))
    assert isinstance(values, list)
    return [
        (int(a), int(b), str(c), str(d), None if e is None else str(e)) for a, b, c, d, e in values
    ]


def command_output(command: str, path: Path) -> tuple[int, dict[str, list[dict[str, object]]]]:
    """The exit status and the JSON object the command prints for one file."""
    result = run([command, path.relative_to(ROOT).as_posix()])
    output = json.loads(result.stdout)
    assert isinstance(output, dict)
    return result.returncode, output


def check_diagnostics(path: Path) -> list[tuple[object, ...]]:
    """The diagnostics `check` prints for one file, in the Python API's tuple order."""
    values: list[tuple[object, ...]] = []
    for diagnostic in command_output("check", path)[1]["diagnostics"]:
        location = diagnostic["location"]
        assert isinstance(location, dict)
        values.append(
            (
                location["line"],
                location["col"],
                diagnostic["severity"],
                diagnostic["message"],
                diagnostic["code"],
            )
        )
    return values


@pytest.mark.parametrize("path", PARSE_FILES, ids=lambda path: path.relative_to(ROOT).as_posix())
def test_the_python_api_matches_the_commands_leading_diagnostics(path: Path) -> None:
    """`parse` equals the leading `check` diagnostics, and as many as `allium parse` prints.

    Upstream's `check` prints the parser's diagnostics before the analyser's.
    """
    expected = api_diagnostics(path)
    assert check_diagnostics(path)[: len(expected)] == expected
    # `allium parse` prints the parser's own diagnostics, spans and all: the count compares.
    # Its status is the reference's, as T13 measured it: 0 on every corpus file, 1 on
    # broken.allium.
    status, output = command_output("parse", path)
    assert len(output["diagnostics"]) == len(expected)
    assert status == (1 if path == SMOKE / "broken.allium" else 0)


def test_the_python_api_case_compares_at_least_one_diagnostic(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The parametrised case cannot pass on empty lists alone; print the total."""
    total = sum(len(api_diagnostics(path)) for path in PARSE_FILES)
    with capsys.disabled():
        sys.stdout.write(f"\nparse diagnostics over {len(PARSE_FILES)} files: {total}\n")
    assert total >= 1
