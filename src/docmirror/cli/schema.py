"""`docmirror schema`: the JSON Schema of each published artefact."""

from __future__ import annotations

from typing import TYPE_CHECKING

from docmirror.config.models import Config
from docmirror.report.models import CrawlReport, Frontmatter, IndexEntry, json_schema

if TYPE_CHECKING:
    from pydantic import BaseModel

ARTIFACTS: dict[str, type[BaseModel]] = {
    "config": Config,
    "report": CrawlReport,
    "frontmatter": Frontmatter,
    "index": IndexEntry,
}


def schema_for(name: str) -> dict[str, object]:
    """The schema document for `config`, `report`, `frontmatter` or `index`."""
    return json_schema(ARTIFACTS[name])
