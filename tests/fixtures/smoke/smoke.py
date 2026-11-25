# Copyright 2026 Steven Cutting
"""Check parsing, checking and version compatibility in the isolated installed wheel."""

import pickle
from pathlib import Path

import alliumpy

fixtures = Path(__file__).resolve().parent
assert alliumpy.parse((fixtures / "ok.allium").read_text()) == []
assert alliumpy.parse((fixtures / "broken.allium").read_text())
assert alliumpy.__version__.startswith(alliumpy.ALLIUM_VERSION)
error = alliumpy.AlliumError("failure")
restored = pickle.loads(pickle.dumps(error))  # noqa: S301 - Only locally generated smoke data.
assert type(restored) is alliumpy.AlliumError
assert restored.args == error.args
assert alliumpy.check([str(fixtures / "ok.allium")]).status == 0
broken = alliumpy.check([str(fixtures / "broken.allium")])
assert broken.status == 1
assert [(d.line, d.col) for d in broken.files[0].diagnostics] == [(5, 9)]
