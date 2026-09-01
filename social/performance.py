from dataclasses import dataclass

from marketing.experiment import ExperimentDecision, ExperimentResult, evaluate_experiment

from .models import SocialPlan, SocialPlatform


@dataclass(frozen=True)
class SocialPerformance:
    platform: SocialPlatform
    content_format: str
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
    def profit(self) -> float:
        return self.revenue - self.total_cost

    @property
    def conversion_rate(self) -> float:
        return self.orders / self.visits if self.visits else 0.0


def evaluate_social_performance(performance: SocialPerformance, *, min_visits: int = 100) -> ExperimentDecision:
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


def performance_from_plan(plan: SocialPlan, **metrics) -> SocialPerformance:
    if plan.content_format in ("NO_CONTENT", "RESEARCH"):
        raise ValueError("non-publishing plans cannot produce campaign performance")
    return SocialPerformance(platform=plan.platform, content_format=plan.content_format, **metrics)
