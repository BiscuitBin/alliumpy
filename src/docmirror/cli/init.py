"""`docmirror init`: seed a starter docmirror.toml and an empty manifest from a URL."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlsplit, urlunsplit

from docmirror.cli.common import LOG, Common, fail
from docmirror.config.loader import CONFIG_FILENAME, render_toml
from docmirror.config.models import Config, Scope, Site
from docmirror.config.profiles import detect_profile
from docmirror.exit_codes import ExitCode
from docmirror.state.db import atomic_write_text, open_manifest

if TYPE_CHECKING:
    from docmirror.config.models import Profile

_LOCALE = re.compile(r"^[a-z]{2}(?:-[a-z]{2,4})?$", re.IGNORECASE)

SITE_NAMES = {
    "mslearn": {"/graph": "Microsoft Graph"},
    "devsite": {"/workspace": "Google Workspace"},
}


def guess_locale(path: str) -> str:
    """The locale segment that leads the path, if any.

    >>> guess_locale("/en-us/graph/api/overview")
    'en-us'
    >>> guess_locale("/workspace/gmail/api/guides")
    ''
    """
    first = path.strip("/").split("/", 1)[0]
    return first.lower() if _LOCALE.match(first) else ""


def seed_config(url: str, profile_name: str | None = None) -> Config:
    """A starter configuration for `url`: host, prefix, locale, detected profile."""
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        message = f"not an http(s) URL: {url}"
        raise ValueError(message)
    name = profile_name or detect_profile(url)
    locale = guess_locale(parts.path)
    segments = [segment for segment in parts.path.split("/") if segment]
    directory = parts.path if parts.path.endswith("/") else parts.path.rsplit("/", 1)[0] + "/"
    prefix = directory
    if locale and len(segments) >= 2:  # noqa: PLR2004 - locale plus one product segment
        prefix = f"/{segments[0]}/{segments[1]}/"
    elif len(segments) >= 1:
        prefix = f"/{segments[0]}/"
    if not prefix.startswith("/"):
        prefix = "/" + prefix
    root_url = urlunsplit((parts.scheme, parts.netloc.lower(), prefix, "", ""))
    site_name = parts.netloc.lower()
    for marker, candidate in SITE_NAMES.get(name, {}).items():
        prefixes = (marker, f"/{locale}{marker}") if locale else (marker,)
        if parts.path.lower().startswith(prefixes):
            site_name = candidate
    scope = Scope(allowed_hosts=[parts.netloc.lower()], path_prefixes=[prefix])
    profile: Profile | None = None
    from docmirror.config.profiles import BUILTIN_PROFILES  # noqa: PLC0415 - avoid import cycles

    profile = BUILTIN_PROFILES.get(name)
    if profile is not None and profile.meaningful_query_params:
        scope.meaningful_query_params = list(profile.meaningful_query_params)
    if name == "mslearn" and "/graph" in parts.path.lower():
        scope.version_param = "view"
        scope.version_default = "v1.0"
        scope.version_map = {"graph-rest-1.0": "v1.0", "graph-rest-beta": "beta"}
        scope.exclude = ["re:/graph/(changelog|whats-new)", "**/toc.json"]
    site = Site(name=site_name, root_url=root_url, start_urls=[url], locale=locale, profile=name)
    return Config(site=site, scope=scope)


def run_init(url: str, out_dir: Path, common: Common, *, profile: str | None = None) -> ExitCode:
    """Create `out_dir`, write the starter TOML and create the manifest."""
    try:
        config = seed_config(url, profile)
    except ValueError as error:
        fail(str(error), ExitCode.USAGE)
    config_path = common.config_path or out_dir / CONFIG_FILENAME
    if config_path.exists():
        fail(f"{config_path} already exists; refusing to overwrite", ExitCode.USAGE)
    out_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_text(config_path, render_toml(config))
    with open_manifest(out_dir) as manifest:
        manifest.set_meta("root_url", config.site.root_url)
        manifest.set_meta("profile", config.site.profile)
    LOG.info("wrote %s (profile %s)", config_path, config.site.profile)
    common.emitter.emit(
        "init", out_dir=str(out_dir), config=str(config_path), profile=config.site.profile
    )
    if not common.json_events:
        print(f"Initialised {out_dir} with profile {config.site.profile}.")
        print(f"Next: docmirror crawl {out_dir}")
    return ExitCode.OK
