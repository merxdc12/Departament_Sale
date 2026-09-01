from dataclasses import dataclass
from typing import Literal

from business_core.models import BusinessOpportunity, RiskAssessment
from .competitor import CompetitorAnalysis

ValidationDecision = Literal["GO", "TEST", "HOLD", "REJECT"]


@dataclass(frozen=True)
class ProductValidation:
    opportunity_id: str
    decision: ValidationDecision
    score: int
    confidence: float
    reason: str


def validate_product(
    opportunity: BusinessOpportunity,
    competitors: CompetitorAnalysis,
    risk: RiskAssessment,
) -> ProductValidation:
    if risk.blocked:
        return ProductValidation(opportunity.opportunity_id, "REJECT", 0, opportunity.confidence, "Risk gate blocks this product opportunity.")

    confidence = round(min(opportunity.confidence, competitors.evidence_confidence or opportunity.confidence), 2)
    score = max(0, opportunity.score - risk.penalty)
    if confidence < 0.4:
        decision: ValidationDecision = "HOLD"
        reason = "Evidence is insufficient; collect more market and competitor data."
    elif score >= 80:
        decision = "GO"
        reason = "Strong validated opportunity; prepare a controlled product test."
    elif score >= 60:
        decision = "TEST"
        reason = "Opportunity supports a small controlled test."
    elif score >= 45:
        decision = "HOLD"
        reason = "Opportunity needs stronger evidence or differentiation."
    else:
        decision = "REJECT"
        reason = "Risk-adjusted opportunity is too weak."
    return ProductValidation(opportunity.opportunity_id, decision, score, confidence, reason)
