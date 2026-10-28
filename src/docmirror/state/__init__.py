"""The manifest: SQLite state under `<out>/.docmirror/state.sqlite`."""

from __future__ import annotations

from docmirror.state.db import STATE_DIR, STATE_FILE, Manifest, open_manifest

__all__ = ["STATE_DIR", "STATE_FILE", "Manifest", "open_manifest"]
