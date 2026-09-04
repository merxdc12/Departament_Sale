from dataclasses import dataclass
from typing import Literal

NicheType = Literal["TRENDING", "EVERGREEN", "SEASONAL", "HYBRID"]


@dataclass(frozen=True)
class NicheSignals:
    trend_score: int
    stable_demand_score: int
    seasonality_score: int = 0


def classify_niche(signals: NicheSignals) -> NicheType:
    for name, value in (
        ("trend_score", signals.trend_score),
        ("stable_demand_score", signals.stable_demand_score),
        ("seasonality_score", signals.seasonality_score),
    ):
        if not 0 <= value <= 100:
            raise ValueError(f"{name} must be between 0 and 100. Received: {value}")

    if signals.stable_demand_score >= 65 and signals.trend_score >= 65:
        return "HYBRID"
    if signals.seasonality_score >= 70:
        return "SEASONAL"
    if signals.trend_score >= 70 and signals.stable_demand_score < 65:
        return "TRENDING"
    return "EVERGREEN"
