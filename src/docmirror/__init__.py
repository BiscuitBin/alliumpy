"""docmirror: mirror a documentation website into a Markdown knowledge base."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("docmirror")
except PackageNotFoundError:  # pragma: no cover - only when run from an unbuilt checkout
    __version__ = "0.0.0"

__all__ = ["__version__"]
