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
    code_lang_attrs=["class:lang-", "class:language-", "data-lang", "data-language"],
    admonitions=[
        AdmonitionSpec(selector=".admonition", title=".admonition-title", kind_from="class"),
        AdmonitionSpec(selector="div.alert", title=".alert-title", kind_from="class"),
    ],
)

MSLEARN = Profile(
    main_selector=["main#main", "div.content"],
    # Learn renders its breadcrumb trail client-side from toc.json; the server HTML
    # has none, so this selector matches nothing and the trail stays absent.
    breadcrumb_selector="ul#breadcrumbs, .breadcrumbs",
    strip_selectors=[
        ".page-metadata-container",
        ".page-metadata",
        "#article-metadata",
        "#user-feedback",
        "nav",
        "[data-bi-name='feedback']",
        "[data-bi-name='pageactions']",
        "#article-header-page-actions",
        "#article-header-page-actions-overflow",
        "#article-header-breadcrumbs-overflow-popover",
        "details.popover",
        "#ms--additional-resources",
        "#ms--additional-resources-mobile",
        "#action-panel",
        ".skip-to-main-link",
        "[data-bi-name='breadcrumb']",
        ".visibility-hidden-visual-diff",
        "#ms--in-this-article",
        "#center-doc-outline",
        "#affixed-left-container",
        "#ms--collapsible-toc-header",
        "[data-id='ai-summary']",
        "#ms--ai-summary-header",
        "[unauthorized-private-section]",
        ".notification",
        "button",
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
    # Learn's callouts are `div.NOTE` (and TIP, IMPORTANT, WARNING, CAUTION) with the
    # kind as the class and the label in the first paragraph; the prompt's `div.alert`
    # is the older Docs markup and matches nothing here.
    admonitions=[
        AdmonitionSpec(
            selector="div.NOTE, div.TIP, div.IMPORTANT, div.WARNING, div.CAUTION, div.alert",
            title="p:first-child, p.alert-title",
            kind_from="class",
        )
    ],
    code_lang_attrs=["class:lang-", "class:language-", "data-lang", "data-language"],
    heading_anchor_style="attr",
    interactive_selectors=[".try-it", "[data-bi-name='try-it']", "[data-interactive-sample]"],
    last_updated_selector="local-time[datetime], time[datetime]",
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
        "devsite-recommendations-sidebar",
        "devsite-recommendations-dropdown",
        # The generated "Page Summary" panel is not part of the authored page.
        "devsite-key-takeaways-panel",
        ".nocontent",
        "[data-nosnippet]",
        ".devsite-rating",
        "devsite-ai-summary",
    ],
    tabs=[
        # `devsite-selector` holds one <section> per tab whose first heading is the
        # label; there is no server-rendered tablist.
        TabSpec(group="devsite-selector", panel="section", panel_heading="h2, h3, h4"),
        TabSpec(
            group="devsite-tabs:not(.upper-tabs)",
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
            title="strong, b",
            kind_from="class",
        )
    ],
    # devsite marks the language on `pre[syntax]` and terminals on `code.devsite-terminal`.
    code_lang_attrs=["syntax", "class:lang-", "class:language-", "data-lang", "data-language"],
    heading_anchor_style="attr",
    interactive_selectors=[
        "devsite-iframe",
        "devsite-code-explorer",
        ".devsite-embedded-apis-explorer",
        "devsite-apis-explorer",
    ],
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
