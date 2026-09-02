from dataclasses import dataclass

from .confidence import calculate_confidence
from .models import Decision, SEOAnalysis, SEOInput
from .risk import evaluate_seo_risk
from .scoring import opportunity_score


@dataclass(frozen=True)
class SEODecision:
    product_id: str
    platform: str
    analysis: SEOAnalysis


def make_seo_decision(data: SEOInput) -> SEODecision:
    raw = opportunity_score(
        data.demand_score,
        data.competition_score,
        data.buyer_intent_score,
        data.trend_score,
    )
    risk = evaluate_seo_risk(
        trademark_risk=data.trademark_risk,
        copyright_risk=data.copyright_risk,
        policy_risk=data.policy_risk,
        prohibited_content=data.prohibited_content,
        misleading_claim_risk=data.misleading_claim_risk,
    )
    confidence = calculate_confidence(
        has_search_data=data.has_search_data,
        has_competitor_data=data.has_competitor_data,
        has_trend_data=data.has_trend_data,
        has_price_data=data.has_price_data,
        has_sales_data=data.has_sales_data,
    )

    adjusted = 0 if risk.blocked else max(0, raw - risk.penalty)
    if risk.blocked:
        decision: Decision = "REJECT"
        reason = "Critical business/IP risk blocks this opportunity."
    elif confidence.score < 0.60:
        decision = "REVIEW"
        reason = "Evidence confidence is too low; collect additional reliable data."
    elif adjusted >= 70:
        decision = "TEST"
        reason = "Risk-adjusted opportunity supports a controlled market test."
    elif adjusted >= 50:
        decision = "REVIEW"
        reason = "Opportunity requires additional analysis before testing."
    else:
        decision = "REJECT"
        reason = "Risk-adjusted opportunity is currently too weak."

    analysis = SEOAnalysis(
        raw_opportunity_score=raw,
        risk_penalty=risk.penalty,
        adjusted_score=adjusted,
        risk_level=risk.level,
        risk_reasons=risk.reasons,
        confidence=confidence.score,
        confidence_level=confidence.level,
        missing_sources=confidence.missing_sources,
        decision=decision,
        reason=reason,
    )
    return SEODecision(data.product_id, data.platform, analysis)
