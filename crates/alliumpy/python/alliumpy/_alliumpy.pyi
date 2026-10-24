# Copyright 2026 Steven Cutting
"""Native Allium parser API."""

from typing import final

__all__ = ["ALLIUM_VERSION", "ALLIUM_VERSION_STRING", "AlliumError", "Diagnostic", "parse"]

ALLIUM_VERSION: str
"""Version of the wrapped upstream parser."""
ALLIUM_VERSION_STRING: str
"""Complete upstream console version line."""

class AlliumError(ValueError):
    """An Allium operation failed."""

@final
class Diagnostic:
    """An immutable upstream diagnostic with a one-based location."""

    @property
    def line(self) -> int:
        """One-based source line."""
    @property
    def col(self) -> int:
        """One-based byte column."""
    @property
    def severity(self) -> str:
        """Error, warning or info."""
    @property
    def message(self) -> str:
        """Upstream message."""
    @property
    def code(self) -> str | None:
        """Optional upstream code."""
    def __eq__(self, other: object, /) -> bool:
        """Compare diagnostic values."""
    def __hash__(self) -> int:
        """Hash the diagnostic value."""
    def __repr__(self) -> str:  # noqa: PYI029 - CONVENTIONS §9 specifies the representation.
        """Represent every field using Python quoting."""

def parse(source: str) -> list[Diagnostic]:
    """Return upstream's parse diagnostics in source order."""
