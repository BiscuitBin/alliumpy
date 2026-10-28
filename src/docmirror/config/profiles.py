"""Built-in extraction profiles and host-based detection.

The selectors are starting points verified against the live sites during the build;
`docs/site-notes.md` records what was found. Nothing outside this module and the
user's TOML names a site, so a new platform is a new profile, never a code branch.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from docmirror.config.models import AdmonitionSpec, Profile, TabSpec

if TYPE_CHECKING:
    from docmirror.config.models import Config

GENERIC = Profile(
    main_selector=["main", "article", "[role=main]", "#content", ".content"],
    strip_selectors=["nav", "header", "footer", "aside.sidebar", ".breadcrumb", ".breadcrumbs"],
    tabs=[
        TabSpec(
            group=".tabs, .tabbed-set, .tabGroup",
            label="[role=tab]",
            panel="[role=tabpanel]",
            panel_key="id",
            label_key="aria-controls",
        )
    ],
    admonitions=[
        AdmonitionSpec(selector=".admonition", title=".admonition-title", kind_from="class"),
        AdmonitionSpec(selector="div.alert", title=".alert-title", kind_from="class"),
    ],
)

MSLEARN = Profile(
    main_selector=["main#main", "div.content"],
    breadcrumb_selector="ul#breadcrumbs, .breadcrumbs",
    strip_selectors=[
        ".page-metadata",
        "[class^='feedback-']",
        "[class*=' feedback-']",
        "#user-feedback",
        "nav",
        "[data-bi-name='feedback']",
        "[data-bi-name='pageactions']",
        ".page-actions",
        "#article-header-page-actions",
        "#ms--additional-resources",
        ".metadata",
        "#action-panel",
        ".skip-to-main-link",
        "[data-bi-name='breadcrumb']",
    ],
    meaningful_query_params=["view"],
    tabs=[
        TabSpec(
            group=".tabGroup",
            label="ul[role=tablist] a[data-tab]",
            panel="section[data-tab]",
            panel_key="data-tab",
            label_key="data-tab",
        )
    ],
    admonitions=[AdmonitionSpec(selector="div.alert", title="p.alert-title", kind_from="class")],
    code_lang_attrs=["class:lang-", "class:language-", "data-lang", "data-language"],
    heading_anchor_style="attr",
    interactive_selectors=[".try-it", "[data-bi-name='try-it']", "iframe", "video"],
    last_updated_selector="time[data-article-date], time",
)

DEVSITE = Profile(
    main_selector=["article.devsite-article", ".devsite-article-body"],
    breadcrumb_selector=".devsite-breadcrumb-list",
    strip_selectors=[
        "devsite-feedback",
        ".devsite-article-meta",
        "devsite-toc",
        ".devsite-banner",
        "devsite-page-rating",
        "devsite-thumb-rating",
        ".devsite-page-title-meta",
        ".devsite-article-sitemap",
        "devsite-content-footer",
        ".devsite-breadcrumb-list",
        "devsite-actions",
        ".devsite-feedback-wrapper",
        "devsite-page-feedback",
    ],
    tabs=[
        TabSpec(
            group="devsite-selector",
            label="devsite-tabs tab",
            panel="section[aria-labelledby]",
            panel_key="aria-labelledby",
            label_key="id",
        ),
        TabSpec(
            group="devsite-tabs",
            label="tab",
            panel="div[role=tabpanel]",
            panel_key="aria-labelledby",
            label_key="id",
        ),
    ],
    admonitions=[
        AdmonitionSpec(
            selector="aside.note, aside.caution, aside.warning, aside.key-point, "
            "aside.objective, aside.tip, aside.important, aside.success, aside.beta, "
            "aside.deprecated, aside.special, aside.key-term, aside.dogfood, aside.experimental",
            title="b, strong",
            kind_from="class",
        )
    ],
    code_lang_attrs=["class:lang-", "class:language-", "data-lang", "data-language"],
    heading_anchor_style="attr",
    interactive_selectors=["devsite-iframe", "iframe", "devsite-code-explorer", "video"],
    last_updated_selector=".devsite-article-meta time, time[itemprop=dateModified]",
)

BUILTIN_PROFILES: dict[str, Profile] = {
    "generic": GENERIC,
    "mslearn": MSLEARN,
    "devsite": DEVSITE,
}

_HOST_HINTS: tuple[tuple[str, str], ...] = (
    ("learn.microsoft.com", "mslearn"),
    ("docs.microsoft.com", "mslearn"),
    ("developers.google.com", "devsite"),
    ("developer.android.com", "devsite"),
    ("cloud.google.com", "devsite"),
    ("firebase.google.com", "devsite"),
)


def detect_profile(url: str) -> str:
    """The built-in profile name for a URL's host, or `generic`.

    >>> detect_profile("https://learn.microsoft.com/en-us/graph/")
    'mslearn'
    >>> detect_profile("https://example.org/docs/")
    'generic'
    """
    host = urlsplit(url).hostname or ""
    for suffix, name in _HOST_HINTS:
        if host == suffix or host.endswith("." + suffix):
            return name
    return "generic"


def resolve_profile(config: Config) -> Profile:
    """The active profile: the built-in merged under the TOML's overrides for that name."""
    name = config.site.profile
    base = BUILTIN_PROFILES.get(name, GENERIC)
    override = config.extract.profiles.get(name)
    if override is None:
        return base
    merged = base.model_dump()
    merged.update(override.model_dump(exclude_unset=True))
    return Profile.model_validate(merged)
