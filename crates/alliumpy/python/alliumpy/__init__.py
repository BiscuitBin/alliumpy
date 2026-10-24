# Copyright 2026 Steven Cutting
"""Allium parser diagnostics for Python."""

from importlib.metadata import version

from ._alliumpy import ALLIUM_VERSION, AlliumError, Diagnostic, parse

__version__ = version("alliumpy")
__all__ = ["parse", "Diagnostic", "AlliumError", "ALLIUM_VERSION"]  # noqa: RUF022 - Order fixed by CONVENTIONS §9.
