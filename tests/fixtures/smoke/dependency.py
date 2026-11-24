# Copyright 2026 Steven Cutting
"""Check the installed wheel's runtime dependency, apart from smoke.py.

smoke.py also runs in the release workflow, which installs the wheel alone with
--no-deps; this script runs where the dependency is installed too: the local wheel
smoke, which takes Typer from the locked pixi environment, and CI's Python 3.11 job.
"""

import re
import sys
from importlib.metadata import requires, version
from pathlib import Path

import alliumpy

# The package is the venv's own wheel, not the pixi environment's editable copy, and
# its one runtime dependency (decision 0019) is declared and satisfied.
assert Path(alliumpy.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
declared = [r for r in requires("alliumpy") or [] if r.startswith("typer")]
assert len(declared) == 1, declared
match = re.fullmatch(r"typer>=([\d.]+),<([\d.]+)", declared[0])
assert match is not None, declared[0]


def release(text: str) -> tuple[int, ...]:
    """Parse a dotted release such as 0.29.2 into comparable integers."""
    return tuple(int(part) for part in text.split("."))


floor, ceiling = match.groups()
assert release(floor) <= release(version("typer")) < release(ceiling), version("typer")
