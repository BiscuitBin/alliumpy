"""Quality gates, measured from the extracted DOM and the Markdown output."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml import html

GATE_NAMES: tuple[str, ...] = (
    "text_coverage",
    "code_blocks",
    "code_lang_rate",
    "tables",
    "table_cells",
    "headings",
    "links",
    "images",
    "list_items",
    "tabs_expanded",
)


@dataclass(slots=True)
class QualityResult:
    """The measured metrics, the failed gates and the score."""

    metrics: dict[str, float] = field(default_factory=dict)
    failed: list[str] = field(default_factory=list)
    score: float = 0.0

    @property
    def low_confidence(self) -> bool:
        """Whether any gate failed."""
        return bool(self.failed)


def measure_quality(dom: html.HtmlElement, markdown: str, counts: dict[str, int]) -> QualityResult:
    """Measure every gate from the extracted DOM and the Markdown output."""
    from docmirror.quality.measure import measure  # noqa: PLC0415 - heavy imports stay lazy

    return measure(dom, markdown, counts)
