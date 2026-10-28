"""The SQLite schema and its migrations, applied in order by `Manifest`."""

from __future__ import annotations

SCHEMA_VERSION = 1

MIGRATIONS: dict[int, str] = {
    1: """
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS pages (
    normalized_url TEXT PRIMARY KEY,
    canonical_url TEXT,
    path TEXT,
    title TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    http_status INTEGER,
    etag TEXT,
    last_modified TEXT,
    sitemap_lastmod TEXT,
    raw_sha256 TEXT,
    content_sha256 TEXT,
    render_tier TEXT,
    extractor TEXT,
    quality_score REAL,
    low_confidence INTEGER,
    flags_json TEXT,
    first_seen TEXT,
    last_seen TEXT,
    last_changed TEXT,
    redirect_to TEXT,
    tombstoned_at TEXT,
    discovered_via TEXT,
    description TEXT,
    headings_json TEXT,
    version TEXT,
    locale TEXT,
    word_count INTEGER,
    fetched_at TEXT,
    frontmatter_json TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS pages_path ON pages(path);
CREATE TABLE IF NOT EXISTS aliases (
    url TEXT PRIMARY KEY,
    normalized_url TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS frontier (
    url TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'pending',
    depth INTEGER NOT NULL DEFAULT 0,
    discovered_from TEXT,
    discovered_via TEXT,
    attempts INTEGER NOT NULL DEFAULT 0,
    next_attempt_at TEXT,
    sitemap_lastmod TEXT,
    priority INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS frontier_status ON frontier(status, priority, depth);
CREATE TABLE IF NOT EXISTS links (
    from_url TEXT NOT NULL,
    to_url TEXT NOT NULL,
    fragment TEXT,
    kind TEXT NOT NULL,
    resolved_path TEXT,
    PRIMARY KEY (from_url, to_url, fragment)
);
CREATE INDEX IF NOT EXISTS links_to ON links(to_url);
CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    command TEXT NOT NULL,
    args_json TEXT,
    exit_code INTEGER,
    counts_json TEXT
);
CREATE TABLE IF NOT EXISTS keywords_cache (
    content_sha256 TEXT PRIMARY KEY,
    keywords_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tier_cache (
    host TEXT NOT NULL,
    path_pattern TEXT NOT NULL,
    tier TEXT NOT NULL,
    PRIMARY KEY (host, path_pattern)
);
CREATE TABLE IF NOT EXISTS anchors (
    normalized_url TEXT NOT NULL,
    anchor TEXT NOT NULL,
    PRIMARY KEY (normalized_url, anchor)
);
""",
}
