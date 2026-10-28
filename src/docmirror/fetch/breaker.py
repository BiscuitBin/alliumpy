"""The per-host circuit breaker over a rolling window of fetch outcomes."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

TIERS = ("http", "browser", "stealth")


@dataclass
class HostBreaker:
    """Rolling block rate for one host, with escalation and tripping.

    If more than `threshold` of the last `window` outcomes are blocks: pause the host,
    halve its rate and escalate its default tier by one. If the rate is still above the
    threshold after the next `window` outcomes at the highest available tier, trip.
    """

    window: int = 50
    threshold: float = 0.20
    highest_tier: str = "browser"
    outcomes: deque[bool] = field(default_factory=deque)
    tier_index: int = 0
    tripped: bool = False
    escalations: int = 0
    # The block rate that caused the last escalation, kept because escalating clears the window.
    trigger_rate: float = 0.0
    _since_escalation: int = 0

    @property
    def tier(self) -> str:
        """The host's current default tier."""
        return TIERS[self.tier_index]

    @property
    def block_rate(self) -> float:
        """Share of blocks in the window."""
        return (sum(self.outcomes) / len(self.outcomes)) if self.outcomes else 0.0

    def record(self, *, blocked: bool) -> str:
        """Record one outcome; return `ok`, `escalate` or `trip`."""
        if self.tripped:
            return "trip"
        self.outcomes.append(blocked)
        while len(self.outcomes) > self.window:
            self.outcomes.popleft()
        self._since_escalation += 1
        if len(self.outcomes) < min(self.window, 10) or self.block_rate <= self.threshold:
            return "ok"
        highest = TIERS.index(self.highest_tier)
        if self.tier_index < highest:
            self.tier_index += 1
            self.escalations += 1
            self._since_escalation = 0
            self.trigger_rate = self.block_rate
            self.outcomes.clear()
            return "escalate"
        if self._since_escalation >= self.window or self.escalations == 0:
            self.tripped = True
            return "trip"
        return "ok"
