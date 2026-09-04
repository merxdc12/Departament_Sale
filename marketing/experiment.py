from dataclasses import dataclass
from typing import Literal

ExperimentDecision = Literal["COLLECT_DATA", "STOP", "MODIFY", "SCALE"]


@dataclass(frozen=True)
class ExperimentResult:
    impressions: int = 0
    clicks: int = 0
    visits: int = 0
    orders: int = 0
    revenue: float = 0.0
    total_cost: float = 0.0

    @property
    def ctr(self) -> float:
        return self.clicks / self.impressions if self.impressions else 0.0

    @property
    def conversion_rate(self) -> float:
        return self.orders / self.visits if self.visits else 0.0

    @property
    def profit(self) -> float:
        return self.revenue - self.total_cost


def evaluate_experiment(
    result: ExperimentResult,
    *,
    min_visits: int = 100,
    scale_conversion: float = 0.03,
    stop_conversion: float = 0.01,
) -> ExperimentDecision:
    if min_visits <= 0:
        raise ValueError("min_visits must be positive")
    if not 0 <= stop_conversion < scale_conversion <= 1:
        raise ValueError("conversion thresholds are invalid")
    if result.visits < min_visits:
        return "COLLECT_DATA"
    if result.conversion_rate >= scale_conversion and result.profit > 0:
        return "SCALE"
    if result.conversion_rate < stop_conversion or result.profit < 0:
        return "STOP"
    return "MODIFY"
