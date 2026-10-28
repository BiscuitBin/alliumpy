"""`docmirror index`: regenerate the index files offline."""

from __future__ import annotations

from pathlib import Path

from docmirror.cli.common import LOG, Common, config_for, fail
from docmirror.exit_codes import ExitCode
from docmirror.index.writers import write_indexes
from docmirror.state.db import open_manifest


def run_index(out_dir: Path, common: Common) -> ExitCode:
    """Rebuild `index.md`, `index.jsonl`, `llms.txt` and `_index.md` files."""
    if not out_dir.is_dir():
        fail(f"{out_dir} is not a directory; run docmirror init first", ExitCode.USAGE)
    config = config_for(out_dir, common)
    with open_manifest(out_dir) as manifest:
        pages = write_indexes(config, out_dir, manifest, None)
    LOG.info("indexed %d pages", len(pages))
    common.emitter.emit("index", out_dir=str(out_dir), pages=len(pages))
    if not common.json_events:
        print(f"Indexed {len(pages)} pages into index.md, index.jsonl and llms.txt")
    return ExitCode.OK
