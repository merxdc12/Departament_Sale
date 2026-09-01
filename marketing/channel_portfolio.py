from dataclasses import dataclass
from typing import Literal

ChannelClass = Literal["SEARCH", "SOCIAL", "COMMUNITY", "OWNED", "SALES"]
ChannelDecision = Literal["AVOID", "RESEARCH", "RETEST", "PREFER", "SCALE"]


@dataclass(frozen=True)
class MarketingChannelKPI:
    channel: str
    channel_class: ChannelClass
    experiments: int = 0
    visits: int = 0
    orders: int = 0
    revenue: float = 0.0
    profit: float = 0.0
    confidence: float = 0.0
    risk: int = 20

    def __post_init__(self) -> None:
        if self.experiments < 0 or self.visits < 0 or self.orders < 0:
            raise ValueError("experiments, visits and orders cannot be negative")
        if self.orders > self.visits:
            raise ValueError("orders cannot exceed visits")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        if not 0 <= self.risk <= 100:
            raise ValueError("risk must be between 0 and 100")

    @property
    def conversion_rate(self) -> float:
        return self.orders / self.visits if self.visits else 0.0


@dataclass(frozen=True)
class MarketingChannelRow:
    channel: str
    channel_class: ChannelClass
    experiments: int
    visits: int
    orders: int
    conversion_rate: float
    revenue: float
    profit: float
    confidence: float
    risk: int
    priority_score: float
    decision: ChannelDecision


def _decision(priority: float, profit: float, confidence: float) -> ChannelDecision:
    if profit < 0 and confidence >= 0.4:
        return "AVOID"
    if confidence < 0.4:
        return "RESEARCH"
    if priority >= 70 and profit > 0:
        return "SCALE"
    if priority >= 50 and profit > 0:
        return "PREFER"
    return "RETEST"


def build_marketing_channel_portfolio(items: tuple[MarketingChannelKPI, ...]) -> tuple[MarketingChannelRow, ...]:
    rows = []
    for item in items:
        normalized_profit = max(-100.0, min(100.0, item.profit))
        priority = round(
            normalized_profit * 0.45
            + item.conversion_rate * 100 * 0.25
            + item.confidence * 100 * 0.20
            + (100 - item.risk) * 0.10,
            2,
        )
        rows.append(MarketingChannelRow(
            channel=item.channel,
            channel_class=item.channel_class,
            experiments=item.experiments,
            visits=item.visits,
            orders=item.orders,
            conversion_rate=item.conversion_rate,
            revenue=item.revenue,
            profit=item.profit,
            confidence=item.confidence,
            risk=item.risk,
            priority_score=priority,
            decision=_decision(priority, item.profit, item.confidence),
        ))
    return tuple(sorted(rows, key=lambda x: (x.priority_score, x.profit, x.conversion_rate), reverse=True))


BASE_CHANNELS: tuple[tuple[str, ChannelClass], ...] = (
    ("GOOGLE_SEO", "SEARCH"),
    ("PINTEREST", "SOCIAL"),
    ("INSTAGRAM", "SOCIAL"),
    ("FACEBOOK", "SOCIAL"),
    ("THREADS", "SOCIAL"),
    ("TIKTOK", "SOCIAL"),
    ("YOUTUBE", "SOCIAL"),
    ("X", "SOCIAL"),
    ("REDDIT", "COMMUNITY"),
    ("EMAIL", "OWNED"),
    ("OWN_WEBSITE", "OWNED"),
)
