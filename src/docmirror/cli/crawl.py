"""`docmirror crawl`: implemented in a later phase."""

from __future__ import annotations

from typing import Any

from docmirror.cli.common import fail
from docmirror.exit_codes import ExitCode


def run_crawl(*args: Any, **kwargs: Any) -> ExitCode:  # noqa: ANN401 - placeholder signature
    """Not yet implemented: exits 2 with a message naming the command."""
    del args, kwargs
    fail("crawl is not implemented yet", ExitCode.USAGE)
