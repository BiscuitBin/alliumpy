"""Human-readable sizes and durations used in configuration values."""

from __future__ import annotations

import re
from datetime import timedelta

_SIZE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([KMGT]?i?B?)\s*$", re.IGNORECASE)
_SIZE_UNITS = {
    "": 1,
    "B": 1,
    "KB": 10**3,
    "MB": 10**6,
    "GB": 10**9,
    "TB": 10**12,
    "KIB": 2**10,
    "MIB": 2**20,
    "GIB": 2**30,
    "TIB": 2**40,
}
_DURATION = re.compile(r"(\d+(?:\.\d+)?)\s*([smhdw])", re.IGNORECASE)
_DURATION_UNITS = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}


def parse_size(value: str | int) -> int:
    """Bytes from `2GiB`, `500MB`, `1024` or an integer.

    >>> parse_size("2GiB")
    2147483648
    >>> parse_size(42)
    42
    """
    if isinstance(value, int):
        return value
    match = _SIZE.match(value)
    if match is None:
        message = f"not a size: {value!r}"
        raise ValueError(message)
    number, unit = match.groups()
    return int(float(number) * _SIZE_UNITS[unit.upper()])


def parse_duration(value: str) -> timedelta | None:
    """A timedelta from `7d`, `12h30m`, `90s`; the empty string means no duration.

    >>> parse_duration("1d12h")
    datetime.timedelta(days=1, seconds=43200)
    >>> parse_duration("") is None
    True
    """
    text = value.strip()
    if not text:
        return None
    parts = _DURATION.findall(text)
    if not parts or "".join(f"{n}{u}" for n, u in parts).lower() != re.sub(r"\s", "", text).lower():
        message = f"not a duration: {value!r}"
        raise ValueError(message)
    seconds = sum(float(number) * _DURATION_UNITS[unit.lower()] for number, unit in parts)
    return timedelta(seconds=seconds)
