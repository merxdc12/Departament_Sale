"""Adapters publishing department outputs onto the shared EventBus."""

from dashboard.kpi import KPIDashboard
from learning.models import LearningRecommendation
from marketing.models import MarketingPlan
from performance.models import ListingPerformance
from seo.decision import SEODecision

from .event_bus import EventBus
from .events import BusinessEvent


def _publish(bus, name, source, subject_id, payload):
    event = BusinessEvent(name=name, source_department=source, subject_id=subject_id, payload=payload)
    bus.publish(event)
    return event


def publish_opportunity(bus, opportunity):
    return _publish(bus, "OPPORTUNITY_FOUND", "business_intelligence", opportunity.opportunity_id, {"problem": opportunity.problem, "market": opportunity.market, "score": opportunity.score, "confidence": opportunity.confidence, "business_lines": opportunity.possible_business_lines})


def publish_competitor_analysis(bus, analysis, *, subject_id):
    return _publish(bus, "COMPETITION_ANALYZED", "competitor_intelligence", subject_id, {"competitors": analysis.competitors, "average_price": analysis.average_price, "average_rating": analysis.average_rating, "total_reviews": analysis.total_reviews, "gaps": analysis.gaps, "confidence": analysis.evidence_confidence})


def publish_product_validation(bus, validation):
    return _publish(bus, "PRODUCT_VALIDATED", "product_validation", validation.opportunity_id, {"decision": validation.decision, "score": validation.score, "confidence": validation.confidence, "reason": validation.reason})


def publish_unit_economics(bus, economics, *, subject_id):
    name = "ECONOMICS_APPROVED" if economics.profitable else "ECONOMICS_REJECTED"
    return _publish(bus, name, "economics", subject_id, {"sale_price": economics.sale_price, "variable_cost": economics.variable_cost, "contribution_margin": economics.contribution_margin, "margin_rate": economics.margin_rate, "break_even_orders": economics.break_even_orders, "profitable": economics.profitable})


def publish_seo_decision(bus: EventBus, decision: SEODecision):
    a = decision.analysis
    return _publish(bus, "SEO_ANALYZED", "seo", decision.product_id, {"platform": decision.platform, "raw_opportunity_score": a.raw_opportunity_score, "adjusted_score": a.adjusted_score, "risk_level": a.risk_level, "confidence": a.confidence, "decision": a.decision, "reason": a.reason})


def publish_marketing_plan(bus: EventBus, plan: MarketingPlan):
    return _publish(bus, "MARKETING_PLAN_READY", "marketing", plan.product_id, {"platform": plan.platform, "action": plan.action, "market": plan.market, "channels": plan.channels, "contribution_margin": plan.contribution_margin, "margin_rate": plan.margin_rate, "manual_approval_required": bool(plan.guardrails and plan.guardrails.require_manual_approval)})


def publish_community_plan(bus, decision, *, subject_id):
    return _publish(bus, "COMMUNITY_PLAN_READY", "community", subject_id, {"community_name": decision.community_name, "opportunity_score": decision.opportunity_score, "action": decision.community_action, "content_format": decision.content_format, "human_approval_required": decision.human_approval_required})


def publish_social_plan(bus, decision, *, subject_id):
    p = decision.plan
    return _publish(bus, "SOCIAL_PLAN_READY", "social", subject_id, {"platform": p.platform, "action": p.action, "content_format": p.content_format, "link_allowed": p.link_allowed, "human_approval_required": p.human_approval_required, "memory_recommendation": decision.memory_recommendation})


def publish_listing_performance(bus: EventBus, performance: ListingPerformance):
    total_cost = round(performance.fees + performance.production_cost + performance.advertising_cost + performance.other_cost, 2)
    profit = round(performance.revenue - total_cost, 2)
    recorded = _publish(bus, "PERFORMANCE_RECORDED", "performance", performance.listing_id or performance.shop_id or performance.platform, {"platform": performance.platform, "impressions": performance.impressions, "clicks": performance.clicks, "visits": performance.visits, "orders": performance.orders, "revenue": performance.revenue, "total_cost": total_cost, "profit": profit, "data_source": performance.data_source})
    events = [recorded]
    if performance.orders > 0:
        events.append(_publish(bus, "SALE_COMPLETED", "performance", recorded.subject_id, {"platform": performance.platform, "orders": performance.orders, "revenue": performance.revenue, "profit": profit}))
    return tuple(events)


def publish_kpi_dashboard(bus: EventBus, dashboard: KPIDashboard, *, subject_id="business"):
    return _publish(bus, "KPI_UPDATED", "cfo_kpi", subject_id, {"experiments": dashboard.experiments, "visits": dashboard.visits, "orders": dashboard.orders, "revenue": dashboard.revenue, "profit": dashboard.profit, "conversion_rate": dashboard.conversion_rate, "profitable_experiments": dashboard.profitable_experiments, "scale_decisions": dashboard.scale_decisions, "stop_decisions": dashboard.stop_decisions})


def publish_learning_recommendation(bus: EventBus, recommendation: LearningRecommendation, *, subject_id):
    return _publish(bus, "MEMORY_UPDATED", "memory", subject_id, {"preferred_channels": recommendation.preferred_channels, "avoid_channels": recommendation.avoid_channels, "reason": recommendation.reason})
