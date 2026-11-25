# Copyright 2026 Steven Cutting
"""Allium parser diagnostics for Python."""

from importlib.metadata import version

from ._alliumpy import (
    ALLIUM_VERSION,
    AlliumError,
    Diagnostic,
    FileReport,
    Finding,
    Report,
    analyse,
    check,
    parse,
)

__version__ = version("alliumpy")
__all__ = [  # noqa: RUF022 - Order fixed by CONVENTIONS §9, new names appended.
    "parse",
    "Diagnostic",
    "AlliumError",
    "ALLIUM_VERSION",
    "check",
    "analyse",
    "Report",
    "FileReport",
    "Finding",
]
