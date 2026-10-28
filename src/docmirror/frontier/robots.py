"""robots.txt: `Disallow`, `Crawl-delay` and `Sitemap:` through protego."""

from __future__ import annotations

from dataclasses import dataclass, field

from protego import Protego


@dataclass
class Robots:
    """One host's robots.txt, parsed; an absent file allows everything."""

    agent: str
    parser: Protego | None = None
    respect: bool = True
    sitemaps: list[str] = field(default_factory=list)

    @classmethod
    def parse(cls, text: str, agent: str, *, respect: bool = True) -> Robots:
        """Parse a robots.txt body."""
        parser = Protego.parse(text)
        return cls(agent=agent, parser=parser, respect=respect, sitemaps=list(parser.sitemaps))

    @classmethod
    def absent(cls, agent: str, *, respect: bool = True) -> Robots:
        """The robots for a host with no robots.txt."""
        return cls(agent=agent, parser=None, respect=respect)

    def allows(self, url: str) -> bool:
        """Whether the agent may fetch `url` (always true when not respecting)."""
        if not self.respect or self.parser is None:
            return True
        return bool(self.parser.can_fetch(url, self.agent))

    def crawl_delay(self) -> float | None:
        """The `Crawl-delay` for the agent, if any and if respected."""
        if not self.respect or self.parser is None:
            return None
        delay = self.parser.crawl_delay(self.agent)
        return None if delay is None else float(delay)
