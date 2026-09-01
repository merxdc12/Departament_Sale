"""Shared contracts for Phoenix Online Business OS departments."""

from .event_bus import EventBus
from .events import BusinessEvent
from .integrations import (
    publish_community_plan,
    publish_kpi_dashboard,
    publish_learning_recommendation,
    publish_listing_performance,
    publish_marketing_plan,
    publish_seo_decision,
    publish_social_plan,
)
from .models import (
    BusinessOpportunity,
    Customer,
    FinanceRecord,
    Lead,
    OpportunitySignals,
    ProductProfile,
    RiskAssessment,
)

__all__ = [
    "BusinessEvent",
    "BusinessOpportunity",
    "Customer",
    "EventBus",
    "FinanceRecord",
    "Lead",
    "OpportunitySignals",
    "ProductProfile",
    "RiskAssessment",
    "publish_community_plan",
    "publish_kpi_dashboard",
    "publish_learning_recommendation",
    "publish_listing_performance",
    "publish_marketing_plan",
    "publish_seo_decision",
    "publish_social_plan",
]
