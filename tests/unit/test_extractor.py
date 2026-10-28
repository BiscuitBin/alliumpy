"""Main-content selection, stripping, metadata and shell detection."""

from __future__ import annotations

from docmirror.config.profiles import BUILTIN_PROFILES
from docmirror.extract import extract_page

PAGE = """
<html lang="en-us"><head><title>T | Site</title><meta name="description" content="Desc">
<meta property="og:title" content="OG"><link rel="canonical" href="/c"></head>
<body><nav>skip</nav><main id="main"><h1 id="t">Title</h1><p>Body text here.</p>
<div id="user-feedback">feedback</div><script>x()</script><div hidden>hidden chrome</div>
<section hidden><p>tab panel</p></section><p aria-hidden="true"></p>
<pre><code class="lang-http">GET /me</code></pre><h2 id="s">S</h2></main>
<ul class="breadcrumbs"><li>Home</li><li>Docs</li></ul></body></html>
"""


def test_profile_extraction_and_metadata() -> None:
    result = extract_page(PAGE, "https://h/docs/page", BUILTIN_PROFILES["mslearn"])
    assert result.extractor == "profile"
    text = result.content.text_content()
    assert "Body text" in text
    assert "feedback" not in text
    assert "hidden chrome" not in text
    assert "tab panel" in text
    assert "skip" not in text
    meta = result.metadata
    assert meta.title == "T | Site"
    assert meta.og_title == "OG"
    assert meta.description == "Desc"
    assert meta.canonical_url == "https://h/c"
    assert meta.lang == "en-us"
    assert meta.breadcrumbs == ["Home", "Docs"]
    assert meta.heading_ids == ["t", "s"]
    assert not meta.spa_shell


def test_fallback_when_no_selector_matches() -> None:
    page = "<html><body><div><p>" + "Real article content. " * 40 + "</p></div></body></html>"
    result = extract_page(page, "https://h/x", BUILTIN_PROFILES["mslearn"])
    assert result.extractor in {"trafilatura", "readability", "body"}
    assert "Real article" in result.content.text_content()


def test_spa_shell_and_noscript_signals() -> None:
    shell = '<html><body><div id="root"></div><noscript>You need to enable JavaScript.</noscript></body></html>'
    result = extract_page(shell, "https://h/x", BUILTIN_PROFILES["generic"])
    assert result.metadata.spa_shell
    assert result.metadata.noscript_needs_js
    assert result.text_chars < 50
