"""Options every subcommand shares, logging setup and the exit-code mapping."""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, NoReturn

import typer
from rich.console import Console
from rich.logging import RichHandler

from docmirror.config.loader import CONFIG_FILENAME, ConfigError, load_config
from docmirror.config.models import Config
from docmirror.exit_codes import ExitCode
from docmirror.report.events import EventEmitter

LOG = logging.getLogger("docmirror")


@dataclass
class Common:
    """What the global options resolved to for this invocation."""

    config_path: Path | None = None
    json_events: bool = False
    yes: bool = False
    non_interactive: bool = False
    verbosity: int = 0
    quiet: bool = False
    overrides: dict[str, object] = field(default_factory=dict)

    @property
    def emitter(self) -> EventEmitter:
        """The NDJSON emitter for this invocation."""
        return EventEmitter(enabled=self.json_events)

    @property
    def interactive(self) -> bool:
        """Whether prompting is allowed: never when stdout is not a TTY."""
        return not self.non_interactive and sys.stdout.isatty()

    def non_interactive_confirmed(self) -> bool:
        """Whether `--yes` stood in for a confirmation."""
        return self.yes


def configure_logging(common: Common) -> None:
    """Rich logging on stderr at the level the flags select."""
    level = logging.WARNING
    if common.quiet:
        level = logging.ERROR
    elif common.verbosity == 1:
        level = logging.INFO
    elif common.verbosity >= 2:  # noqa: PLR2004 - two -v flags
        level = logging.DEBUG
    handler = RichHandler(
        console=Console(stderr=True),
        show_path=common.verbosity >= 2,  # noqa: PLR2004 - two -v flags
        rich_tracebacks=False,
        markup=False,
    )
    logging.basicConfig(level=level, handlers=[handler], format="%(message)s", force=True)
    logging.getLogger("docmirror").setLevel(level)


ConfigOption = Annotated[
    Path | None,
    typer.Option("--config", help="Path to docmirror.toml (default: <out-dir>/docmirror.toml)."),
]
JsonOption = Annotated[
    bool, typer.Option("--json", help="NDJSON progress events on stdout; human logs on stderr.")
]
YesOption = Annotated[
    bool, typer.Option("--yes", "--non-interactive", help="Never prompt; accept defaults.")
]
VerboseOption = Annotated[
    int, typer.Option("--verbose", "-v", count=True, help="More logging; repeatable.")
]
QuietOption = Annotated[bool, typer.Option("--quiet", help="Errors only.")]


def common_from(
    *,
    config: Path | None,
    json_events: bool,
    yes: bool,
    verbose: int,
    quiet: bool,
) -> Common:
    """Bundle the global options and configure logging."""
    common = Common(
        config_path=config,
        json_events=json_events,
        yes=yes,
        non_interactive=yes or not sys.stdout.isatty(),
        verbosity=verbose,
        quiet=quiet,
    )
    configure_logging(common)
    return common


def config_for(out_dir: Path, common: Common) -> Config:
    """Load the configuration for an output directory under the precedence rules."""
    import os  # noqa: PLC0415 - keeps the environment read at call time for tests

    path = common.config_path or out_dir / CONFIG_FILENAME
    try:
        return load_config(path, environ=os.environ, overrides=common.overrides)
    except ConfigError as error:
        fail(str(error), ExitCode.USAGE)


def fail(message: str, code: ExitCode) -> NoReturn:
    """Print an error to stderr and exit with `code`."""
    print(f"docmirror: {message}", file=sys.stderr)
    raise typer.Exit(code=int(code))
