"""Shared business objects used across all departments.

These contracts are intentionally small and side-effect free. Departments exchange
these objects instead of reaching into each other's internal state.
"""

from dataclasses import dataclass, field
from typing import Literal

BusinessLine = Literal["POD", "KDP", "DIGITAL", "DROPSHIPPING", "DIY_IOT", "OTHER"]
Decision = Literal["DISCOVERED", "RESEARCH", "TEST", "APPROVE", "REJECT", "HOLD"]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


@dataclass(frozen=True)
class OpportunitySignals:
    demand_score: int
    competition_score: int
    buyer_intent_score: int
    trend_score: int
    evidence_sources: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for name in ("demand_score", "competition_score", "buyer_intent_score", "trend_score"):
            value = getattr(self, name)
            if not 0 <= value <= 100:
                raise ValueError(f"{name} must be between 0 and 100. Received: {value}")


@dataclass(frozen=True)
class BusinessOpportunity:
    opportunity_id: str
    problem: str
    market: str
    signals: OpportunitySignals
    possible_business_lines: tuple[BusinessLine, ...] = field(default_factory=tuple)
    score: int = 0
    confidence: float = 0.0
    status: Decision = "DISCOVERED"


@dataclass(frozen=True)
class ProductProfile:
    product_id: str
    opportunity_id: str
    name: str
    business_line: BusinessLine
    market: str
    selling_price: float = 0.0


@dataclass(frozen=True)
class Lead:
    lead_id: str
    source: str
    market: str
    problem: str = ""
    product_id: str | None = None
    score: int = 0


@dataclass(frozen=True)
class Customer:
    customer_id: str
    market: str
    source: str = ""


@dataclass(frozen=True)
class FinanceRecord:
    record_id: str
    product_id: str
    revenue: float = 0.0
    cost: float = 0.0
    currency: str = "PLN"

    @property
    def profit(self) -> float:
        return round(self.revenue - self.cost, 2)


@dataclass(frozen=True)
class RiskAssessment:
    subject_id: str
    level: RiskLevel
    blocked: bool = False
    reasons: tuple[str, ...] = field(default_factory=tuple)
