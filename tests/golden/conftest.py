"""Parametrize the golden suite over every captured page."""

from __future__ import annotations

from typing import TYPE_CHECKING

from golden_fixtures import captured_pages

if TYPE_CHECKING:
    import pytest


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Parametrize any test taking `captured` over every fixture page."""
    if "captured" in metafunc.fixturenames:
        pages = captured_pages()
        metafunc.parametrize("captured", pages, ids=[p.id for p in pages])
