from dataclasses import dataclass

from .discovery import RankedCommunity
from .models import CommunityOpportunity, CommunitySignals
from .pain import PainMiningResult
from .reddit import analyze_reddit_opportunity
from .rules import RuleEvidence, analyze_rule_evidence


@dataclass(frozen=True)
class RedditIntelligenceInput:
    ranked_community: RankedCommunity
    rule_evidence: RuleEvidence
    pain_result: PainMiningResult
    problem_fit: int
    reputation_fit: int


def _clamp_score(value: int) -> int:
    if not 0 <= value <= 100:
        raise ValueError(f"score must be between 0 and 100. Received: {value}")
    return value


def build_reddit_opportunity(data: RedditIntelligenceInput) -> CommunityOpportunity:
    """Convert discovery, rule evidence and discussion evidence into one safe decision."""
    problem_fit = _clamp_score(data.problem_fit)
    reputation_fit = _clamp_score(data.reputation_fit)

    policy = analyze_rule_evidence(data.rule_evidence)
    if policy.community_name != data.ranked_community.name:
        raise ValueError("rule evidence must belong to the ranked community")

    audience_fit = data.ranked_community.relevance_score
    conversation_activity = data.ranked_community.activity_score
    if data.pain_result.sample_count <= 0:
        purchase_intent = 0
    else:
        purchase_intent = min(
            100,
            round(data.pain_result.intent_mentions / data.pain_result.sample_count * 25),
        )

    signals = CommunitySignals(
        audience_fit=audience_fit,
        problem_fit=problem_fit,
        conversation_activity=conversation_activity,
        purchase_intent=purchase_intent,
        reputation_fit=reputation_fit,
    )
    return analyze_reddit_opportunity(policy, signals)
