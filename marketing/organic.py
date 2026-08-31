from dataclasses import dataclass
from typing import Literal

OrganicChannel = Literal[
    "MARKETPLACE_SEO",
    "GOOGLE_SEO",
    "PINTEREST_ORGANIC",
    "INSTAGRAM_ORGANIC",
    "CONTENT",
]


@dataclass(frozen=True)
class OrganicPlan:
    channels: tuple[OrganicChannel, ...]
    paid_ads_enabled: bool
    reason: str


def organic_first_plan(platform: str) -> OrganicPlan:
    platform_name = platform.strip().lower()
    channels: list[OrganicChannel] = ["MARKETPLACE_SEO", "GOOGLE_SEO"]
    if platform_name in {"etsy", "redbubble", "teepublic", "amazon"}:
        channels.append("PINTEREST_ORGANIC")
    channels.extend(("CONTENT", "INSTAGRAM_ORGANIC"))
    return OrganicPlan(
        channels=tuple(channels),
        paid_ads_enabled=False,
        reason="Organic-first: validate demand and conversion before paid acquisition.",
    )
