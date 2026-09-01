from dataclasses import dataclass
from typing import Literal

from .models import CommunityOpportunity, CommunityPolicy
from .pain import PainMiningResult

ContentFormat = Literal[
    "NO_CONTENT",
    "ANSWER",
    "TUTORIAL",
    "DISCUSSION",
    "FEEDBACK_REQUEST",
    "SOFT_MENTION",
    "PROMO_POST",
]
MentionLevel = Literal["NONE", "CONTEXTUAL", "DIRECT"]
CTAType = Literal["NONE", "DISCUSS", "ASK_FEEDBACK", "LEARN_MORE", "VISIT_LINK"]


@dataclass(frozen=True)
class ContentStrategy:
    format: ContentFormat
    mention_level: MentionLevel
    cta: CTAType
    link_allowed: bool
    disclosure_required: bool
    human_approval_required: bool
    objective: str
    angle: str
    reasons: tuple[str, ...]


def _top_pain(pain_result: PainMiningResult) -> str:
    if pain_result.pains:
        return pain_result.pains[0].phrase
    if pain_result.question_mentions:
        return "answer a recurring audience question"
    return "provide useful context relevant to the community"


def build_content_strategy(
    opportunity: CommunityOpportunity,
    policy: CommunityPolicy,
    pain_result: PainMiningResult,
) -> ContentStrategy:
    """Map a safe community opportunity into a human-approved content format.

    This function creates strategy only. It never publishes, messages users, votes,
    creates accounts, or attempts to disguise commercial intent.
    """
    if opportunity.community_name != policy.community_name:
        raise ValueError("opportunity and policy must belong to the same community")

    angle = _top_pain(pain_result)

    if opportunity.action in ("BLOCK", "RESEARCH"):
        return ContentStrategy(
            format="NO_CONTENT",
            mention_level="NONE",
            cta="NONE",
            link_allowed=False,
            disclosure_required=False,
            human_approval_required=True,
            objective="Do not publish promotional content yet.",
            angle=angle,
            reasons=("Community eligibility is not sufficient for content publication.",),
        )

    if opportunity.action == "CONTRIBUTE":
        fmt: ContentFormat = "ANSWER" if pain_result.question_mentions else "TUTORIAL"
        return ContentStrategy(
            format=fmt,
            mention_level="NONE",
            cta="DISCUSS",
            link_allowed=False,
            disclosure_required=False,
            human_approval_required=True,
            objective="Build trust by solving a real community problem without promotion.",
            angle=angle,
            reasons=(
                "Self-promotion is not allowed.",
                "No product mention, external CTA, or disguised endorsement is permitted.",
            ),
        )

    if opportunity.action == "SOFT_MENTION":
        fmt = "FEEDBACK_REQUEST" if pain_result.question_mentions else "DISCUSSION"
        return ContentStrategy(
            format=fmt,
            mention_level="CONTEXTUAL",
            cta="ASK_FEEDBACK" if fmt == "FEEDBACK_REQUEST" else "DISCUSS",
            link_allowed=False,
            disclosure_required=policy.commercial_disclosure_required,
            human_approval_required=True,
            objective="Join the discussion with useful context and only a relevant product mention.",
            angle=angle,
            reasons=(
                "A product mention may be contextual, but it must not masquerade as an independent recommendation.",
                "No external link is included unless the community rules explicitly allow it.",
            ),
        )

    if opportunity.action == "DIRECT_PROMOTION":
        if not policy.self_promotion_allowed or not policy.links_allowed or not opportunity.link_allowed:
            raise ValueError("direct promotion requires explicit self-promotion and link permission")
        return ContentStrategy(
            format="PROMO_POST",
            mention_level="DIRECT",
            cta="VISIT_LINK",
            link_allowed=True,
            disclosure_required=True,
            human_approval_required=True,
            objective="Run a transparent, rule-compliant promotional test.",
            angle=angle,
            reasons=(
                "Rules explicitly allow self-promotion and links.",
                "Commercial relationship must be disclosed clearly.",
                "Human approval remains mandatory before publishing.",
            ),
        )

    raise ValueError(f"Unsupported community action: {opportunity.action}")
