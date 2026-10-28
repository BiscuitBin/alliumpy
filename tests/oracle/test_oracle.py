"""Fidelity oracles (`-m oracle`): Learn's MCP Markdown and devsite's `.md.txt` endpoints."""

from __future__ import annotations

import json
import re
import urllib.request

import pytest

from docmirror.config.loader import validate_config
from docmirror.fetch.session import HttpFetcher
from docmirror.index.keywords import plain_text
from docmirror.pipeline import process_page
from docmirror.quality.measure import words

pytestmark = pytest.mark.oracle

LEARN_MCP = "https://learn.microsoft.com/api/mcp"
LEARN_PAGES = [
    "https://learn.microsoft.com/en-us/graph/api/user-get?view=graph-rest-1.0",
    "https://learn.microsoft.com/en-us/graph/api/user-list?view=graph-rest-1.0",
    "https://learn.microsoft.com/en-us/graph/api/resources/user?view=graph-rest-1.0",
    "https://learn.microsoft.com/en-us/graph/auth/auth-concepts",
    "https://learn.microsoft.com/en-us/graph/paging",
    "https://learn.microsoft.com/en-us/graph/errors",
    "https://learn.microsoft.com/en-us/graph/json-batching",
    "https://learn.microsoft.com/en-us/graph/throttling",
    "https://learn.microsoft.com/en-us/graph/query-parameters",
    "https://learn.microsoft.com/en-us/graph/overview",
]
DEVSITE_PAGES = [
    "https://developers.google.com/workspace/gmail/api/guides",
    "https://developers.google.com/workspace/gmail/api/guides/labels",
    "https://developers.google.com/workspace/gmail/api/guides/sending",
    "https://developers.google.com/workspace/gmail/api/guides/push",
    "https://developers.google.com/workspace/gmail/api/guides/filtering",
    "https://developers.google.com/workspace/gmail/api/guides/batch",
    "https://developers.google.com/workspace/gmail/api/guides/uploads",
    "https://developers.google.com/workspace/gmail/api/guides/threads",
    "https://developers.google.com/workspace/drive/api/guides/about-sdk",
    "https://developers.google.com/workspace/calendar/api/guides/create-events",
]
MIN_RECALL = 0.95


def _recall(oracle_markdown: str, ours: str) -> float:
    needed = words(plain_text(oracle_markdown))
    have: dict[str, int] = {}
    for token in words(plain_text(ours)):
        have[token] = have.get(token, 0) + 1
    hit = 0
    for token in needed:
        if have.get(token, 0):
            have[token] -= 1
            hit += 1
    return hit / len(needed) if needed else 1.0


async def _ours(url: str, profile: str) -> str:
    fetcher = HttpFetcher(impersonate="chrome", locale="en-us")
    try:
        result = await fetcher.fetch(url)
    finally:
        await fetcher.close()
    if not result.ok:
        pytest.skip(f"page unreachable: {url} ({result.status})")
    config = validate_config({"site": {"profile": profile}})
    return process_page(result.text(), result.final_url, config, config.profile()).markdown_body


def _learn_oracle(url: str) -> str:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "microsoft_docs_fetch", "arguments": {"url": url}},
    }
    request = urllib.request.Request(
        LEARN_MCP,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
            raw = response.read().decode("utf-8", errors="replace")
    except OSError as error:
        pytest.skip(f"Learn MCP oracle unreachable: {error}")
    texts: list[str] = []
    for line in raw.splitlines():
        line = line.removeprefix("data:").strip()  # noqa: PLW2901
        if not line.startswith("{"):
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        content = message.get("result", {}).get("content", [])
        texts.extend(item["text"] for item in content if item.get("type") == "text")
    if not texts:
        pytest.skip("Learn MCP oracle returned no Markdown")
    return "\n".join(texts)


def _devsite_oracle(url: str) -> str:
    request = urllib.request.Request(url + ".md.txt", headers={"User-Agent": "Mozilla/5.0"})  # noqa: S310
    try:
        with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
            if response.status != 200:
                pytest.skip(f"no .md.txt oracle for {url}")
            text: str = response.read().decode("utf-8", errors="replace")
    except OSError as error:
        pytest.skip(f".md.txt oracle unreachable: {error}")
    return text


@pytest.mark.parametrize("url", LEARN_PAGES)
def test_learn_oracle_recall(url: str) -> None:
    import asyncio  # noqa: PLC0415

    oracle = _learn_oracle(url)
    ours = asyncio.run(_ours(url, "mslearn"))
    recall = _recall(oracle, ours)
    assert recall >= MIN_RECALL, f"recall {recall:.3f} for {url}"


@pytest.mark.parametrize("url", DEVSITE_PAGES)
def test_devsite_oracle_recall(url: str) -> None:
    import asyncio  # noqa: PLC0415

    oracle = _devsite_oracle(url)
    oracle = re.sub(r"^---\n.*?\n---\n", "", oracle, count=1, flags=re.DOTALL)
    ours = asyncio.run(_ours(url, "devsite"))
    recall = _recall(oracle, ours)
    assert recall >= MIN_RECALL, f"recall {recall:.3f} for {url}"
