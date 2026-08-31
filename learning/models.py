from dataclasses import dataclass, field
from typing import Literal

from marketing.niche import NicheType

Outcome = Literal["STOP", "MODIFY", "SCALE"]


@dataclass(frozen=True)
class ExperimentMemory:
    experiment_id: str
    product_id: str
    platform: str
    market: str
    niche_type: NicheType
    channel: str
    target_segment: str
    positioning: str
    keywords: tuple[str, ...] = field(default_factory=tuple)
    visits: int = 0
    orders: int = 0
    revenue: float = 0.0
    profit: float = 0.0
    outcome: Outcome = "MODIFY"
    notes: str = ""

    @property
    def conversion_rate(self) -> float:
        return self.orders / self.visits if self.visits else 0.0


@dataclass(frozen=True)
class LearnedPattern:
    niche_type: NicheType
    channel: str
    experiments: int
    total_visits: int
    total_orders: int
    total_profit: float
    conversion_rate: float
    average_profit_per_experiment: float
    score: float


@dataclass(frozen=True)
class LearningRecommendation:
    preferred_channels: tuple[str, ...]
    avoid_channels: tuple[str, ...]
    patterns: tuple[LearnedPattern, ...]
    reason: str
