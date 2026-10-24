# Copyright 2026 Steven Cutting
"""Exercise the public Python API over the smoke inputs."""

from pathlib import Path

import alliumpy

FIXTURES = Path(__file__).resolve().parents[3] / "tests/fixtures/smoke"


def test_valid_source() -> None:
    """Accept the upstream-compatible module."""
    assert alliumpy.parse((FIXTURES / "ok.allium").read_text()) == []


def test_broken_source() -> None:
    """Report a located error for invalid source."""
    diagnostics = alliumpy.parse((FIXTURES / "broken.allium").read_text())
    assert diagnostics
    assert diagnostics[0].severity == "error"
    assert diagnostics[0].line >= 1


def test_diagnostic_value_semantics() -> None:
    """Preserve equality, hashing and Python's own representation conventions."""
    source = (FIXTURES / "broken.allium").read_text()
    first = alliumpy.parse(source)[0]
    second = alliumpy.parse(source)[0]
    assert first == second
    assert hash(first) == hash(second)
    assert repr(first) == (
        f"Diagnostic(line={first.line}, col={first.col}, severity={first.severity!r}, "
        f"message={first.message!r}, code={first.code!r})"
    )


def test_version_constants() -> None:
    """Identify the wrapped release independently of package metadata."""
    assert alliumpy.ALLIUM_VERSION == "3.6.1"
    assert alliumpy.__version__.startswith(alliumpy.ALLIUM_VERSION)
