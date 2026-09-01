from dataclasses import dataclass
from typing import Literal

from marketing.experiment import ExperimentDecision

from .models import SocialPlatform
from .performance import SocialPerformance

SocialRecommendation = Literal["INSUFFICIENT_DATA", "AVOID", "RETEST", "PREFER"]


@dataclass(frozen=True)
class SocialMemory:
    platform: SocialPlatform
    content_format: str
    visits: int
    orders: int
    revenue: float
    profit: float
    outcome: ExperimentDecision


@dataclass(frozen=True)
class SocialLearning:
    platform: SocialPlatform
    content_format: str
    experiments: int
    visits: int
    orders: int
    profit: float
    conversion_rate: float
    recommendation: SocialRecommendation


def remember_social(performance: SocialPerformance, outcome: ExperimentDecision) -> SocialMemory:
    return SocialMemory(performance.platform, performance.content_format, performance.visits, performance.orders, performance.revenue, performance.profit, outcome)


def learn_social_history(history: tuple[SocialMemory, ...], *, platform: SocialPlatform, content_format: str, min_experiments: int = 2) -> SocialLearning:
    if min_experiments <= 0:
        raise ValueError("min_experiments must be positive")
    relevant = tuple(x for x in history if x.platform == platform and x.content_format == content_format)
    visits = sum(x.visits for x in relevant)
    orders = sum(x.orders for x in relevant)
    profit = sum(x.profit for x in relevant)
    conversion = orders / visits if visits else 0.0
    if len(relevant) < min_experiments:
        recommendation: SocialRecommendation = "INSUFFICIENT_DATA"
    elif profit < 0:
        recommendation = "AVOID"
    elif profit > 0 and conversion >= 0.03:
        recommendation = "PREFER"
    else:
        recommendation = "RETEST"
    return SocialLearning(platform, content_format, len(relevant), visits, orders, profit, conversion, recommendation)
