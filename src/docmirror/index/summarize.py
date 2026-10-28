"""The Summarizer protocol: a hook for a later LLM summarizer; `NoopSummarizer` is the default."""

from __future__ import annotations

from typing import Protocol


class Summarizer(Protocol):
    """Produces a description for a page from its title and Markdown body."""

    def summarize(self, title: str, body: str, fallback: str) -> str:
        """The description to index; `fallback` is the meta description or first paragraph."""


class NoopSummarizer:
    """Keeps the fallback description unchanged."""

    def summarize(self, title: str, body: str, fallback: str) -> str:
        """Return `fallback`."""
        del title, body
        return fallback


def summarizer_for(name: str) -> Summarizer:
    """The configured summarizer; only `none` exists."""
    if name != "none":
        message = f"unknown summarizer {name!r}; only 'none' is implemented"
        raise ValueError(message)
    return NoopSummarizer()
