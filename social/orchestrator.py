from dataclasses import dataclass, replace

from marketing.experiment import ExperimentDecision

from .memory import SocialMemory, learn_social_history, remember_social
from .models import SocialPlan, SocialPolicy, SocialSignals
from .performance import SocialPerformance, evaluate_social_performance
from .strategy import build_social_plan


@dataclass(frozen=True)
class SocialCampaignDecision:
    plan: SocialPlan
    memory_recommendation: str
    experiment_decision: ExperimentDecision | None = None
    memory_record: SocialMemory | None = None


def plan_social_campaign(policy: SocialPolicy, signals: SocialSignals, history: tuple[SocialMemory, ...] = (), *, commercial: bool = False) -> SocialCampaignDecision:
    base = build_social_plan(policy, signals, commercial=commercial)
    learning = learn_social_history(history, platform=base.platform, content_format=base.content_format)
    plan = base
    if base.action in ("BLOCK", "RESEARCH"):
        return SocialCampaignDecision(base, learning.recommendation)
    if learning.recommendation == "AVOID":
        plan = replace(base, action="RESEARCH", content_format="RESEARCH", link_allowed=False, objective="Pause this format after repeated unprofitable tests and research a new variation.", reasons=base.reasons + ("Memory recommends AVOID.",))
    elif learning.recommendation == "PREFER":
        plan = replace(base, objective=base.objective + " Prioritize this proven profitable format.", reasons=base.reasons + ("Memory recommends PREFER.",))
    elif learning.recommendation == "RETEST":
        plan = replace(base, objective=base.objective + " Test another controlled variation before scaling.", reasons=base.reasons + ("Memory recommends RETEST.",))
    return SocialCampaignDecision(plan, learning.recommendation)


def close_social_campaign(decision: SocialCampaignDecision, performance: SocialPerformance) -> SocialCampaignDecision:
    plan = decision.plan
    if plan.action not in ("ORGANIC_CONTENT", "COMMERCIAL_CONTENT"):
        raise ValueError("only publishable campaign plans can be evaluated")
    if performance.platform != plan.platform or performance.content_format != plan.content_format:
        raise ValueError("performance must match the planned platform and content format")
    outcome = evaluate_social_performance(performance)
    memory = remember_social(performance, outcome)
    return SocialCampaignDecision(plan, decision.memory_recommendation, outcome, memory)
