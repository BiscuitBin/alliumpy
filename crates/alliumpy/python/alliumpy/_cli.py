# Copyright 2026 Steven Cutting
"""Console entry point: upstream's allium command, vendored into the extension."""

import os
import signal
import sys

from ._alliumpy import _run_cli


def main() -> int:
    """Run upstream's command on this process's arguments and return its exit status."""
    # Upstream's binary dies on SIGINT at once; Python's handler would wait for the
    # command to finish, then print a KeyboardInterrupt traceback. An inherited
    # SIG_IGN, which Python leaves in place, stays ignored, as upstream's does.
    if signal.getsignal(signal.SIGINT) is not signal.SIG_IGN:
        signal.signal(signal.SIGINT, signal.SIG_DFL)
    # Rust's runtime points a closed standard descriptor at the null device before
    # upstream's main runs, so its output goes nowhere rather than into a file it opens.
    for fd in (0, 1, 2):
        try:
            os.fstat(fd)
        except OSError:
            null = os.open(os.devnull, os.O_RDWR)
            if null != fd:
                os.dup2(null, fd)
                os.close(null)
    status = _run_cli(sys.argv[1:])
    for stream in (sys.stdout, sys.stderr):
        if stream is not None:
            stream.flush()
    return status
