"""The manifest connection: WAL mode, migrations, and typed row access.

Every page write is a temp file in the target's directory, `os.replace` onto the
target, then the row commit, so an interrupted run leaves at most one page
inconsistent and the next run re-fetches it.
"""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self

from docmirror.state.schema import MIGRATIONS, SCHEMA_VERSION

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Mapping

STATE_DIR = ".docmirror"
STATE_FILE = "state.sqlite"
# A tombstoned page is rechecked after everything else unless it is rediscovered.
DEFERRED_PRIORITY = -1


def now_iso() -> str:
    """The current UTC time as `YYYY-MM-DDTHH:MM:SSZ`."""
    return datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True, slots=True)
class FrontierEntry:
    """One row of the frontier table."""

    url: str
    status: str
    depth: int
    discovered_from: str | None
    discovered_via: str | None
    attempts: int
    next_attempt_at: str | None
    sitemap_lastmod: str | None
    priority: int


class Manifest:
    """The SQLite manifest for one output directory."""

    def __init__(self, path: Path) -> None:
        """Open or create the database at `path`, applying pending migrations."""
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path, isolation_level=None)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA synchronous=NORMAL")
        self.connection.execute("PRAGMA foreign_keys=ON")
        self._migrate()

    # -- lifecycle -------------------------------------------------------------

    def _migrate(self) -> None:
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        current = int(self.get_meta("schema_version") or 0)
        for version in range(current + 1, SCHEMA_VERSION + 1):
            self.connection.executescript("BEGIN;" + MIGRATIONS[version] + "COMMIT;")
            self.set_meta("schema_version", str(version))

    def close(self) -> None:
        """Close the connection."""
        self.connection.close()

    def __enter__(self) -> Self:
        """Context-manager entry."""
        return self

    def __exit__(self, *_: object) -> None:
        """Close on exit."""
        self.close()

    def transaction(self) -> _Transaction:
        """A context manager that commits on success and rolls back on error."""
        return _Transaction(self.connection)

    # -- meta ------------------------------------------------------------------

    def get_meta(self, key: str) -> str | None:
        """A value from the `meta` table."""
        row = self.connection.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        return None if row is None else str(row["value"])

    def set_meta(self, key: str, value: str) -> None:
        """Set a value in the `meta` table."""
        self.connection.execute(
            "INSERT INTO meta(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )

    # -- pages -----------------------------------------------------------------

    def _one(self, query: str, parameters: tuple[object, ...]) -> sqlite3.Row | None:
        row: sqlite3.Row | None = self.connection.execute(query, parameters).fetchone()
        return row

    def get_page(self, normalized_url: str) -> sqlite3.Row | None:
        """The page row, if known."""
        return self._one("SELECT * FROM pages WHERE normalized_url = ?", (normalized_url,))

    def page_by_path(self, path: str) -> sqlite3.Row | None:
        """The page row written at `path`, if any."""
        return self._one("SELECT * FROM pages WHERE path = ?", (path,))

    def upsert_page(self, normalized_url: str, **fields: Any) -> None:  # noqa: ANN401 - row values
        """Insert or update a page row with the given columns."""
        fields = dict(fields)
        if "flags" in fields:
            fields["flags_json"] = json.dumps(sorted(fields.pop("flags")))
        if "headings" in fields:
            fields["headings_json"] = json.dumps(fields.pop("headings"))
        if "frontmatter" in fields:
            fields["frontmatter_json"] = json.dumps(fields.pop("frontmatter"), sort_keys=True)
        columns = ["normalized_url", *fields]
        placeholders = ", ".join("?" for _ in columns)
        updates = (
            ", ".join(f"{column} = excluded.{column}" for column in fields)
            or "normalized_url = excluded.normalized_url"
        )
        self.connection.execute(
            f"INSERT INTO pages({', '.join(columns)}) VALUES({placeholders}) "
            f"ON CONFLICT(normalized_url) DO UPDATE SET {updates}",
            (normalized_url, *fields.values()),
        )

    def gone_pages(self) -> list[sqlite3.Row]:
        """Every tombstoned page row, ordered by path."""
        return list(
            self.connection.execute(
                "SELECT * FROM pages WHERE status = 'gone' ORDER BY path"
            ).fetchall()
        )

    def pages(self, *, written_only: bool = False) -> list[sqlite3.Row]:
        """Every page row, ordered by path."""
        query = "SELECT * FROM pages"
        if written_only:
            query += " WHERE path IS NOT NULL AND status = 'written' AND tombstoned_at IS NULL"
        query += " ORDER BY path"
        return list(self.connection.execute(query).fetchall())

    def path_taken(self, path: str) -> bool:
        """Whether any page already owns `path`."""
        return self.page_by_path(path) is not None

    # -- aliases ---------------------------------------------------------------

    def add_alias(self, url: str, normalized_url: str) -> None:
        """Record that `url` is an alias of `normalized_url`."""
        self.connection.execute(
            "INSERT INTO aliases(url, normalized_url) VALUES(?, ?) "
            "ON CONFLICT(url) DO UPDATE SET normalized_url = excluded.normalized_url",
            (url, normalized_url),
        )

    def resolve_alias(self, url: str) -> str | None:
        """The normalized URL an alias points to."""
        row = self.connection.execute(
            "SELECT normalized_url FROM aliases WHERE url = ?", (url,)
        ).fetchone()
        return None if row is None else str(row["normalized_url"])

    # -- frontier --------------------------------------------------------------

    def enqueue(
        self,
        url: str,
        *,
        depth: int,
        discovered_from: str | None,
        discovered_via: str,
        sitemap_lastmod: str | None = None,
        priority: int = 0,
        status: str = "pending",
    ) -> bool:
        """Add a URL to the frontier unless it is already there; returns whether added."""
        cursor = self.connection.execute(
            "INSERT OR IGNORE INTO frontier(url, status, depth, discovered_from, discovered_via, "
            "sitemap_lastmod, priority) VALUES(?, ?, ?, ?, ?, ?, ?)",
            (url, status, depth, discovered_from, discovered_via, sitemap_lastmod, priority),
        )
        if cursor.rowcount == 0 and sitemap_lastmod is not None:
            self.connection.execute(
                "UPDATE frontier SET sitemap_lastmod = ? WHERE url = ? AND sitemap_lastmod IS NULL",
                (sitemap_lastmod, url),
            )
        if cursor.rowcount == 0:
            # Rediscovery promotes a deferred row; only a pending one, so a page that is
            # gone again in this run is not queued a second time.
            self.connection.execute(
                "UPDATE frontier SET priority = ?, depth = MIN(depth, ?) "
                "WHERE url = ? AND status = 'pending' AND priority < 0",
                (priority, depth, url),
            )
        return cursor.rowcount == 1

    def frontier_defer(self, url: str) -> None:
        """Queue an existing row as pending behind every other row (a deferred recheck)."""
        self.connection.execute(
            "UPDATE frontier SET status = 'pending', priority = ? WHERE url = ?",
            (DEFERRED_PRIORITY, url),
        )

    def frontier_set_status(
        self, url: str, status: str, *, next_attempt_at: str | None = None
    ) -> None:
        """Set a frontier row's status, bumping attempts on retry statuses."""
        self.connection.execute(
            "UPDATE frontier SET status = ?, next_attempt_at = ?, attempts = attempts + "
            "CASE WHEN ? IN ('retry', 'failed') THEN 1 ELSE 0 END WHERE url = ?",
            (status, next_attempt_at, status, url),
        )

    def frontier_bulk_status(
        self, from_status: str, to_status: str, *, host: str | None = None
    ) -> int:
        """Move every row in `from_status` (optionally for one host) to `to_status`."""
        if host is None:
            cursor = self.connection.execute(
                "UPDATE frontier SET status = ? WHERE status = ?", (to_status, from_status)
            )
        else:
            cursor = self.connection.execute(
                "UPDATE frontier SET status = ? WHERE status = ? AND (url LIKE ? OR url LIKE ?)",
                (to_status, from_status, f"https://{host}/%", f"http://{host}/%"),
            )
        return int(cursor.rowcount)

    def frontier_pending(self, limit: int) -> list[FrontierEntry]:
        """Up to `limit` pending rows: shallowest, highest priority, oldest; deferred rows last."""
        rows = self.connection.execute(
            "SELECT * FROM frontier WHERE status = 'pending' "
            "ORDER BY (priority < 0) ASC, depth ASC, priority DESC, rowid ASC LIMIT ?",
            (limit,),
        ).fetchall()
        return [
            FrontierEntry(**{k: row[k] for k in FrontierEntry.__dataclass_fields__}) for row in rows
        ]

    def frontier_count(self, status: str | None = None) -> int:
        """Rows in the frontier, optionally in one status."""
        if status is None:
            row = self.connection.execute("SELECT COUNT(*) AS n FROM frontier").fetchone()
        else:
            row = self.connection.execute(
                "SELECT COUNT(*) AS n FROM frontier WHERE status = ?", (status,)
            ).fetchone()
        return int(row["n"])

    def frontier_rows(self) -> list[FrontierEntry]:
        """Every frontier row in insertion order."""
        rows = self.connection.execute("SELECT * FROM frontier ORDER BY rowid").fetchall()
        return [
            FrontierEntry(**{k: row[k] for k in FrontierEntry.__dataclass_fields__}) for row in rows
        ]

    # -- links -----------------------------------------------------------------

    def replace_links(
        self, from_url: str, links: Iterable[tuple[str, str, str, str | None]]
    ) -> None:
        """Replace the outbound link rows of a page: `(to_url, fragment, kind, resolved_path)`."""
        self.connection.execute("DELETE FROM links WHERE from_url = ?", (from_url,))
        self.connection.executemany(
            "INSERT OR REPLACE INTO links(from_url, to_url, fragment, kind, resolved_path) "
            "VALUES(?, ?, ?, ?, ?)",
            [(from_url, to, fragment, kind, path) for to, fragment, kind, path in links],
        )

    def inbound(self, to_url: str) -> list[sqlite3.Row]:
        """Link rows pointing at `to_url`."""
        return list(self.connection.execute("SELECT * FROM links WHERE to_url = ?", (to_url,)))

    def link_counts(self) -> tuple[dict[str, int], dict[str, int]]:
        """Outbound-internal and inbound-internal counts per normalized URL."""
        outbound: dict[str, int] = {}
        inbound: dict[str, int] = {}
        for row in self.connection.execute(
            "SELECT from_url, to_url FROM links WHERE kind = 'internal'"
        ):
            outbound[row["from_url"]] = outbound.get(row["from_url"], 0) + 1
            inbound[row["to_url"]] = inbound.get(row["to_url"], 0) + 1
        return outbound, inbound

    # -- anchors ---------------------------------------------------------------

    def replace_anchors(self, normalized_url: str, anchors: Iterable[str]) -> None:
        """Replace the known fragment anchors of a page."""
        self.connection.execute("DELETE FROM anchors WHERE normalized_url = ?", (normalized_url,))
        self.connection.executemany(
            "INSERT OR IGNORE INTO anchors(normalized_url, anchor) VALUES(?, ?)",
            [(normalized_url, anchor) for anchor in anchors],
        )

    def anchors(self, normalized_url: str) -> set[str]:
        """The known anchors of a page."""
        return {
            str(row["anchor"])
            for row in self.connection.execute(
                "SELECT anchor FROM anchors WHERE normalized_url = ?", (normalized_url,)
            )
        }

    # -- caches ----------------------------------------------------------------

    def cached_keywords(self, content_sha256: str) -> list[str] | None:
        """Keywords cached for a body hash."""
        row = self.connection.execute(
            "SELECT keywords_json FROM keywords_cache WHERE content_sha256 = ?", (content_sha256,)
        ).fetchone()
        if row is None:
            return None
        loaded: list[str] = json.loads(row["keywords_json"])
        return loaded

    def cache_keywords(self, content_sha256: str, keywords: list[str]) -> None:
        """Cache keywords for a body hash."""
        self.connection.execute(
            "INSERT OR REPLACE INTO keywords_cache(content_sha256, keywords_json) VALUES(?, ?)",
            (content_sha256, json.dumps(keywords)),
        )

    def cached_tier(self, host: str, path_pattern: str) -> str | None:
        """The tier a path pattern of a host is known to need."""
        row = self.connection.execute(
            "SELECT tier FROM tier_cache WHERE host = ? AND path_pattern = ?", (host, path_pattern)
        ).fetchone()
        return None if row is None else str(row["tier"])

    def cache_tier(self, host: str, path_pattern: str, tier: str) -> None:
        """Remember that a path pattern of a host needs `tier`."""
        self.connection.execute(
            "INSERT OR REPLACE INTO tier_cache(host, path_pattern, tier) VALUES(?, ?, ?)",
            (host, path_pattern, tier),
        )

    # -- runs ------------------------------------------------------------------

    def start_run(self, run_id: str, command: str, args: Mapping[str, Any]) -> None:
        """Record the start of a run."""
        self.connection.execute(
            "INSERT INTO runs(id, started_at, command, args_json) VALUES(?, ?, ?, ?)",
            (run_id, now_iso(), command, json.dumps(dict(args), sort_keys=True, default=str)),
        )

    def finish_run(self, run_id: str, exit_code: int, counts: Mapping[str, Any]) -> None:
        """Record the end of a run."""
        self.connection.execute(
            "UPDATE runs SET finished_at = ?, exit_code = ?, counts_json = ? WHERE id = ?",
            (now_iso(), exit_code, json.dumps(dict(counts), sort_keys=True), run_id),
        )

    def runs(self) -> Iterator[sqlite3.Row]:
        """Every run, oldest first."""
        return iter(self.connection.execute("SELECT * FROM runs ORDER BY started_at"))


class _Transaction:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def __enter__(self) -> None:
        self._connection.execute("BEGIN IMMEDIATE")

    def __exit__(self, exc_type: object, *_: object) -> None:
        if exc_type is None:
            self._connection.execute("COMMIT")
        else:
            self._connection.execute("ROLLBACK")


def open_manifest(out_dir: Path) -> Manifest:
    """The manifest for an output directory, created when missing."""
    return Manifest(out_dir / STATE_DIR / STATE_FILE)


def atomic_write_text(path: Path, text: str) -> None:
    """Write `text` to `path` through a temp file in the same directory and `os.replace`."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".docmirror-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
        Path(temp_name).replace(path)
    except BaseException:
        Path(temp_name).unlink(missing_ok=True)
        raise
