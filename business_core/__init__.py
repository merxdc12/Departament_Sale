"""Shared contracts for Phoenix Online Business OS departments."""

from .event_bus import EventBus
from .events import BusinessEvent
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
]
