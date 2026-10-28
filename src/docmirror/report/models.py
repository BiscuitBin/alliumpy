"""The artefacts with a published JSON Schema: the report, the frontmatter and the index."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

REPORT_FILENAME = "crawl-report.json"

QualityFlag = Literal[
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
    "extractor_fallback",
    "render_needed",
    "interactive_omitted",
    "uncrawled_internal",
    "unresolved_fragment",
    "dangling_inbound",
    "soft_block_suspected",
    "html_table_kept",
    "empty_content",
]


class Artifact(BaseModel):
    """Base for the published artefacts: strict, with a schema draft declared."""

    model_config = ConfigDict(extra="forbid", json_schema_extra={})


class RunInfo(Artifact):
    """The `run` block of the report."""

    id: str
    command: str
    started_at: str
    finished_at: str
    duration_s: float
    exit_code: int
    version: str
    config_hash: str
    robots_ignored: bool = False


class Totals(Artifact):
    """The `totals` block of the report."""

    discovered: int = 0
    fetched: int = 0
    converted: int = 0
    skipped_unchanged: int = 0
    failed: int = 0
    blocked: int = 0
    low_confidence: int = 0


class HostReport(Artifact):
    """One `per_host[]` entry."""

    host: str
    fetched: int = 0
    blocked: int = 0
    block_rate: float = 0.0
    tiers_used: list[str] = Field(default_factory=list)
    breaker_tripped: bool = False
    robots_ignored: bool = False
    render_escalations: int = 0
    retry_after_honored: int = 0


class BlockedUrl(Artifact):
    """One `blocked_urls[]` entry."""

    url: str
    status: int | None = None
    signature: str
    tier: str


class FailedUrl(Artifact):
    """One `failed_urls[]` entry."""

    url: str
    error: str
    attempts: int


class LowConfidencePage(Artifact):
    """One `low_confidence_pages[]` entry."""

    path: str
    quality_score: float
    flags: list[str]


class BrokenLink(Artifact):
    """One `broken_links[]` entry."""

    from_path: str
    href: str
    reason: str


class Changes(Artifact):
    """The `changes` block of the report."""

    added: list[str] = Field(default_factory=list)
    changed: list[str] = Field(default_factory=list)
    unchanged: list[str] = Field(default_factory=list)
    removed: list[str] = Field(default_factory=list)
    moved: list[str] = Field(default_factory=list)
    failed: list[str] = Field(default_factory=list)


class QualitySummary(Artifact):
    """The `quality_summary` block of the report."""

    mean_score: float = 0.0
    p10_score: float = 0.0
    gate_failures: dict[str, int] = Field(default_factory=dict)


class CrawlReport(Artifact):
    """`crawl-report.json`."""

    run: RunInfo
    totals: Totals = Field(default_factory=Totals)
    per_host: list[HostReport] = Field(default_factory=list)
    blocked_urls: list[BlockedUrl] = Field(default_factory=list)
    failed_urls: list[FailedUrl] = Field(default_factory=list)
    low_confidence_pages: list[LowConfidencePage] = Field(default_factory=list)
    broken_links: list[BrokenLink] = Field(default_factory=list)
    changes: Changes = Field(default_factory=Changes)
    quality_summary: QualitySummary = Field(default_factory=QualitySummary)
    render_escalations: int = 0
    retry_after_honored: int = 0
    robots_ignored: bool = False


class Frontmatter(Artifact):
    """The YAML frontmatter of every page. Keys with unknown values are omitted."""

    source_url: str
    title: str
    fetched_at: str
    content_sha256: str
    quality_score: float
    low_confidence: bool
    breadcrumbs: list[str] | None = None
    canonical_url: str | None = None
    converter: str | None = None
    description: str | None = None
    etag: str | None = None
    extractor: str | None = None
    keywords: list[str] | None = None
    last_modified: str | None = None
    locale: str | None = None
    profile: str | None = None
    quality_flags: list[str] = Field(default_factory=list)
    render: Literal["http", "browser", "stealth"] | None = None
    sitemap_lastmod: str | None = None
    version: str | None = None


class IndexEntry(Artifact):
    """One line of `index.jsonl`."""

    path: str
    source_url: str
    title: str
    description: str
    keywords: list[str]
    headings: list[str]
    version: str | None = None
    locale: str | None = None
    quality_score: float
    low_confidence: bool
    quality_flags: list[str]
    content_sha256: str
    fetched_at: str
    last_modified: str | None = None
    word_count: int
    outbound_internal: int
    inbound_internal: int


SCHEMA_URI = "https://json-schema.org/draft/2020-12/schema"


def json_schema(model: type[BaseModel]) -> dict[str, object]:
    """The JSON Schema (draft 2020-12) of an artefact model."""
    schema = model.model_json_schema()
    return {"$schema": SCHEMA_URI, **schema}
