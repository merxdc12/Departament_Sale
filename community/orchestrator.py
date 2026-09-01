from dataclasses import dataclass

from marketing.experiment import ExperimentDecision

from .adaptive_strategy import AdaptiveContentDecision, build_adaptive_content_strategy
from .intelligence import RedditIntelligenceInput, build_reddit_opportunity
from .memory import CommunityMemory, remember
from .performance import CommunityPerformance, evaluate_community_performance
from .rules import analyze_rule_evidence


@dataclass(frozen=True)
class RedditCampaignDecision:
    community_name: str
    opportunity_score: int
    community_action: str
    content_format: str
    pain_angle: str
    objective: str
    link_allowed: bool
    disclosure_required: bool
    human_approval_required: bool
    memory_recommendation: str
    experiment_decision: ExperimentDecision | None = None
    memory_record: CommunityMemory | None = None


def plan_reddit_campaign(
    data: RedditIntelligenceInput,
    history: tuple[CommunityMemory, ...] = (),
) -> RedditCampaignDecision:
    """Run intelligence -> policy -> adaptive content planning without external actions."""
    opportunity = build_reddit_opportunity(data)
    policy = analyze_rule_evidence(data.rule_evidence)
    adaptive: AdaptiveContentDecision = build_adaptive_content_strategy(
        opportunity,
        policy,
        data.pain_result,
        history,
    )
    strategy = adaptive.strategy
    return RedditCampaignDecision(
        community_name=opportunity.community_name,
        opportunity_score=opportunity.score,
        community_action=opportunity.action,
        content_format=strategy.format,
        pain_angle=strategy.angle,
        objective=strategy.objective,
        link_allowed=strategy.link_allowed,
        disclosure_required=strategy.disclosure_required,
        human_approval_required=strategy.human_approval_required,
        memory_recommendation=adaptive.learning.recommendation,
    )


def close_reddit_campaign(
    plan: RedditCampaignDecision,
    performance: CommunityPerformance,
) -> RedditCampaignDecision:
    """Evaluate a completed/manual campaign observation and create its memory record."""
    if performance.community_name != plan.community_name:
        raise ValueError("performance must belong to the planned community")
    if performance.content_format != plan.content_format:
        raise ValueError("performance content format must match the planned format")
    if plan.content_format == "NO_CONTENT":
        raise ValueError("NO_CONTENT plans cannot be evaluated as published campaigns")

    decision = evaluate_community_performance(performance)
    memory = remember(performance, decision)
    return RedditCampaignDecision(
        community_name=plan.community_name,
        opportunity_score=plan.opportunity_score,
        community_action=plan.community_action,
        content_format=plan.content_format,
        pain_angle=plan.pain_angle,
        objective=plan.objective,
        link_allowed=plan.link_allowed,
        disclosure_required=plan.disclosure_required,
        human_approval_required=plan.human_approval_required,
        memory_recommendation=plan.memory_recommendation,
        experiment_decision=decision,
        memory_record=memory,
    )
