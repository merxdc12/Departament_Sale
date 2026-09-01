from dataclasses import dataclass

from .memory import SocialLearning


@dataclass(frozen=True)
class ChannelPortfolioRow:
    channel: str
    experiments: int
    visits: int
    orders: int
    profit: float
    conversion_rate: float
    confidence: float
    risk: int
    priority_score: float
    recommendation: str


def build_channel_portfolio(learnings: tuple[SocialLearning, ...], *, risks: dict[str, int] | None = None) -> tuple[ChannelPortfolioRow, ...]:
    risks = risks or {}
    rows = []
    for item in learnings:
        risk = risks.get(item.platform, 20)
        if not 0 <= risk <= 100:
            raise ValueError("risk must be between 0 and 100")
        confidence = min(1.0, item.experiments / 5)
        normalized_profit = max(-100.0, min(100.0, item.profit))
        priority = round(
            normalized_profit * 0.45
            + item.conversion_rate * 100 * 0.25
            + confidence * 100 * 0.20
            + (100 - risk) * 0.10,
            2,
        )
        rows.append(ChannelPortfolioRow(item.platform, item.experiments, item.visits, item.orders, item.profit, item.conversion_rate, confidence, risk, priority, item.recommendation))
    return tuple(sorted(rows, key=lambda x: (x.priority_score, x.profit, x.conversion_rate), reverse=True))
