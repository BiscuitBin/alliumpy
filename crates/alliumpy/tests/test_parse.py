# Copyright 2026 Steven Cutting
"""Verify the public Python API against independent upstream CLI results."""

from importlib.metadata import version
from pathlib import Path
from unittest import TestCase

import alliumpy
import alliumpy._alliumpy as native

FIXTURES = Path(__file__).resolve().parents[3] / "tests/fixtures/smoke"
BROKEN_MESSAGE = (
    "expected declaration (entity, rule, enum, value, config, surface, actor, given, "
    "default, variant, deferred, use, open question, contract, invariant), found '?'"
)
DiagnosticValue = tuple[int, int, str, str, str | None]
BROKEN: list[DiagnosticValue] = [(5, 9, "error", BROKEN_MESSAGE, None)]

# Parsing


class TestParsing(TestCase):
    """Compare smoke inputs with allium-cli 3.6.1's check output."""

    def test_fixtures(self) -> None:
        """Read both repository fixtures regardless of the working directory."""
        for filename, expected in (("ok.allium", []), ("broken.allium", BROKEN)):
            with self.subTest(fixture=filename):
                diagnostics = alliumpy.parse((FIXTURES / filename).read_text(encoding="utf-8"))
                actual = [(d.line, d.col, d.severity, d.message, d.code) for d in diagnostics]
                assert actual == expected
                if filename == "broken.allium":
                    assert any(d.severity == "error" for d in diagnostics)

    def test_empty_source(self) -> None:
        """Preserve the reference CLI's missing-version warning on empty input."""
        actual = [(d.line, d.col, d.severity, d.message, d.code) for d in alliumpy.parse("")]
        assert actual == [
            (
                1,
                1,
                "warning",
                "missing version marker; expected '-- allium: 1' as the first line",
                None,
            ),
        ]

    def test_non_string_source(self) -> None:
        """Reject an argument pyo3 cannot convert to a source string."""
        with self.assertRaises(TypeError):  # noqa: PT027 - Ticket permits only standard-library test imports.
            alliumpy.parse(123)  # type: ignore[arg-type]  # Exercise runtime conversion.

    def test_keyword_source(self) -> None:
        """Accept the source keyword that the canonical stub promises."""
        assert alliumpy.parse(source=(FIXTURES / "ok.allium").read_text(encoding="utf-8")) == []


# Diagnostic and AlliumError


def broken_diagnostic() -> alliumpy.Diagnostic:
    """Return a diagnostic from the independently checked broken fixture."""
    return alliumpy.parse((FIXTURES / "broken.allium").read_text(encoding="utf-8"))[0]


class TestDiagnostic(TestCase):
    """Pin runtime value behavior and types that stubtest cannot infer."""

    def test_frozen(self) -> None:
        """Reject mutation of the source location."""
        diagnostic = broken_diagnostic()
        with self.assertRaises(AttributeError):  # noqa: PT027 - Ticket permits only standard-library test imports.
            diagnostic.line = 99  # type: ignore[misc]  # Exercise the read-only boundary.

    def test_repr(self) -> None:
        """Represent the independently recorded fields in their contractual order."""
        assert repr(broken_diagnostic()) == (
            f"Diagnostic(line=5, col=9, severity='error', message={BROKEN_MESSAGE!r}, code=None)"
        )

    def test_line_type(self) -> None:
        """Expose the line as an integer at runtime."""
        assert isinstance(broken_diagnostic().line, int)

    def test_col_type(self) -> None:
        """Expose the column as an integer at runtime."""
        assert isinstance(broken_diagnostic().col, int)

    def test_severity_type(self) -> None:
        """Expose severity as a plain string at runtime."""
        assert isinstance(broken_diagnostic().severity, str)

    def test_message_type(self) -> None:
        """Expose the upstream message as a string at runtime."""
        assert isinstance(broken_diagnostic().message, str)

    def test_code_type(self) -> None:
        """Expose an optional string code at runtime."""
        assert isinstance(broken_diagnostic().code, str | None)

    def test_equal_values(self) -> None:
        """Compare and hash repeated parses by diagnostic value."""
        first = broken_diagnostic()
        second = broken_diagnostic()
        assert first == second
        assert hash(first) == hash(second)

    def test_different_values(self) -> None:
        """Distinguish diagnostics from different sources."""
        assert broken_diagnostic() != alliumpy.parse("")[0]

    def test_error(self) -> None:
        """Raise and catch the public ValueError subclass with its message intact."""
        assert issubclass(alliumpy.AlliumError, ValueError)
        message = "parcel rejected"
        with self.assertRaises(alliumpy.AlliumError) as caught:  # noqa: PT027 - Standard-library imports only.
            raise alliumpy.AlliumError(message)
        assert str(caught.exception) == "parcel rejected"


# Versions and __all__


def test_version_constants() -> None:
    """Identify the pinned parser and its complete native version line."""
    assert alliumpy.ALLIUM_VERSION == "3.6.1"
    assert native.ALLIUM_VERSION_STRING.startswith("allium " + alliumpy.ALLIUM_VERSION)


def test_package_version() -> None:
    """Match installed package metadata while retaining the upstream prefix."""
    assert alliumpy.__version__.startswith(alliumpy.ALLIUM_VERSION)
    assert alliumpy.__version__ == version("alliumpy")


def test_exports() -> None:
    """Resolve every declared re-export and keep the native version line private."""
    assert set(alliumpy.__all__) == {"ALLIUM_VERSION", "AlliumError", "Diagnostic", "parse"}
    for name in alliumpy.__all__:
        assert getattr(alliumpy, name) is not None
    assert not hasattr(alliumpy, "ALLIUM_VERSION_STRING")
