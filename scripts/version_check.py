# Copyright 2026 Steven Cutting
"""Compare independently written release versions with the installed console script."""

import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

# A reference that hangs is a failed read, not a gate that never returns.
REFERENCE_TIMEOUT_SECONDS = 60

# The dev shell names where the flake built the reference (decision 0018).
REFERENCE_VARIABLE = "ALLIUMPY_PARITY_REFERENCE"


def reference_path() -> Path | None:
    """The parity reference the dev shell names, or None when it names none."""
    named = os.environ.get(REFERENCE_VARIABLE, "")
    if not named:
        print(
            f"version-check: {REFERENCE_VARIABLE} is not set; run this inside the dev shell",
            file=sys.stderr,
        )
        return None
    return Path(named)


def flake_reference_version(root: Path) -> str | None:
    """The allium-cli version flake.nix builds as the reference, or None when unstated."""
    flake = root / "flake.nix"
    if not flake.is_file():
        print("version-check: flake.nix is missing", file=sys.stderr)
        return None
    found: list[str] = re.findall(
        r'^\s*alliumCliVersion = "([^"]+)";$', flake.read_text(), re.MULTILINE
    )
    if len(found) != 1:
        print(
            'version-check: flake.nix must state alliumCliVersion = "x.y.z"; exactly once',
            file=sys.stderr,
        )
        return None
    return found[0]


def reference_output(reference: Path) -> str | None:
    """The reference's `--version` output, or None when it is missing or fails."""
    if not reference.is_file():
        print(f"version-check: the reference {reference} is missing", file=sys.stderr)
        return None
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


def version_string(pin: str, source: str, console: str) -> int:
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
    # The dev shell builds its reference, so it must exist, run, print a version line
    # and be at the pin; anything else is a failure, not a note.
    reference = reference_path()
    output = None if reference is None else reference_output(reference)
    if output is None:
        return 1
    if output.split()[1:2] != [pin]:
        print(
            f"version-check: the dev shell's reference prints {output.strip()!r}, not"
            f" allium {pin}; leave the shell and enter it again",
            file=sys.stderr,
        )
        return 1
    if output != console:
        print(
            f"version-check: console output {console!r} differs from the reference's {output!r}",
            file=sys.stderr,
        )
        return 1
    print(f"version-check: the reference prints the same: {output.strip()}")
    return 0


def member_versions(root: Path) -> dict[str, str] | None:
    """Each workspace member's version as cargo resolves it, or None after an error.

    A member manifest either inherits the workspace version or writes its own; an
    explicit one would drift silently past the workspace table. Cargo, not a glob over
    members, decides membership: a path dependency joins the workspace and an excluded
    directory does not.
    """
    metadata = subprocess.run(
        [  # noqa: S607 - just check's check-toolchain proves PATH's cargo runs the pinned compiler.
            "cargo",
            "metadata",
            "--no-deps",
            "--format-version=1",
            "--locked",
            "--offline",
            "--manifest-path",
            str(root / "Cargo.toml"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if metadata.returncode != 0:
        print(f"version-check: cargo metadata failed: {metadata.stderr}", file=sys.stderr)
        return None
    packages = json.loads(metadata.stdout)["packages"]
    if not packages:
        print("version-check: no workspace member crate was found", file=sys.stderr)
        return None
    return {f"crate {package['name']} version": package["version"] for package in packages}


def versions_agree(versions: dict[str, str]) -> bool:
    """Whether every version equals the workspace version, naming both values when not."""
    expected = versions["workspace version"]
    for name, value in versions.items():
        if value != expected:
            print(
                f"version-check: workspace version={expected!r} differs from {name}={value!r}",
                file=sys.stderr,
            )
            return False
    print(f"version-check: all {len(versions)} versions agree: {expected}")
    return True


def main(argv: list[str]) -> int:
    """Fail with both names and values when release metadata drifts."""
    root = Path(__file__).resolve().parents[1]
    cargo = tomllib.loads((root / "Cargo.toml").read_text())
    pin = cargo["workspace"]["dependencies"]["allium-parser"].removeprefix("=")
    # The pin alone, before any wheel exists (T13): this path reads Cargo.toml only.
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
    flake_reference = flake_reference_version(root)
    members = member_versions(root)
    if (
        flake_reference is None
        or members is None
        or not versions_agree(versions | {"flake.nix parity reference": flake_reference} | members)
    ):
        return 1
    return version_string(pin, source, result.stdout)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
