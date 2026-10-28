"""NDJSON progress events on stdout when `--json` is set; nothing otherwise."""

from __future__ import annotations

import json
import sys
from typing import IO, Any


class EventEmitter:
    """Writes one JSON object per line to `stream` when enabled."""

    def __init__(self, *, enabled: bool, stream: IO[str] | None = None) -> None:
        """Create an emitter; `stream` defaults to stdout."""
        self.enabled = enabled
        self.stream = stream if stream is not None else sys.stdout

    def emit(self, event: str, **fields: Any) -> None:  # noqa: ANN401 - JSON values
        """Emit one event."""
        if not self.enabled:
            return
        payload = {"event": event, **fields}
        self.stream.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")
        self.stream.flush()
