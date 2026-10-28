"""Smoke the installed wheel: import, schemas, init, doctor and verify, offline.

Run with `python -I` from a fresh virtual environment and the console script's path as
the only argument. Every assertion is the contract; a failure prints what it saw.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import docmirror


def run(script: str, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Run the console script and return the completed process."""
    return subprocess.run(
        [script, *args], check=False, capture_output=True, text=True, cwd=cwd, timeout=120
    )


def main(script: str) -> int:
    """Exercise the wheel and print the verdict."""
    assert docmirror.__version__ != "0.0.0", docmirror.__version__
    version = run(script, "--version")
    assert version.returncode == 0, version.stderr
    assert version.stdout.strip() == f"docmirror {docmirror.__version__}", version.stdout

    for name in ("config", "report", "frontmatter", "index"):
        result = run(script, "schema", name)
        assert result.returncode == 0, (name, result.stderr)
        document = json.loads(result.stdout)
        assert document["$schema"] == "https://json-schema.org/draft/2020-12/schema", name
        assert "properties" in document, name
    bad = run(script, "schema", "nonsense")
    assert bad.returncode == 2, bad

    with tempfile.TemporaryDirectory() as temp:
        out = Path(temp) / "mirror"
        init = run(script, "init", "https://example.org/docs/guide/", str(out))
        assert init.returncode == 0, init.stderr
        assert (out / "docmirror.toml").is_file()
        assert (out / ".docmirror" / "state.sqlite").is_file()
        again = run(script, "init", "https://example.org/docs/guide/", str(out))
        assert again.returncode == 2, again

        doctor = run(script, "doctor", "--json")
        payload = json.loads(doctor.stdout)
        assert payload["event"] == "doctor", payload
        names = {check["name"] for check in payload["checks"]}
        assert {"python", "curl_cffi", "patchright", "patchright browser"} <= names, names

        report = run(script, "report", str(out))
        assert report.returncode == 2, report

    print("smoke: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
