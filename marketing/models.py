from dataclasses import dataclass, field
from typing import Literal

from seo.decision import SEODecision

MarketingAction = Literal["BLOCK", "RESEARCH", "TEST"]
ChannelName = Literal["SEO", "PINTEREST", "INSTAGRAM", "ETSY_ADS", "ORGANIC_SOCIAL"]


@dataclass(frozen=True)
class ProductEconomics:
    sale_price: float
    production_cost: float
    platform_fees: float = 0.0
    shipping_cost: float = 0.0
    other_variable_cost: float = 0.0

    @property
    def contribution_margin(self) -> float:
        return round(
            self.sale_price
            - self.production_cost
            - self.platform_fees
            - self.shipping_cost
            - self.other_variable_cost,
            2,
        )

    @property
    def margin_rate(self) -> float:
        if self.sale_price <= 0:
            return 0.0
        return round(self.contribution_margin / self.sale_price, 4)


@dataclass(frozen=True)
class MarketingInput:
    seo: SEODecision
    economics: ProductEconomics
    target_segment: str
    positioning: str
    market: str
    language: str
    available_test_budget: float = 0.0
    preferred_channels: tuple[ChannelName, ...] = ("SEO",)


@dataclass(frozen=True)
class TestGuardrails:
    duration_days: int
    max_budget: float
    target_visits: int
    stop_conversion_below: float
    scale_conversion_at_or_above: float
    require_manual_approval: bool = True


@dataclass(frozen=True)
class MarketingPlan:
    product_id: str
    platform: str
    action: MarketingAction
    target_segment: str
    positioning: str
    market: str
    language: str
    contribution_margin: float
    margin_rate: float
    channels: tuple[ChannelName, ...] = field(default_factory=tuple)
    guardrails: TestGuardrails | None = None
    reasons: tuple[str, ...] = field(default_factory=tuple)
