# Copyright 2026 Steven Cutting
"""Native Allium parser API."""

from typing import final

__all__ = [
    "ALLIUM_VERSION",
    "ALLIUM_VERSION_STRING",
    "AlliumError",
    "Diagnostic",
    "FileReport",
    "Finding",
    "Report",
    "_run_cli",
    "analyse",
    "check",
    "parse",
]

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

@final
class Finding:
    """An immutable analyse finding, as upstream's command printed it."""

    @property
    def type(self) -> str:
        """The finding's type, such as dead_transition."""
    @property
    def summary(self) -> str:
        """Upstream's one-line summary."""
    @property
    def affected_entities(self) -> list[str]:
        """The entities the finding names."""
    @property
    def json(self) -> str:
        """The finding's complete JSON object, every key the command printed included."""
    def __eq__(self, other: object, /) -> bool:
        """Compare finding values."""
    def __hash__(self) -> int:
        """Hash the finding value."""
    def __repr__(self) -> str:  # noqa: PYI029 - Every field, as Diagnostic's.
        """Represent every field using Python quoting."""

@final
class FileReport:
    """The command's immutable report on one specification file."""

    @property
    def spec_file(self) -> str:
        """The path as the command printed it."""
    @property
    def diagnostics(self) -> list[Diagnostic]:
        """The file's diagnostics, in the command's order."""
    @property
    def findings(self) -> list[Finding]:
        """The file's findings, in the command's order; check reports none."""
    def __eq__(self, other: object, /) -> bool:
        """Compare report values."""
    def __hash__(self) -> int:
        """Hash the report value."""
    def __repr__(self) -> str:  # noqa: PYI029 - Every field, as Diagnostic's.
        """Represent every field using Python quoting."""

@final
class Report:
    """What one run of allium check or allium analyse reported."""

    @property
    def status(self) -> int:
        """The command's exit status: 0, 1, or 2 when no .allium file is found."""
    @property
    def files(self) -> list[FileReport]:
        """One report per file the command read; an unreadable file has none."""
    @property
    def stderr(self) -> str:
        """What the command wrote to stderr, such as an unreadable file's error."""
    def __eq__(self, other: object, /) -> bool:
        """Compare report values."""
    def __hash__(self) -> int:
        """Hash the report value."""
    def __repr__(self) -> str:  # noqa: PYI029 - Every field, as Diagnostic's.
        """Represent every field using Python quoting."""

def check(paths: list[str]) -> Report:
    """Run upstream's allium check on paths; raise AlliumError if it panics or prints no reports."""

def analyse(paths: list[str]) -> Report:
    """Run upstream's allium analyse on paths; raise AlliumError as check does."""

def parse(source: str) -> list[Diagnostic]:
    """Return upstream's parse diagnostics in source order."""

def _run_cli(args: list[str]) -> int:
    """Run upstream's allium command on the process's stdout and stderr; return its status."""
