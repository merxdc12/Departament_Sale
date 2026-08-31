from .models import CommunityOpportunity, CommunityPolicy, CommunitySignals


def _validate(signals: CommunitySignals) -> None:
    for name, value in (
        ("audience_fit", signals.audience_fit),
        ("problem_fit", signals.problem_fit),
        ("conversation_activity", signals.conversation_activity),
        ("purchase_intent", signals.purchase_intent),
        ("reputation_fit", signals.reputation_fit),
    ):
        if not 0 <= value <= 100:
            raise ValueError(f"{name} must be between 0 and 100. Received: {value}")


def analyze_reddit_opportunity(
    policy: CommunityPolicy,
    signals: CommunitySignals,
) -> CommunityOpportunity:
    """Decide how to participate without disguising advertising or bypassing rules.

    This layer never posts, votes, sends DMs, creates accounts, or bypasses platform
    controls. It prepares a rule-aware recommendation for human approval.
    """
    _validate(signals)

    if not policy.rules_checked:
        return CommunityOpportunity(
            platform="REDDIT",
            community_name=policy.community_name,
            score=0,
            action="RESEARCH",
            risk_level="HIGH",
            link_allowed=False,
            reasons=("Community rules must be checked before participation.",),
        )

    score = round(
        signals.audience_fit * 0.30
        + signals.problem_fit * 0.25
        + signals.conversation_activity * 0.15
        + signals.purchase_intent * 0.15
        + signals.reputation_fit * 0.15
    )

    if score < 45:
        return CommunityOpportunity(
            platform="REDDIT",
            community_name=policy.community_name,
            score=score,
            action="BLOCK",
            risk_level="MEDIUM",
            link_allowed=False,
            reasons=("Community fit is too weak; avoid promotional participation.",),
        )

    if not policy.self_promotion_allowed:
        return CommunityOpportunity(
            platform="REDDIT",
            community_name=policy.community_name,
            score=score,
            action="CONTRIBUTE",
            risk_level="LOW",
            link_allowed=False,
            reasons=(
                "Self-promotion is not allowed; contribute useful non-promotional content only.",
                "Do not use disguised endorsements, unsolicited DMs, or artificial engagement.",
            ),
        )

    if policy.links_allowed and score >= 75:
        return CommunityOpportunity(
            platform="REDDIT",
            community_name=policy.community_name,
            score=score,
            action="DIRECT_PROMOTION",
            risk_level="MEDIUM",
            link_allowed=True,
            reasons=(
                "Strong community fit and rules allow self-promotion and links.",
                "Commercial relationship must be disclosed when relevant.",
                "Human approval is required before publishing.",
            ),
        )

    return CommunityOpportunity(
        platform="REDDIT",
        community_name=policy.community_name,
        score=score,
        action="SOFT_MENTION",
        risk_level="LOW",
        link_allowed=False,
        reasons=(
            "Participate with useful content; mention the product only when directly relevant.",
            "Do not disguise marketing as an independent recommendation.",
        ),
    )
