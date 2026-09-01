from dataclasses import dataclass
from typing import Literal

from marketing.experiment import ExperimentDecision

from .performance import CommunityPerformance

MemoryRecommendation = Literal["INSUFFICIENT_DATA", "AVOID", "RETEST", "PREFER"]


@dataclass(frozen=True)
class CommunityMemory:
    community_name: str
    content_format: str
    pain_angle: str
    visits: int
    orders: int
    revenue: float
    profit: float
    outcome: ExperimentDecision


@dataclass(frozen=True)
class CommunityLearning:
    community_name: str
    content_format: str
    experiments: int
    visits: int
    orders: int
    profit: float
    conversion_rate: float
    recommendation: MemoryRecommendation


def remember(performance: CommunityPerformance, outcome: ExperimentDecision) -> CommunityMemory:
    return CommunityMemory(
        community_name=performance.community_name,
        content_format=performance.content_format,
        pain_angle=performance.pain_angle,
        visits=performance.visits,
        orders=performance.orders,
        revenue=performance.revenue,
        profit=performance.profit,
        outcome=outcome,
    )


def learn_community_history(
    history: tuple[CommunityMemory, ...],
    *,
    community_name: str,
    content_format: str,
    min_experiments: int = 2,
) -> CommunityLearning:
    if min_experiments <= 0:
        raise ValueError("min_experiments must be positive")
    relevant = tuple(
        x for x in history
        if x.community_name == community_name and x.content_format == content_format
    )
    visits = sum(x.visits for x in relevant)
    orders = sum(x.orders for x in relevant)
    profit = sum(x.profit for x in relevant)
    conversion = orders / visits if visits else 0.0

    if len(relevant) < min_experiments:
        recommendation: MemoryRecommendation = "INSUFFICIENT_DATA"
    elif profit < 0:
        recommendation = "AVOID"
    elif profit > 0 and conversion >= 0.03:
        recommendation = "PREFER"
    else:
        recommendation = "RETEST"

    return CommunityLearning(
        community_name=community_name,
        content_format=content_format,
        experiments=len(relevant),
        visits=visits,
        orders=orders,
        profit=profit,
        conversion_rate=conversion,
        recommendation=recommendation,
    )
