# Copyright 2026 Steven Cutting
"""Console entry point for the foundation's version tracer."""

import sys

from ._alliumpy import ALLIUM_VERSION_STRING


def main() -> int:
    """Print upstream's version or identify the ticket providing commands."""
    if sys.argv[1:] in (["-V"], ["--version"]):
        print(ALLIUM_VERSION_STRING)
        return 0
    print("allium: commands arrive with T13; only --version and -V are available", file=sys.stderr)
    return 2
