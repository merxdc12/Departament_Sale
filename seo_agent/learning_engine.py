from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class SEOObservation:
    keyword: str
    cluster: str
    impressions: int = 0
    clicks: int = 0
    visits: int = 0
    orders: int = 0
    revenue: float = 0.0
    profit: float = 0.0

    @property
    def ctr(self) -> float:
        return self.clicks / self.impressions if self.impressions else 0.0

    @property
    def conversion(self) -> float:
        return self.orders / self.visits if self.visits else 0.0


@dataclass(frozen=True)
class LearningSignal:
    keyword: str
    cluster: str
    visibility_score: float
    attraction_score: float
    conversion_score: float
    profit_score: float
    evidence_score: float
    commercial_score: float


class SEOLearningEngine:
    """Conservative KPI feedback engine.

    It does not infer marketplace demand from missing data and does not mark
    low-sample observations as winners. Scores are feedback signals for the
    next SEO candidate-ranking cycle, not guarantees of future sales.
    """

    def __init__(self, min_impressions: int = 100) -> None:
        self.min_impressions = min_impressions

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))

    def evaluate(self, observation: SEOObservation) -> LearningSignal:
        evidence = self._clamp(observation.impressions / self.min_impressions)
        visibility = self._clamp(observation.impressions / max(self.min_impressions, 1))
        attraction = self._clamp(observation.ctr / 0.05)  # calibration target, configurable later
        conversion = self._clamp(observation.conversion / 0.03)
        profit = self._clamp(observation.profit / 10.0) if observation.profit > 0 else 0.0

        # Profit and conversion deliberately dominate raw visibility.
        commercial = evidence * (
            0.10 * visibility
            + 0.20 * attraction
            + 0.30 * conversion
            + 0.40 * profit
        )
        return LearningSignal(
            keyword=observation.keyword,
            cluster=observation.cluster,
            visibility_score=visibility,
            attraction_score=attraction,
            conversion_score=conversion,
            profit_score=profit,
            evidence_score=evidence,
            commercial_score=commercial,
        )

    def rank(self, observations: Iterable[SEOObservation]) -> list[LearningSignal]:
        signals = [self.evaluate(item) for item in observations]
        return sorted(signals, key=lambda item: item.commercial_score, reverse=True)
