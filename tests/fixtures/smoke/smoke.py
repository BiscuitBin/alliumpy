# Copyright 2026 Steven Cutting
"""Exercise the installed wheel with isolated Python."""

from pathlib import Path

import alliumpy

fixtures = Path(__file__).resolve().parent
assert alliumpy.parse((fixtures / "ok.allium").read_text()) == []
assert alliumpy.parse((fixtures / "broken.allium").read_text())
assert alliumpy.__version__.startswith(alliumpy.ALLIUM_VERSION)
