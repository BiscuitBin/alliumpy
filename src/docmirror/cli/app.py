"""The `docmirror` command."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Annotated, Literal

import typer

from docmirror import __version__
from docmirror.cli.common import (
    ConfigOption,
    JsonOption,
    QuietOption,
    VerboseOption,
    YesOption,
    common_from,
)
from docmirror.exit_codes import ExitCode

app = typer.Typer(
    name="docmirror",
    help="Mirror a documentation website into a local, interlinked Markdown knowledge base.",
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode=None,
    pretty_exceptions_enable=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def _version(value: bool) -> None:
    if value:
        print(f"docmirror {__version__}")
        raise typer.Exit(code=0)


@app.callback()
def _root(
    version: Annotated[
        bool,
        typer.Option("--version", callback=_version, is_eager=True, help="Print the version."),
    ] = False,
) -> None:
    """Mirror a documentation website into a local, interlinked Markdown knowledge base."""


@app.command("init")
def init_command(
    url: Annotated[str, typer.Argument(help="A page or root URL of the documentation site.")],
    out_dir: Annotated[Path, typer.Argument(help="The output directory to create.")],
    config: ConfigOption = None,
    json_events: JsonOption = False,
    yes: YesOption = False,
    verbose: VerboseOption = 0,
    quiet: QuietOption = False,
    profile: Annotated[
        str | None, typer.Option("--profile", help="Force a built-in profile name.")
    ] = None,
) -> None:
    """Create OUT_DIR with a starter docmirror.toml and an empty manifest. Does not crawl."""
    from docmirror.cli.init import run_init  # noqa: PLC0415 - lazy subcommand import

    common = common_from(
        config=config, json_events=json_events, yes=yes, verbose=verbose, quiet=quiet
    )
    raise typer.Exit(code=int(run_init(url, out_dir, common, profile=profile)))


@app.command("doctor")
def doctor_command(
    json_events: JsonOption = False,
    verbose: VerboseOption = 0,
    quiet: QuietOption = False,
) -> None:
    """Check the environment: Python, curl_cffi, the Patchright browser, Camoufox, write access."""
    from docmirror.cli.doctor import run_doctor  # noqa: PLC0415

    common = common_from(
        config=None, json_events=json_events, yes=True, verbose=verbose, quiet=quiet
    )
    raise typer.Exit(code=int(run_doctor(common)))


@app.command("schema")
def schema_command(
    artifact: Annotated[
        str, typer.Argument(help="One of: config, report, frontmatter, index.")
    ] = "config",
) -> None:
    """Print the JSON Schema (draft 2020-12) for the named artifact."""
    from docmirror.cli.schema import schema_for  # noqa: PLC0415

    try:
        document = schema_for(artifact)
    except KeyError:
        print(
            f"docmirror: unknown schema {artifact!r}; choose config, report, frontmatter or index",
            file=sys.stderr,
        )
        raise typer.Exit(code=int(ExitCode.USAGE)) from None
    print(json.dumps(document, indent=2, sort_keys=False))


@app.command("report")
def report_command(
    out_dir: Annotated[Path, typer.Argument(help="An initialised output directory.")],
    json_events: JsonOption = False,
    verbose: VerboseOption = 0,
    quiet: QuietOption = False,
) -> None:
    """Print the last crawl-report.json as a human table, or as JSON with --json."""
    from docmirror.cli.report import run_report  # noqa: PLC0415

    common = common_from(
        config=None, json_events=json_events, yes=True, verbose=verbose, quiet=quiet
    )
    raise typer.Exit(code=int(run_report(out_dir, common)))


CrawlMode = Literal["crawl", "update"]


def _crawl_like(
    mode: CrawlMode,
    out_dir: Path,
    common_kwargs: dict[str, object],
    overrides: dict[str, object],
    flags: dict[str, object],
) -> None:
    from docmirror.cli.crawl import run_crawl  # noqa: PLC0415

    common = common_from(
        config=common_kwargs["config"],  # type: ignore[arg-type]
        json_events=bool(common_kwargs["json_events"]),
        yes=bool(common_kwargs["yes"]),
        verbose=int(common_kwargs["verbose"]),  # type: ignore[call-overload]
        quiet=bool(common_kwargs["quiet"]),
    )
    common.overrides = {k: v for k, v in overrides.items() if v is not None}
    raise typer.Exit(code=int(run_crawl(mode, out_dir, common, flags)))


def _crawl_signature(mode: CrawlMode):  # type: ignore[no-untyped-def]  # noqa: ANN202
    def command(
        out_dir: Annotated[Path, typer.Argument(help="An initialised output directory.")],
        config: ConfigOption = None,
        json_events: JsonOption = False,
        yes: YesOption = False,
        verbose: VerboseOption = 0,
        quiet: QuietOption = False,
        allow_host: Annotated[list[str] | None, typer.Option("--allow-host")] = None,
        path_prefix: Annotated[list[str] | None, typer.Option("--path-prefix")] = None,
        include: Annotated[list[str] | None, typer.Option("--include")] = None,
        exclude: Annotated[list[str] | None, typer.Option("--exclude")] = None,
        max_depth: Annotated[int | None, typer.Option("--max-depth")] = None,
        max_pages: Annotated[int | None, typer.Option("--max-pages")] = None,
        max_bytes: Annotated[str | None, typer.Option("--max-bytes")] = None,
        locale: Annotated[str | None, typer.Option("--locale")] = None,
        rate: Annotated[
            float | None, typer.Option("--rate", help="Requests per second per host.")
        ] = None,
        concurrency: Annotated[int | None, typer.Option("--concurrency")] = None,
        robots: Annotated[str | None, typer.Option("--robots", help="respect | ignore")] = None,
        render: Annotated[
            str | None, typer.Option("--render", help="auto | never | always")
        ] = None,
        stealth: Annotated[
            str | None, typer.Option("--stealth", help="off | patchright | camoufox")
        ] = None,
        user_agent: Annotated[str | None, typer.Option("--user-agent")] = None,
        timeout: Annotated[float | None, typer.Option("--timeout")] = None,
        resume: Annotated[bool, typer.Option("--resume/--no-resume")] = True,
        dry_run: Annotated[
            bool, typer.Option("--dry-run", help="Print the planned frontier and exit.")
        ] = False,
        prune: Annotated[bool | None, typer.Option("--prune/--no-prune")] = None,
        fail_on_low_quality: Annotated[
            bool | None, typer.Option("--fail-on-low-quality/--no-fail-on-low-quality")
        ] = None,
        max_age: Annotated[
            str | None, typer.Option("--max-age", help="Refetch pages older than this, e.g. 7d.")
        ] = None,
    ) -> None:
        overrides: dict[str, object] = {
            "scope.allowed_hosts": allow_host,
            "scope.path_prefixes": path_prefix,
            "scope.include": include,
            "scope.exclude": exclude,
            "scope.max_depth": max_depth,
            "scope.max_pages": max_pages,
            "scope.max_bytes": max_bytes,
            "site.locale": locale,
            "fetch.rate_per_host": rate,
            "fetch.concurrency_per_host": concurrency,
            "fetch.robots": robots,
            "render.mode": render,
            "antibot.stealth": stealth,
            "fetch.user_agent": user_agent,
            "fetch.timeout_s": timeout,
            "update.prune": prune,
            "report.fail_on_low_quality": fail_on_low_quality,
            "update.max_age": max_age,
        }
        _crawl_like(
            mode,
            out_dir,
            {
                "config": config,
                "json_events": json_events,
                "yes": yes,
                "verbose": verbose,
                "quiet": quiet,
            },
            overrides,
            {"resume": resume, "dry_run": dry_run},
        )

    return command


app.command("crawl", help="Full crawl per config; on a populated directory behaves like update.")(
    _crawl_signature("crawl")
)
app.command(
    "update", help="Incremental run: sitemap lastmod, conditional GETs, tombstones and redirects."
)(_crawl_signature("update"))


@app.command("verify")
def verify_command(
    out_dir: Annotated[Path, typer.Argument(help="An initialised output directory.")],
    config: ConfigOption = None,
    json_events: JsonOption = False,
    yes: YesOption = False,
    verbose: VerboseOption = 0,
    quiet: QuietOption = False,
) -> None:
    """Offline: re-run quality gates, check every relative link and fragment, and the manifest."""
    from docmirror.cli.verify import run_verify  # noqa: PLC0415

    common = common_from(
        config=config, json_events=json_events, yes=yes, verbose=verbose, quiet=quiet
    )
    raise typer.Exit(code=int(run_verify(out_dir, common)))


@app.command("index")
def index_command(
    out_dir: Annotated[Path, typer.Argument(help="An initialised output directory.")],
    config: ConfigOption = None,
    json_events: JsonOption = False,
    yes: YesOption = False,
    verbose: VerboseOption = 0,
    quiet: QuietOption = False,
) -> None:
    """Offline: regenerate index.md, index.jsonl, llms.txt and per-directory _index.md."""
    from docmirror.cli.index import run_index  # noqa: PLC0415

    common = common_from(
        config=config, json_events=json_events, yes=yes, verbose=verbose, quiet=quiet
    )
    raise typer.Exit(code=int(run_index(out_dir, common)))


@app.command("fetch")
def fetch_command(
    url: Annotated[str, typer.Argument(help="The page to fetch and convert.")],
    config: ConfigOption = None,
    json_events: JsonOption = False,
    yes: YesOption = False,
    verbose: VerboseOption = 0,
    quiet: QuietOption = False,
    tier: Annotated[str | None, typer.Option("--tier", help="http | browser | stealth")] = None,
    dump_html: Annotated[
        Path | None, typer.Option("--dump-html", help="Save the extracted main-content HTML.")
    ] = None,
    profile: Annotated[str | None, typer.Option("--profile", help="Force a profile name.")] = None,
) -> None:
    """Debug: fetch and convert one page to stdout using the config's pipeline."""
    from docmirror.cli.fetch import run_fetch  # noqa: PLC0415

    common = common_from(
        config=config, json_events=json_events, yes=yes, verbose=verbose, quiet=quiet
    )
    raise typer.Exit(
        code=int(run_fetch(url, common, tier=tier, dump_html=dump_html, profile=profile))
    )


def main() -> None:
    """Console-script entry point."""
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
