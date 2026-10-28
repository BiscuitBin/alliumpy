"""`docmirror crawl` and `docmirror update`."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from docmirror.cli.common import LOG, Common, config_for, fail
from docmirror.config.loader import CONFIG_FILENAME
from docmirror.exit_codes import ExitCode
from docmirror.state.db import open_manifest


def run_crawl(mode: str, out_dir: Path, common: Common, flags: dict[str, Any]) -> ExitCode:
    """Load the configuration, open the manifest and run the crawler."""
    if not out_dir.is_dir():
        fail(f"{out_dir} is not a directory; run docmirror init first", ExitCode.USAGE)
    config = config_for(out_dir, common)
    if not config.site.root_url and not config.site.start_urls:
        fail("[site] root_url or start_urls must be set", ExitCode.USAGE)
    config_path = common.config_path or out_dir / CONFIG_FILENAME
    config_text = config_path.read_text(encoding="utf-8") if config_path.is_file() else ""
    from docmirror.pipeline import Crawler  # noqa: PLC0415 - heavy import kept off the help path

    with open_manifest(out_dir) as manifest:
        recorded = manifest.get_meta("root_url")
        differs = bool(recorded) and recorded != config.site.root_url
        if differs and not common.non_interactive_confirmed():
            fail(
                f"[site] root_url {config.site.root_url!r} differs from the manifest's "
                f"{recorded!r}; pass --yes to proceed",
                ExitCode.USAGE,
            )
        manifest.set_meta("root_url", config.site.root_url)
        command = "update" if (mode == "update" or manifest.pages(written_only=True)) else "crawl"
        LOG.info("%s %s with profile %s", command, out_dir, config.site.profile)
        crawler = Crawler(
            config,
            out_dir,
            manifest,
            common.emitter,
            command=command,
            config_text=config_text,
            resume=bool(flags.get("resume", True)),
            dry_run=bool(flags.get("dry_run", False)),
        )
        try:
            return asyncio.run(crawler.run())
        except KeyboardInterrupt:
            return ExitCode.PARTIAL
