"""General opportunity discovery built on the proven SEO scoring model."""

from business_core.models import BusinessOpportunity, OpportunitySignals
from seo.scoring import opportunity_score


def discover_opportunity(
    *,
    opportunity_id: str,
    problem: str,
    market: str,
    signals: OpportunitySignals,
    possible_business_lines: tuple[str, ...],
) -> BusinessOpportunity:
    if not problem.strip():
        raise ValueError("problem is required")
    if not market.strip():
        raise ValueError("market is required")
    if not possible_business_lines:
        raise ValueError("at least one possible business line is required")

    score = opportunity_score(
        signals.demand_score,
        signals.competition_score,
        signals.buyer_intent_score,
        signals.trend_score,
    )
    evidence_count = len(set(signals.evidence_sources))
    confidence = round(min(1.0, evidence_count / 5), 2)
    return BusinessOpportunity(
        opportunity_id=opportunity_id,
        problem=problem.strip(),
        market=market.strip(),
        signals=signals,
        possible_business_lines=possible_business_lines,
        score=score,
        confidence=confidence,
    )
