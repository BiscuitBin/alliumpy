# Copyright 2026 Steven Cutting
"""Compare independently written release versions with the installed console script."""

import re
import subprocess
import sys
import tomllib
from pathlib import Path


def main() -> int:
    """Fail with both names and values when release metadata drifts."""
    root = Path(__file__).resolve().parents[1]
    cargo = tomllib.loads((root / "Cargo.toml").read_text())
    wheel = tomllib.loads((root / "crates/alliumpy/pyproject.toml").read_text())
    source = (root / "crates/alliumpy-core/src/lib.rs").read_text()
    match = re.search(r'pub const ALLIUM_VERSION: &str = "([^"]+)";', source)
    if match is None:
        print("version-check: ALLIUM_VERSION literal is missing", file=sys.stderr)
        return 1
    executable = root / "target/wheel-smoke/venv/bin/allium"
    if not executable.is_file():
        print(
            "version-check: run just wheel-smoke first (console script is missing)", file=sys.stderr
        )
        return 1
    result = subprocess.run(
        [str(executable), "--version"], capture_output=True, text=True, check=False
    )
    words = result.stdout.split()
    if result.returncode != 0 or len(words) < 2 or words[0] != "allium":
        print(f"version-check: invalid console version output: {result!r}", file=sys.stderr)
        return 1
    versions = {
        "workspace version": cargo["workspace"]["package"]["version"],
        "wheel version (without post release)": re.sub(
            r"\.post[0-9]+$", "", wheel["project"]["version"]
        ),
        "allium-parser pin": cargo["workspace"]["dependencies"]["allium-parser"].removeprefix("="),
        "ALLIUM_VERSION": match[1],
        "console version": words[1],
    }
    expected = versions["workspace version"]
    for name, value in versions.items():
        if value != expected:
            print(
                f"version-check: workspace version={expected!r} differs from {name}={value!r}",
                file=sys.stderr,
            )
            return 1
    print(f"version-check: all five versions agree: {expected}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
