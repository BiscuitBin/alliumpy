# Copyright 2026 Steven Cutting
"""Verify the vendored allium command through the extension, on the process's streams."""

import pytest
from alliumpy._alliumpy import ALLIUM_VERSION_STRING, _run_cli


def test_version_prints_upstreams_string_on_the_process_stdout(
    capfd: pytest.CaptureFixture[str],
) -> None:
    """Upstream's --version line reaches file descriptor 1, and the status is 0."""
    assert _run_cli(["--version"]) == 0
    assert capfd.readouterr() == (ALLIUM_VERSION_STRING + "\n", "")


def test_no_arguments_exit_2_with_upstreams_message_on_stderr(
    capfd: pytest.CaptureFixture[str],
) -> None:
    """Upstream's missing-command lines reach file descriptor 2, and the status is 2."""
    assert _run_cli([]) == 2
    assert capfd.readouterr() == ("", "allium: missing command\nRun `allium --help` for usage.\n")
