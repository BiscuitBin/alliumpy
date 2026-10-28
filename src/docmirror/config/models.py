"""The configuration schema: one pydantic model per TOML section.

Unknown keys are errors (exit 2) with the key path in the message, which `extra="forbid"`
provides. Every field carries its default, so an empty TOML is a valid configuration
once `[site] root_url` is set.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from docmirror.config.units import parse_duration, parse_size

RenderMode = Literal["auto", "never", "always"]
Stealth = Literal["off", "patchright", "camoufox"]
Robots = Literal["respect", "ignore"]
Backend = Literal["html-to-markdown", "markdownify"]
AnchorStyle = Literal["attr", "inline"]
Tier = Literal["http", "browser", "stealth"]
Fallback = Literal["trafilatura", "readability"]


class Section(BaseModel):
    """Base for every section: unknown keys are configuration errors."""

    model_config = ConfigDict(extra="forbid", validate_default=True)


class Site(Section):
    """`[site]`: what is mirrored and which profile reads it."""

    name: str = ""
    root_url: str = ""
    start_urls: list[str] = Field(default_factory=list)
    locale: str = ""
    profile: str = "generic"


class Scope(Section):
    """`[scope]`: which URLs are in the mirror."""

    allowed_hosts: list[str] = Field(default_factory=list)
    path_prefixes: list[str] = Field(default_factory=list)
    include: list[str] = Field(default_factory=list)
    exclude: list[str] = Field(default_factory=list)
    max_depth: int = Field(default=10, ge=0)
    max_pages: int = Field(default=5000, ge=1)
    max_bytes: str = "2GiB"
    meaningful_query_params: list[str] = Field(default_factory=list)
    version_param: str = ""
    version_default: str = ""
    version_map: dict[str, str] = Field(default_factory=dict)

    @field_validator("max_bytes")
    @classmethod
    def _size(cls, value: str) -> str:
        parse_size(value)
        return value

    @property
    def max_bytes_int(self) -> int:
        """`max_bytes` in bytes."""
        return parse_size(self.max_bytes)


class Provider(Section):
    """`[fetch.provider]`: reserved for an unblocking provider; not implemented."""

    name: str = ""
    enabled: bool = False

    @model_validator(mode="after")
    def _reserved(self) -> Provider:
        if self.enabled or self.name:
            message = "[fetch.provider] is reserved and not implemented in this version"
            raise ValueError(message)
        return self


class Fetch(Section):
    """`[fetch]`: politeness, retries and impersonation."""

    rate_per_host: float = Field(default=2.0, gt=0)
    concurrency_per_host: int = Field(default=4, ge=1)
    timeout_s: float = Field(default=30.0, gt=0)
    retries: int = Field(default=5, ge=1)
    robots: Robots = "respect"
    impersonate: str = "chrome"
    user_agent: str = ""
    provider: Provider = Field(default_factory=Provider)


class Render(Section):
    """`[render]`: when and how a page is rendered in a browser."""

    mode: RenderMode = "auto"
    min_text_chars: int = Field(default=200, ge=0)
    wait_until: Literal["load", "domcontentloaded", "networkidle", "commit"] = "networkidle"
    max_wait_s: float = Field(default=20.0, gt=0)


class Antibot(Section):
    """`[antibot]`: stealth tier and the circuit breaker."""

    stealth: Stealth = "patchright"
    window: int = Field(default=50, ge=1)
    block_rate_threshold: float = Field(default=0.20, gt=0, le=1)
    pause_s: float = Field(default=30.0, ge=0)


class TabSpec(Section):
    """One tab-group shape: the group, its labels and its panels."""

    group: str
    label: str
    panel: str
    panel_key: str = ""
    label_key: str = ""


class AdmonitionSpec(Section):
    """One admonition shape and how its kind and title are read."""

    selector: str
    title: str = ""
    kind_from: Literal["class", "title", "tag"] = "class"


class Profile(Section):
    """`[extract.profiles.<name>]`: every selector the extractor and normalizers use."""

    main_selector: list[str] = Field(default_factory=list)
    breadcrumb_selector: str = ""
    strip_selectors: list[str] = Field(default_factory=list)
    meaningful_query_params: list[str] = Field(default_factory=list)
    tabs: list[TabSpec] = Field(default_factory=list)
    admonitions: list[AdmonitionSpec] = Field(default_factory=list)
    code_lang_attrs: list[str] = Field(
        default_factory=lambda: ["class:lang-", "class:language-", "data-lang", "data-language"]
    )
    heading_anchor_style: AnchorStyle = "attr"
    interactive_selectors: list[str] = Field(default_factory=list)
    login_wall_selector: str = ""
    last_updated_selector: str = ""
    lowercase_paths: bool = False
    # Compatibility aliases for the flat keys the specification's example uses.
    tab_group: str = ""
    tab_label: str = ""
    tab_panel: str = ""
    admonition: str = ""
    admonition_title: str = ""

    @model_validator(mode="after")
    def _fold_flat_keys(self) -> Profile:
        if self.tab_group and not self.tabs:
            self.tabs = [TabSpec(group=self.tab_group, label=self.tab_label, panel=self.tab_panel)]
            self.__pydantic_fields_set__.add("tabs")
        if self.admonition and not self.admonitions:
            self.admonitions = [
                AdmonitionSpec(selector=self.admonition, title=self.admonition_title)
            ]
            self.__pydantic_fields_set__.add("admonitions")
        return self


def _default_fallbacks() -> list[Fallback]:
    return ["trafilatura", "readability"]


class Extract(Section):
    """`[extract]`: the fallback order and the profiles."""

    fallbacks: list[Fallback] = Field(default_factory=_default_fallbacks)
    profiles: dict[str, Profile] = Field(default_factory=dict)


class Convert(Section):
    """`[convert]`: the HTML-to-Markdown backend."""

    backend: Backend = "html-to-markdown"
    bullet: Literal["-", "*", "+"] = "-"


class Links(Section):
    """`[links]`: path mapping and link rewriting."""

    path_template: str = "{path}"
    keep_external_absolute: bool = True


class Index(Section):
    """`[index]`: the root index writers."""

    keywords_per_page: int = Field(default=8, ge=1, le=20)
    hierarchical_threshold: int = Field(default=200, ge=1)
    summarizer: Literal["none"] = "none"


class Update(Section):
    """`[update]`: incremental-run behaviour."""

    max_age: str = ""
    prune: bool = False

    @field_validator("max_age")
    @classmethod
    def _duration(cls, value: str) -> str:
        parse_duration(value)
        return value

    @property
    def max_age_delta(self) -> timedelta | None:
        """`max_age` as a timedelta, or None when unset."""
        return parse_duration(self.max_age)


class Report(Section):
    """`[report]`: what fails the run."""

    fail_on_low_quality: bool = False


class Config(Section):
    """The whole `docmirror.toml`."""

    site: Site = Field(default_factory=Site)
    scope: Scope = Field(default_factory=Scope)
    fetch: Fetch = Field(default_factory=Fetch)
    render: Render = Field(default_factory=Render)
    antibot: Antibot = Field(default_factory=Antibot)
    extract: Extract = Field(default_factory=Extract)
    convert: Convert = Field(default_factory=Convert)
    links: Links = Field(default_factory=Links)
    index: Index = Field(default_factory=Index)
    update: Update = Field(default_factory=Update)
    report: Report = Field(default_factory=Report)

    def profile(self) -> Profile:
        """The active profile: the built-in of that name under the TOML's overrides."""
        from docmirror.config.profiles import resolve_profile  # noqa: PLC0415 - avoids a cycle

        return resolve_profile(self)
