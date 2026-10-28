"""Fetching: curl_cffi sessions, politeness, block detection, the breaker and the ladder."""

from __future__ import annotations

from docmirror.fetch.politeness import HostLimiter, backoff_delay, retry_after_seconds
from docmirror.fetch.session import FetchResult, HttpFetcher

__all__ = ["FetchResult", "HostLimiter", "HttpFetcher", "backoff_delay", "retry_after_seconds"]
