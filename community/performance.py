from dataclasses import dataclass

from marketing.experiment import ExperimentDecision, ExperimentResult, evaluate_experiment

from .content_strategy import ContentStrategy


@dataclass(frozen=True)
class CommunityPerformance:
    community_name: str
    content_format: str
    pain_angle: str
    impressions: int = 0
    clicks: int = 0
    visits: int = 0
    orders: int = 0
    revenue: float = 0.0
    total_cost: float = 0.0

    def __post_init__(self) -> None:
        for name in ("impressions", "clicks", "visits", "orders"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} cannot be negative")
        if self.revenue < 0 or self.total_cost < 0:
            raise ValueError("revenue and total_cost cannot be negative")
        if self.clicks > self.impressions and self.impressions:
            raise ValueError("clicks cannot exceed impressions")
        if self.orders > self.visits:
            raise ValueError("orders cannot exceed visits")

    @property
    def conversion_rate(self) -> float:
        return self.orders / self.visits if self.visits else 0.0

    @property
    def profit(self) -> float:
        return self.revenue - self.total_cost


def evaluate_community_performance(
    performance: CommunityPerformance,
    *,
    min_visits: int = 100,
) -> ExperimentDecision:
    return evaluate_experiment(
        ExperimentResult(
            impressions=performance.impressions,
            clicks=performance.clicks,
            visits=performance.visits,
            orders=performance.orders,
            revenue=performance.revenue,
            total_cost=performance.total_cost,
        ),
        min_visits=min_visits,
    )


def performance_from_strategy(
    community_name: str,
    strategy: ContentStrategy,
    **metrics,
) -> CommunityPerformance:
    return CommunityPerformance(
        community_name=community_name,
        content_format=strategy.format,
        pain_angle=strategy.angle,
        **metrics,
    )
