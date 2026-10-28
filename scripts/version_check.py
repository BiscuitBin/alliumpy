"""Prove that the one version is written identically everywhere it appears.

Three sources: `pyproject.toml`, the package's `__version__` as the wheel smoke's
virtual environment imports it, and what `docmirror --version` prints from that same
environment. The venv is `just wheel-smoke`'s; running this before it fails.
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV = ROOT / "target" / "wheel-smoke" / "venv" / "bin"


def _manifest_version() -> str:
    with (ROOT / "pyproject.toml").open("rb") as stream:
        version: str = tomllib.load(stream)["project"]["version"]
    return version


def _run(*command: str) -> str:
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def main() -> int:
    """Compare the three copies and print the verdict."""
    python = VENV / "python"
    script = VENV / "docmirror"
    if not python.is_file() or not script.is_file():
        print("version-check: run just wheel-smoke first; its venv is missing", file=sys.stderr)
        return 2
    manifest = _manifest_version()
    imported = _run(str(python), "-I", "-c", "import docmirror; print(docmirror.__version__)")
    printed = _run(str(script), "--version")
    words = printed.split()
    if len(words) != 2 or words[0] != "docmirror":
        print(f"version-check: unexpected --version output: {printed!r}", file=sys.stderr)
        return 1
    copies = {"pyproject.toml": manifest, "__version__": imported, "docmirror --version": words[1]}
    if len(set(copies.values())) != 1:
        for name, value in copies.items():
            print(f"version-check: {name} = {value}", file=sys.stderr)
        print("version-check: the copies disagree", file=sys.stderr)
        return 1
    print(f"version-check: {manifest} in every place it is written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
