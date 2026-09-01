from dataclasses import dataclass
from typing import Literal

SocialPlatform = Literal["PINTEREST", "THREADS", "INSTAGRAM", "FACEBOOK", "TIKTOK", "X", "YOUTUBE"]
SocialAction = Literal["BLOCK", "RESEARCH", "ORGANIC_CONTENT", "COMMERCIAL_CONTENT"]


@dataclass(frozen=True)
class SocialPolicy:
    platform: SocialPlatform
    commercial_content_allowed: bool
    affiliate_links_allowed: bool = False
    disclosure_required: bool = True
    official_api_only: bool = True
    automation_allowed: bool = False
    human_approval_required: bool = True


@dataclass(frozen=True)
class SocialSignals:
    audience_fit: int
    content_fit: int
    purchase_intent: int
    engagement_fit: int


@dataclass(frozen=True)
class SocialPlan:
    platform: SocialPlatform
    action: SocialAction
    score: int
    content_format: str
    link_allowed: bool
    disclosure_required: bool
    human_approval_required: bool
    objective: str
    reasons: tuple[str, ...]
