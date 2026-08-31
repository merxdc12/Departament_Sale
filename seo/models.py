from dataclasses import dataclass, field
from typing import Literal

Decision = Literal["TEST", "REVIEW", "REJECT"]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
ConfidenceLevel = Literal["LOW", "MEDIUM", "HIGH"]


@dataclass(frozen=True)
class SEOInput:
    product_id: str
    platform: str
    market: str
    language: str
    demand_score: int
    competition_score: int
    buyer_intent_score: int
    trend_score: int
    has_search_data: bool = False
    has_competitor_data: bool = False
    has_trend_data: bool = False
    has_price_data: bool = False
    has_sales_data: bool = False
    trademark_risk: bool = False
    copyright_risk: bool = False
    policy_risk: bool = False
    prohibited_content: bool = False
    misleading_claim_risk: bool = False


@dataclass(frozen=True)
class SEOAnalysis:
    raw_opportunity_score: int
    risk_penalty: int
    adjusted_score: int
    risk_level: RiskLevel
    risk_reasons: tuple[str, ...] = field(default_factory=tuple)
    confidence: float = 0.0
    confidence_level: ConfidenceLevel = "LOW"
    missing_sources: tuple[str, ...] = field(default_factory=tuple)
    decision: Decision = "REVIEW"
    reason: str = ""
