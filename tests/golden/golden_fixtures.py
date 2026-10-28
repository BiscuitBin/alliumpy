"""The captured pages the golden suite runs over."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

FIXTURES = Path(__file__).parent.parent / "fixtures"
PROFILES = ("mslearn", "devsite")


@dataclass(frozen=True, slots=True)
class Captured:
    """One captured page: its profile, slug, URL and raw HTML."""

    profile: str
    slug: str
    url: str
    html: str

    @property
    def id(self) -> str:
        """The pytest id."""
        return f"{self.profile}/{self.slug}"


def captured_pages() -> list[Captured]:
    """Every fixture directory with a `page.html` and a `url.txt`."""
    pages: list[Captured] = []
    for profile in PROFILES:
        root = FIXTURES / profile
        if not root.is_dir():
            continue
        for directory in sorted(p for p in root.iterdir() if p.is_dir()):
            page = directory / "page.html"
            url = directory / "url.txt"
            if page.is_file() and url.is_file():
                pages.append(
                    Captured(
                        profile,
                        directory.name,
                        url.read_text(encoding="utf-8").strip(),
                        page.read_text(encoding="utf-8", errors="replace"),
                    )
                )
    return pages
