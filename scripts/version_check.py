# Copyright 2026 Steven Cutting
"""Compare independently written release versions with the installed console script."""

import re
import subprocess
import sys
import tomllib
from pathlib import Path

# A reference that hangs is a failed read, not a gate that never returns.
REFERENCE_TIMEOUT_SECONDS = 60


def reference_output(reference: Path) -> str | None:
    """The reference's `--version` output, empty when it is missing, None when it fails."""
    if not reference.is_file():
        return ""
    try:
        result = subprocess.run(
            [str(reference), "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=REFERENCE_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        print(f"version-check: the reference {reference} fails to run: {error}", file=sys.stderr)
        return None
    # Only a well-formed `allium x.y.z` line can be stale; anything else is a failed read.
    if result.returncode != 0 or re.match(r"allium [0-9]+\.[0-9]+\.[0-9]+", result.stdout) is None:
        print(f"version-check: invalid reference version output: {result!r}", file=sys.stderr)
        return None
    return result.stdout


def version_string(root: Path, pin: str, source: str, console: str) -> int:
    """Compare the whole console output with the literal and, at the pin, the reference."""
    literal = re.search(r'pub const ALLIUM_VERSION_STRING: &str = "([^"]+)";', source)
    if literal is None:
        print("version-check: ALLIUM_VERSION_STRING literal is missing", file=sys.stderr)
        return 1
    if console != f"{literal[1]}\n":
        print(
            f"version-check: console output {console!r} differs from"
            f" ALLIUM_VERSION_STRING={literal[1]!r}",
            file=sys.stderr,
        )
        return 1
    # The reference is built by a network recipe outside check: a missing or stale
    # one is a note, not drift (T13). One that exists but fails to run or prints no
    # version line is a failed read.
    output = reference_output(root / ".tools/parity/bin/allium")
    if output is None:
        return 1
    if output.split()[1:2] != [pin]:
        print(
            f"version-check: note: no reference allium {pin} to compare;"
            " run just install-parity-reference"
        )
        return 0
    if output != console:
        print(
            f"version-check: console output {console!r} differs from the reference's {output!r}",
            file=sys.stderr,
        )
        return 1
    print(f"version-check: the reference prints the same: {output.strip()}")
    return 0


def main(argv: list[str]) -> int:
    """Fail with both names and values when release metadata drifts."""
    root = Path(__file__).resolve().parents[1]
    cargo = tomllib.loads((root / "Cargo.toml").read_text())
    pin = cargo["workspace"]["dependencies"]["allium-parser"].removeprefix("=")
    # install-parity-reference reads the pin before any wheel exists (T13), so this
    # path reads Cargo.toml alone.
    if argv == ["--print-pin"]:
        print(pin)
        return 0
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
        "allium-parser pin": pin,
        "ALLIUM_VERSION": match[1],
        "console version": words[1],
    }
    # Each member manifest either inherits the workspace version or writes its own;
    # an explicit one would drift silently past the workspace table, and an absent
    # one is 0.0.0 to cargo.
    members = [
        path
        for pattern in cargo["workspace"]["members"]
        for path in sorted(root.glob(pattern))
        if (path / "Cargo.toml").is_file()
    ]
    if not members:
        print("version-check: no workspace member crate was found", file=sys.stderr)
        return 1
    for member in members:
        package = tomllib.loads((member / "Cargo.toml").read_text())["package"]
        version = package.get("version", "0.0.0")
        if version == {"workspace": True}:
            version = versions["workspace version"]
        versions[f"{package['name']} version"] = version
    expected = versions["workspace version"]
    for name, value in versions.items():
        if value != expected:
            print(
                f"version-check: workspace version={expected!r} differs from {name}={value!r}",
                file=sys.stderr,
            )
            return 1
    print(f"version-check: all {len(versions)} versions agree: {expected}")
    return version_string(root, pin, source, result.stdout)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
