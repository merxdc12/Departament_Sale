from dataclasses import dataclass

from .models import CommunityPolicy


@dataclass(frozen=True)
class RuleEvidence:
    community_name: str
    rule_texts: tuple[str, ...]
    source_verified: bool = False


def analyze_rule_evidence(evidence: RuleEvidence) -> CommunityPolicy:
    """Translate explicit community rules into a conservative participation policy.

    Unknown or ambiguous rules fail closed: self-promotion and links remain disabled.
    """
    if not evidence.community_name.strip():
        raise ValueError("community_name is required")

    texts = tuple(x.strip().lower() for x in evidence.rule_texts if x.strip())
    if not evidence.source_verified or not texts:
        return CommunityPolicy(community_name=evidence.community_name, rules_checked=False)

    combined = " ".join(texts)

    promotion_forbidden = any(
        phrase in combined
        for phrase in (
            "no self promotion",
            "no self-promotion",
            "self promotion is not allowed",
            "no advertising",
            "no promotion",
            "no promotional posts",
        )
    )
    promotion_allowed = any(
        phrase in combined
        for phrase in (
            "self promotion allowed",
            "self-promotion allowed",
            "promotion allowed",
            "promotional posts allowed",
        )
    ) and not promotion_forbidden

    links_forbidden = any(
        phrase in combined
        for phrase in ("no external links", "no links", "external links are not allowed")
    )
    links_allowed = any(
        phrase in combined
        for phrase in ("external links allowed", "links allowed", "link posts allowed")
    ) and not links_forbidden

    disclosure_required = any(
        phrase in combined
        for phrase in (
            "disclose affiliation",
            "disclose your affiliation",
            "commercial disclosure",
            "identify yourself as the creator",
        )
    )

    return CommunityPolicy(
        community_name=evidence.community_name,
        rules_checked=True,
        self_promotion_allowed=promotion_allowed,
        links_allowed=links_allowed,
        commercial_disclosure_required=disclosure_required or promotion_allowed,
        unsolicited_dm_allowed=False,
        automation_allowed=False,
    )
