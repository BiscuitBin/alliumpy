"""`docmirror doctor`: environment checks with a remedy for each failure."""

from __future__ import annotations

import importlib
import importlib.util
import json
import os
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from docmirror.cli.common import Common
from docmirror.exit_codes import ExitCode

MIN_PYTHON = (3, 12)


@dataclass(frozen=True, slots=True)
class Check:
    """One doctor finding."""

    name: str
    ok: bool
    detail: str
    required: bool = True
    remedy: str = ""


def _module_present(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def patchright_browser_path() -> Path | None:
    """The Chromium executable Patchright would launch, if installed."""
    try:
        from patchright._impl._driver import compute_driver_executable  # noqa: PLC0415
        from patchright.sync_api import sync_playwright  # noqa: PLC0415
    except ImportError:
        return None
    del compute_driver_executable
    try:
        with sync_playwright() as playwright:
            candidate = Path(playwright.chromium.executable_path)
    except Exception:  # noqa: BLE001 - any driver failure means "not installed"
        return None
    return candidate if candidate.exists() else None


def run_checks() -> list[Check]:
    """Every check, in display order."""
    checks: list[Check] = []
    version = sys.version_info[:3]
    checks.append(
        Check(
            "python",
            version >= MIN_PYTHON,
            ".".join(map(str, version)),
            remedy="docmirror needs Python 3.12 or newer",
        )
    )
    curl_ok = _module_present("curl_cffi")
    detail = ""
    if curl_ok:
        module = importlib.import_module("curl_cffi")
        detail = f"curl_cffi {getattr(module, '__version__', '?')}"
    checks.append(
        Check("curl_cffi", curl_ok, detail or "not importable", remedy="uv tool install docmirror")
    )
    pr_ok = _module_present("patchright")
    checks.append(
        Check(
            "patchright",
            pr_ok,
            "importable" if pr_ok else "not importable",
            remedy="uv tool install docmirror",
        )
    )
    browser = patchright_browser_path() if pr_ok else None
    checks.append(
        Check(
            "patchright browser",
            browser is not None,
            str(browser) if browser else "Chromium not installed",
            remedy="patchright install chromium",
        )
    )
    cf = _module_present("camoufox")
    checks.append(
        Check(
            "camoufox",
            cf,
            "present (optional)" if cf else "absent (optional)",
            required=False,
            remedy="uv tool install 'docmirror[camoufox]' && camoufox fetch",
        )
    )
    try:
        with tempfile.NamedTemporaryFile(dir=Path.cwd(), prefix=".docmirror-doctor-", delete=True):
            pass
        write_ok, where = True, str(Path.cwd())
    except OSError as error:
        write_ok, where = False, str(error)
    checks.append(Check("write access", write_ok, where, remedy="run from a writable directory"))
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or ""
    checks.append(Check("https proxy", ok=True, detail=proxy or "none configured", required=False))
    return checks


def run_doctor(common: Common) -> ExitCode:
    """Print the checks and exit 1 when a required check fails."""
    checks = run_checks()
    failed = [check for check in checks if check.required and not check.ok]
    if common.json_events:
        print(
            json.dumps(
                {"event": "doctor", "ok": not failed, "checks": [asdict(check) for check in checks]}
            )
        )
    else:
        for check in checks:
            mark = "ok " if check.ok else ("FAIL" if check.required else "warn")
            line = f"[{mark}] {check.name}: {check.detail}"
            if not check.ok and check.remedy:
                line += f"  -> {check.remedy}"
            print(line)
    return ExitCode.PARTIAL if failed else ExitCode.OK
