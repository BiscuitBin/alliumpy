"""The exit-code contract every subcommand maps its outcome to.

`0` done, `1` partial or error, `2` usage, `3` blocked, `4` quality gate. When several
apply the highest is reported, which `highest` computes.
"""

from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    """Process exit statuses, ordered so that `max` picks the most severe."""

    OK = 0
    PARTIAL = 1
    USAGE = 2
    BLOCKED = 3
    QUALITY = 4


def highest(*codes: ExitCode) -> ExitCode:
    """The most severe of several applicable codes.

    >>> highest(ExitCode.PARTIAL, ExitCode.BLOCKED, ExitCode.OK)
    <ExitCode.BLOCKED: 3>
    """
    return max(codes, default=ExitCode.OK)
