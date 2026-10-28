"""Each DOM transform on a small fragment, through the real converter."""

from __future__ import annotations

import copy

from lxml import html

from docmirror.config.models import AdmonitionSpec, Profile, TabSpec
from docmirror.convert import convert_html, postprocess
from docmirror.normalize import normalize
from docmirror.normalize.code_lang import detect_language, normalize_alias
from docmirror.quality import measure_quality

PROFILE = Profile(
    tabs=[
        TabSpec(
            group=".tabGroup",
            label="ul[role=tablist] a[data-tab]",
            panel="section[data-tab]",
            panel_key="data-tab",
            label_key="data-tab",
        ),
        TabSpec(group="devsite-selector", panel="section", panel_heading="h2, h3, h4"),
    ],
    admonitions=[
        AdmonitionSpec(
            selector="div.NOTE, div.TIP, div.alert", title="p:first-child", kind_from="class"
        ),
        AdmonitionSpec(selector="aside.note, aside.special", title="strong, b", kind_from="class"),
    ],
    code_lang_attrs=["syntax", "class:lang-", "class:language-", "data-lang"],
    interactive_selectors=[".try-it"],
)


def run(fragment: str, profile: Profile = PROFILE, backend: str = "html-to-markdown") -> str:
    content = html.fragment_fromstring(fragment, create_parent="div")
    content.make_links_absolute("https://h/docs/")
    result = normalize(content, profile, title="")
    raw = convert_html(result.fragment, backend)  # type: ignore[arg-type]
    return postprocess(result.islands.restore(raw))


def counts_of(fragment: str) -> dict[str, int]:
    content = html.fragment_fromstring(fragment, create_parent="div")
    return normalize(content, PROFILE).counts


LEARN_TABS = (
    '<div class="tabGroup"><ul role="tablist">'
    '<li><a data-tab="http" href="#tabpanel_1_http">HTTP</a></li>'
    '<li><a data-tab="csharp" href="#tabpanel_1_csharp">C#</a></li></ul>'
    '<section data-tab="http"><pre><code class="lang-http">GET https://graph.microsoft.com/v1.0/me'
    "</code></pre></section>"
    '<section data-tab="csharp" hidden><pre><code class="lang-csharp">'
    "var user = await graphClient.Me.GetAsync();</code></pre></section></div>"
)


def test_language_tabs_become_labelled_fences() -> None:
    expected = (
        "**HTTP**\n\n```http\nGET https://graph.microsoft.com/v1.0/me\n```\n\n"
        "**C#**\n\n```csharp\nvar user = await graphClient.Me.GetAsync();\n```\n"
    )
    assert run(LEARN_TABS) == expected
    counts = counts_of(LEARN_TABS)
    assert counts["tab_panels"] == counts["tab_panels_emitted"] == 2


def test_both_backends_agree_on_tabs() -> None:
    assert run(LEARN_TABS, backend="markdownify") == run(LEARN_TABS)


def test_mixed_tabs_become_headings_below_the_enclosing_level() -> None:
    fragment = (
        "<h2>Samples</h2><div class='tabGroup'><ul role='tablist'>"
        "<li><a data-tab='a' href='#a'>Windows</a></li><li><a data-tab='b' href='#b'>macOS</a></li></ul>"
        "<section data-tab='a'><p>Use the installer.</p></section>"
        "<section data-tab='b' hidden><p>Use brew.</p><pre><code>brew install x</code></pre></section></div>"
    )
    out = run(fragment)
    assert (
        "### Windows\n\nUse the installer.\n\n### macOS\n\nUse brew.\n\n```bash\nbrew install x\n```"
        in out
    )


def test_devsite_selector_uses_panel_headings() -> None:
    fragment = (
        "<devsite-selector><section><h3 id='go'>Go</h3><devsite-code><pre syntax='Go'><code>x := 1</code></pre>"
        "</devsite-code></section><section><h3 id='java'>Java</h3><devsite-code><pre syntax='Java'>"
        "<code>int x = 1;</code></pre></devsite-code></section></devsite-selector>"
    )
    assert run(fragment) == "**Go**\n\n```go\nx := 1\n```\n\n**Java**\n\n```java\nint x = 1;\n```\n"


def test_code_language_sources_and_aliases() -> None:
    assert normalize_alias("cs") == "csharp"
    assert normalize_alias("Lang-JS") == "javascript"
    assert normalize_alias("console") == "bash"
    assert normalize_alias("Bash Session") == "bash"
    pre = html.fromstring("<pre><code data-lang='PowerShell'>x</code></pre>")
    assert detect_language(pre, PROFILE.code_lang_attrs) == "powershell"
    pre = html.fromstring("<pre><code>GET /me HTTP/1.1</code></pre>")
    assert detect_language(pre, PROFILE.code_lang_attrs) == "http"
    pre = html.fromstring("<pre><code>HTTP/1.1 200 OK</code></pre>")
    assert detect_language(pre, PROFILE.code_lang_attrs) == "http"
    pre = html.fromstring("<pre><code class='devsite-terminal'>ls</code></pre>")
    assert detect_language(pre, PROFILE.code_lang_attrs) == "bash"
    pre = html.fromstring("<pre>gem install google-api-client</pre>")
    assert detect_language(pre, PROFILE.code_lang_attrs) == "bash"
    pre = html.fromstring('<pre>{"kind": "x"}</pre>')
    assert detect_language(pre, PROFILE.code_lang_attrs) == "json"
    pre = html.fromstring("<pre>node .</pre>")
    assert detect_language(pre, PROFILE.code_lang_attrs) == "bash"
    for text, language in [
        ("python setup.py install", "bash"),
        ('{\n   "kind": "directory#mobiledevice",\n   ...\n}', "json"),
        ("<entry xmlns='http://www.w3.org/2005/Atom'><id>x</id></entry>", "xml"),
        (" import com.google.type.Color;\n\n // ...\n public static Color f(Color c)", "java"),
        (" @Rule public ResetConfigRule resetConfig = new ResetConfigRule();", "java"),
        (" static UIColor* fromProto(Color* protocolor) {", "objectivec"),
        ("// ...\n\nvar protoToCssColor = function(rgb_color) {", "javascript"),
        ("using Microsoft.Graph;\nvar client = new GraphServiceClient();", "csharp"),
        ("Snippet not available", "text"),
        ("https://sites.google.com/feeds/site/domainName", "text"),
        ("03b07b79-c5bc-4b5e-9bfa-13acf4a99998", "text"),
        ("+-------------+\n| Magic header |\n+-------------+", "text"),
        ("x = f(1)", ""),
    ]:
        pre = html.fromstring("<pre></pre>")
        pre.text = text
        assert detect_language(pre, PROFILE.code_lang_attrs) == language, text


def test_code_block_keeps_whitespace_and_strips_gutters_and_links() -> None:
    fragment = (
        "<pre><code class='language-py'><span class='line-number'>1</span>def f():\n"
        "    return <a href='/x'>g</a>()\n\n\nprint(1)</code></pre>"
    )
    assert run(fragment) == "```python\ndef f():\n    return g()\n\n\nprint(1)\n```\n"


def test_fence_is_longer_than_backtick_runs() -> None:
    out = run("<pre><code class='lang-md'>```js\nx\n```</code></pre>")
    assert out.startswith("````md\n```js\n")


def test_admonitions_map_to_gfm_alerts() -> None:
    fragment = (
        "<div class='NOTE'><p>Note</p><p>Body <code>x</code>.</p></div>"
        "<div class='TIP'><p>Tip</p><ul><li>one</li></ul></div>"
        "<aside class='special'><strong>Important:</strong> Sync first.</aside>"
        "<aside class='note'>Plain note.</aside>"
        "<div class='alert'><p>Remember</p><p>Unknown kind keeps its label.</p></div>"
    )
    out = run(fragment)
    assert "> [!NOTE]\n>\n> Body `x`.\n" in out
    assert "> [!TIP]\n>\n> - one\n" in out
    assert "> [!IMPORTANT]\n>\n> Sync first.\n" in out
    assert "> [!NOTE]\n>\n> Plain note.\n" in out
    assert "> [!NOTE]\n>\n> **Remember**\n>\n> Unknown kind keeps its label.\n" in out


def test_simple_table_is_pipe_table_with_escaped_pipes() -> None:
    out = run("<table><tr><th>a</th><th>b|c</th></tr><tr><td><p>1</p></td><td>2</td></tr></table>")
    assert out == "| a | b\\|c |\n| --- | ---- |\n| 1 | 2    |\n"


def test_complex_table_is_sanitized_html() -> None:
    fragment = (
        "<table class='x' style='w'><tr><td rowspan='2' data-x='1'>a</td>"
        "<td><p>x</p><p>y</p></td></tr></table>"
    )
    out = run(fragment)
    assert out.startswith("<table>")
    assert 'rowspan="2"' in out
    assert "data-x" not in out
    assert "class=" not in out
    counts = counts_of(fragment)
    assert counts["tables"] == 1
    assert counts["html_tables"] == 1
    assert counts["table_cells"] == 2


def test_single_row_headerless_table_stays_html() -> None:
    fragment = "<table><tr><td><a href='/i'>Impl</a></td><td>Description</td></tr></table>"
    out = run(fragment)
    assert out.startswith("<table>")
    assert counts_of(fragment)["html_tables"] == 1


def test_row_header_table_stays_html() -> None:
    fragment = (
        "<table><tr><th>base</th><td>x</td></tr><tr><th>description</th><td>y</td></tr></table>"
    )
    assert run(fragment).startswith("<table>")
    column_headers = "<table><tr><th>a</th><th>b</th></tr><tr><td>1</td><td>2</td></tr></table>"
    assert run(column_headers).startswith("| a | b |")


def test_newline_runs_in_text_collapse_outside_code() -> None:
    fragment = "<ul><li>Install the\n      \n      Node.js <a href='/l'>library</a>.</li></ul>"
    assert run(fragment) == "- Install the Node.js [library](https://h/l).\n"
    assert run("<pre><code>a = 1\n\nb(2)</code></pre>") == "```\na = 1\n\nb(2)\n```\n"


def test_layout_table_is_unwrapped() -> None:
    assert run("<table><tr><td><p>Only content</p></td></tr></table>") == "Only content\n"


def test_definition_list_inline_and_block() -> None:
    out = run("<dl><dt>Term</dt><dd>The <em>definition</em> text.</dd></dl>")
    assert out == "**Term**\n    The *definition* text.\n"
    block = run("<dl><dt>T</dt><dd><p>one</p><p>two</p></dd></dl>")
    assert block.startswith("<dl>")


def test_details_keeps_html_with_markdown_inside() -> None:
    out = run("<details open><summary>More</summary><p>Hidden <b>text</b></p></details>")
    assert out == "<details open>\n<summary>More</summary>\n\nHidden **text**\n\n</details>\n"


def test_images_and_figures() -> None:
    out = run(
        "<figure><img src='/i.png' alt=''><figcaption>Cap</figcaption></figure><img src='/j.png' alt='' title='T'>"
    )
    assert out == '![Cap](https://h/i.png)\n\n*Cap*\n\n![T](https://h/j.png "T")\n'


def test_headings_keep_ids_and_single_h1() -> None:
    out = run("<h1 id='a'>A</h1><h1 id='b'>B</h1><h2 id='c'>C <a href='/x'>link</a></h2>")
    assert out == "# A {#a}\n\n## B {#b}\n\n### C [link](https://h/x) {#c}\n"
    assert run("<h2 id='create_the_script'>Create</h2>") == "## Create {#create_the_script}\n"
    inline = Profile(heading_anchor_style="inline")
    assert run("<h2 id='x'>X</h2>", inline) == '<a id="x"></a>\n\n## X\n'


def test_named_anchors_survive() -> None:
    # javadoc-style: an empty `<a name>` before the heading lends it the id.
    out = run("<a name='shutdown()'></a><h4>shutdown()</h4><p>x</p>")
    assert out == "#### shutdown() {#shutdown()}\n\nx\n"
    # A heading with its own id keeps it; the anchor travels as an `<a id>` island.
    out = run("<a name='m()'></a><h4 id='own'>m</h4>")
    assert out == '<a id="m()"></a>\n\n#### m {#own}\n'
    out = run("<p>See <a name='here'>this point</a> later.</p>")
    assert out == 'See <a id="here"></a>this point later.\n'


def test_ids_on_converted_blocks_become_anchors() -> None:
    # An alert keeps its id; a paragraph keeps one only when the page links to it.
    fragment = (
        "<p>See <a href='#n'>note</a> and <a href='#p2'>there</a>.</p>"
        "<aside class='note' id='n'><strong>Note:</strong> Body.</aside>"
        "<p id='p1'>Untargeted.</p><p id='p2'>Targeted.</p>"
    )
    out = run(fragment)
    assert '<a id="n"></a>\n\n> [!NOTE]\n>\n> Body.\n' in out
    assert "Untargeted." in out
    assert 'id="p1"' not in out
    assert '<a id="p2"></a>\n\nTargeted.\n' in out


def test_inline_html_elements_are_kept() -> None:
    out = run("<p>Press <kbd>Ctrl</kbd>, H<sub>2</sub>O, x<sup>2</sup>, <mark>hi</mark></p>")
    assert out == "Press <kbd>Ctrl</kbd>, H<sub>2</sub>O, x<sup>2</sup>, <mark>hi</mark>\n"


def test_math_from_annotations_and_scripts() -> None:
    fragment = (
        "<p>Inline <math><mi>x</mi><annotation encoding='application/x-tex'>x_1</annotation></math> here.</p>"
        "<script type='math/tex; mode=display'>a^2 + b^2</script>"
        "<span class='katex'><annotation encoding='application/x-tex'>\\\\frac{1}{2}</annotation></span>"
    )
    out = run(fragment)
    assert "Inline $x_1$ here." in out
    assert "$$a^2 + b^2$$" in out
    assert "$\\\\frac{1}{2}$" in out


def test_footnotes() -> None:
    fragment = (
        "<p>Claim<sup><a href='#fn1' id='fnref1'>1</a></sup>.</p>"
        "<section class='footnotes'><ol><li id='fn1'><p>Source <a href='#fnref1'>↩</a></p>"
        "</li></ol></section>"
    )
    out = run(fragment)
    assert "Claim[^1]." in out
    assert "[^1]: Source" in out


def test_interactive_placeholders() -> None:
    out = run(
        "<iframe src='https://x/embed'></iframe><div class='try-it'>Try it</div>"
        "<video><source src='/v.mp4'></video>"
    )
    assert "> [!NOTE] Interactive content omitted: https://x/embed" in out
    assert "> [!NOTE] Interactive content omitted: div" in out
    assert "> [!NOTE] Interactive content omitted: https://h/v.mp4" in out


def test_forms_keep_their_text_and_links() -> None:
    fragment = (
        "<form method='get' action='https://s/search'><input type='text' name='q'>"
        "<p><button type='submit'>Search existing</button> "
        "<a class='button' href='/ask'>Ask a new question</a></p></form><p>After.</p>"
    )
    assert run(fragment) == "Search existing [Ask a new question](https://h/ask)\n\nAfter.\n"
    assert run(fragment, backend="markdownify") == run(fragment)


def test_quality_measures_every_gate() -> None:
    fragment = (
        "<h2 id='a'>A</h2><p>Hello <a href='/x'>world</a> words</p>"
        "<ul><li>one</li><li>two</li></ul><pre><code class='lang-json'>{}</code></pre>"
        "<table><tr><th>h</th></tr><tr><td>c</td></tr></table>"
        "<img src='/i.png' alt='i'>"
    )
    content = html.fragment_fromstring(fragment, create_parent="div")

    dom = copy.deepcopy(content)
    result = normalize(content, PROFILE)
    body = postprocess(result.islands.restore(convert_html(result.fragment)))
    quality = measure_quality(dom, body, result.counts)
    assert quality.failed == []
    assert quality.score == 1.0
    assert quality.metrics["headings"] == quality.metrics["dom_headings"] == 1.0
    assert quality.metrics["table_cells"] == 2.0
    lossy = measure_quality(dom, body.replace("world", "").replace("```json", "```"), result.counts)
    assert "code_lang_rate" in lossy.failed
    assert lossy.score < 1.0
