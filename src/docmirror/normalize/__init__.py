"""DOM pre-normalization: one module per transform, run before either backend."""

from __future__ import annotations

from docmirror.normalize.islands import Islands
from docmirror.normalize.pipeline import NormalizeResult, normalize

__all__ = ["Islands", "NormalizeResult", "normalize"]
