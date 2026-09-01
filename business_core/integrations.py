"""Adapters that publish existing department outputs onto the shared EventBus.

These helpers keep department internals independent from business_core. Existing
agents continue to calculate their own decisions; adapters only translate results
into shared BusinessEvent contracts.
"""

from dashboard.kpi import KPIDashboard
from learning.models import LearningRecommendation
from marketing.models import MarketingPlan
from performance.models import ListingPerformance
from seo.decision import SEODecision

from .event_bus import EventBus
from .events import BusinessEvent


def publish_seo_decision(bus: EventBus, decision: SEODecision) -> BusinessEvent:
    analysis = decision.analysis
    event = BusinessEvent(
        name="SEO_ANALYZED",
        source_department="seo",
        subject_id=decision.product_id,
        payload={
            "platform": decision.platform,
            "raw_opportunity_score": analysis.raw_opportunity_score,
            "adjusted_score": analysis.adjusted_score,
            "risk_level": analysis.risk_level,
            "confidence": analysis.confidence,
            "decision": analysis.decision,
            "reason": analysis.reason,
        },
    )
    bus.publish(event)
    return event


def publish_marketing_plan(bus: EventBus, plan: MarketingPlan) -> BusinessEvent:
    event = BusinessEvent(
        name="MARKETING_PLAN_READY",
        source_department="marketing",
        subject_id=plan.product_id,
        payload={
            "platform": plan.platform,
            "action": plan.action,
            "market": plan.market,
            "channels": plan.channels,
            "contribution_margin": plan.contribution_margin,
            "margin_rate": plan.margin_rate,
            "manual_approval_required": bool(
                plan.guardrails and plan.guardrails.require_manual_approval
            ),
        },
    )
    bus.publish(event)
    return event


def publish_community_plan(bus: EventBus, decision, *, subject_id: str) -> BusinessEvent:
    event = BusinessEvent(
        name="COMMUNITY_PLAN_READY",
        source_department="community",
        subject_id=subject_id,
        payload={
            "community_name": decision.community_name,
            "opportunity_score": decision.opportunity_score,
            "action": decision.community_action,
            "content_format": decision.content_format,
            "human_approval_required": decision.human_approval_required,
        },
    )
    bus.publish(event)
    return event


def publish_social_plan(bus: EventBus, decision, *, subject_id: str) -> BusinessEvent:
    plan = decision.plan
    event = BusinessEvent(
        name="SOCIAL_PLAN_READY",
        source_department="social",
        subject_id=subject_id,
        payload={
            "platform": plan.platform,
            "action": plan.action,
            "content_format": plan.content_format,
            "link_allowed": plan.link_allowed,
            "human_approval_required": plan.human_approval_required,
            "memory_recommendation": decision.memory_recommendation,
        },
    )
    bus.publish(event)
    return event


def publish_listing_performance(bus: EventBus, performance: ListingPerformance) -> tuple[BusinessEvent, ...]:
    total_cost = round(
        performance.fees
        + performance.production_cost
        + performance.advertising_cost
        + performance.other_cost,
        2,
    )
    profit = round(performance.revenue - total_cost, 2)
    recorded = BusinessEvent(
        name="PERFORMANCE_RECORDED",
        source_department="performance",
        subject_id=performance.listing_id or performance.shop_id or performance.platform,
        payload={
            "platform": performance.platform,
            "impressions": performance.impressions,
            "clicks": performance.clicks,
            "visits": performance.visits,
            "orders": performance.orders,
            "revenue": performance.revenue,
            "total_cost": total_cost,
            "profit": profit,
            "data_source": performance.data_source,
        },
    )
    bus.publish(recorded)
    events = [recorded]
    if performance.orders > 0:
        sale = BusinessEvent(
            name="SALE_COMPLETED",
            source_department="performance",
            subject_id=recorded.subject_id,
            payload={
                "platform": performance.platform,
                "orders": performance.orders,
                "revenue": performance.revenue,
                "profit": profit,
            },
        )
        bus.publish(sale)
        events.append(sale)
    return tuple(events)


def publish_kpi_dashboard(bus: EventBus, dashboard: KPIDashboard, *, subject_id: str = "business") -> BusinessEvent:
    event = BusinessEvent(
        name="KPI_UPDATED",
        source_department="cfo_kpi",
        subject_id=subject_id,
        payload={
            "experiments": dashboard.experiments,
            "visits": dashboard.visits,
            "orders": dashboard.orders,
            "revenue": dashboard.revenue,
            "profit": dashboard.profit,
            "conversion_rate": dashboard.conversion_rate,
            "profitable_experiments": dashboard.profitable_experiments,
            "scale_decisions": dashboard.scale_decisions,
            "stop_decisions": dashboard.stop_decisions,
        },
    )
    bus.publish(event)
    return event


def publish_learning_recommendation(
    bus: EventBus,
    recommendation: LearningRecommendation,
    *,
    subject_id: str,
) -> BusinessEvent:
    event = BusinessEvent(
        name="MEMORY_UPDATED",
        source_department="memory",
        subject_id=subject_id,
        payload={
            "preferred_channels": recommendation.preferred_channels,
            "avoid_channels": recommendation.avoid_channels,
            "reason": recommendation.reason,
        },
    )
    bus.publish(event)
    return event
