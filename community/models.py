from dataclasses import dataclass, field
from typing import Literal

CommunityAction = Literal["BLOCK", "RESEARCH", "CONTRIBUTE", "SOFT_MENTION", "DIRECT_PROMOTION"]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


@dataclass(frozen=True)
class CommunityPolicy:
    community_name: str
    rules_checked: bool = False
    self_promotion_allowed: bool = False
    links_allowed: bool = False
    commercial_disclosure_required: bool = True
    unsolicited_dm_allowed: bool = False
    automation_allowed: bool = False


@dataclass(frozen=True)
class CommunitySignals:
    audience_fit: int
    problem_fit: int
    conversation_activity: int
    purchase_intent: int
    reputation_fit: int


@dataclass(frozen=True)
class CommunityOpportunity:
    platform: str
    community_name: str
    score: int
    action: CommunityAction
    risk_level: RiskLevel
    link_allowed: bool
    human_approval_required: bool = True
    reasons: tuple[str, ...] = field(default_factory=tuple)
