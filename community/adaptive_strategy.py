from dataclasses import dataclass, replace

from .content_strategy import ContentStrategy, build_content_strategy
from .memory import CommunityLearning, CommunityMemory, learn_community_history
from .models import CommunityOpportunity, CommunityPolicy
from .pain import PainMiningResult


@dataclass(frozen=True)
class AdaptiveContentDecision:
    strategy: ContentStrategy
    learning: CommunityLearning
    memory_applied: bool
    reason: str


def build_adaptive_content_strategy(
    opportunity: CommunityOpportunity,
    policy: CommunityPolicy,
    pain_result: PainMiningResult,
    history: tuple[CommunityMemory, ...],
    *,
    min_experiments: int = 2,
) -> AdaptiveContentDecision:
    """Build a safe content strategy and adapt it using same-community history.

    Rules and the current opportunity always win over memory. Learning may reduce
    or prioritize an eligible strategy, but can never enable promotion, links, or
    automation that the current policy does not allow.
    """
    base = build_content_strategy(opportunity, policy, pain_result)
    learning = learn_community_history(
        history,
        community_name=opportunity.community_name,
        content_format=base.format,
        min_experiments=min_experiments,
    )

    if base.format == "NO_CONTENT":
        return AdaptiveContentDecision(base, learning, False, "Current rules/opportunity block content; memory cannot override safety.")

    if learning.recommendation == "AVOID":
        adapted = replace(
            base,
            format="NO_CONTENT",
            mention_level="NONE",
            cta="NONE",
            link_allowed=False,
            objective="Pause this content format because repeated tests were unprofitable.",
            reasons=base.reasons + ("Memory recommends AVOID for this community and content format.",),
        )
        return AdaptiveContentDecision(adapted, learning, True, "Repeated negative performance paused this format.")

    if learning.recommendation == "PREFER":
        adapted = replace(
            base,
            objective=base.objective + " Prioritize this proven format in the next controlled test.",
            reasons=base.reasons + ("Memory recommends PREFER based on repeated profitable experiments.",),
        )
        return AdaptiveContentDecision(adapted, learning, True, "Repeated profitable performance increases priority, without changing permissions.")

    if learning.recommendation == "RETEST":
        adapted = replace(
            base,
            objective=base.objective + " Run another controlled variation before scaling.",
            reasons=base.reasons + ("Memory recommends RETEST; evidence is mixed or not strong enough to prefer.",),
        )
        return AdaptiveContentDecision(adapted, learning, True, "History is inconclusive; test a controlled variation.")

    return AdaptiveContentDecision(base, learning, False, "Not enough history to adapt the base strategy.")
