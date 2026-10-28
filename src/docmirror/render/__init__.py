"""Browser tiers behind one `BrowserDriver` protocol: Patchright, then Camoufox."""

from __future__ import annotations

from docmirror.render.driver import BrowserDriver, CamoufoxDriver, PatchrightDriver, driver_for

__all__ = ["BrowserDriver", "CamoufoxDriver", "PatchrightDriver", "driver_for"]
