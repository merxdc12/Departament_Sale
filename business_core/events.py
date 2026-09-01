"""Events that allow departments to cooperate without direct coupling."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

EventName = Literal[
    "OPPORTUNITY_FOUND",
    "COMPETITION_ANALYZED",
    "SEO_ANALYZED",
    "PRODUCT_VALIDATED",
    "ECONOMICS_APPROVED",
    "ECONOMICS_REJECTED",
    "RISK_DETECTED",
    "TEST_APPROVED",
    "PRODUCT_CREATED",
    "MARKETING_PLAN_READY",
    "CONTENT_PLAN_READY",
    "COMMUNITY_PLAN_READY",
    "SOCIAL_PLAN_READY",
    "CAMPAIGN_STARTED",
    "LEAD_CREATED",
    "PERFORMANCE_RECORDED",
    "SALE_COMPLETED",
    "ORDER_SHIPPED",
    "CUSTOMER_FEEDBACK",
    "PROFIT_CALCULATED",
    "KPI_UPDATED",
    "EXPERIMENT_COMPLETED",
    "MEMORY_UPDATED",
    "LESSON_SAVED",
]


@dataclass(frozen=True)
class BusinessEvent:
    name: EventName
    source_department: str
    subject_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
