import unittest
from types import SimpleNamespace

from business_core import (
    EventBus,
    publish_community_plan,
    publish_kpi_dashboard,
    publish_learning_recommendation,
    publish_listing_performance,
    publish_marketing_plan,
    publish_seo_decision,
    publish_social_plan,
)
from dashboard.kpi import KPIDashboard
from learning.models import LearningRecommendation
from marketing.manager import build_marketing_plan
from marketing.models import MarketingInput, ProductEconomics
from performance.models import ListingPerformance
from seo.decision import make_seo_decision
from seo.models import SEOInput


class InterdepartmentFlowTests(unittest.TestCase):
    def test_existing_departments_publish_shared_business_events(self):
        bus = EventBus()
        event_names = []
        sale_consumers = []

        for name in (
            "SEO_ANALYZED",
            "MARKETING_PLAN_READY",
            "COMMUNITY_PLAN_READY",
            "SOCIAL_PLAN_READY",
            "PERFORMANCE_RECORDED",
            "SALE_COMPLETED",
            "KPI_UPDATED",
            "MEMORY_UPDATED",
        ):
            bus.subscribe(name, lambda event, names=event_names: names.append(event.name))

        bus.subscribe("SALE_COMPLETED", lambda event: sale_consumers.append("cfo"))
        bus.subscribe("SALE_COMPLETED", lambda event: sale_consumers.append("memory"))

        seo = make_seo_decision(
            SEOInput(
                product_id="PRODUCT-1",
                platform="ETSY",
                market="EU",
                language="en",
                demand_score=85,
                competition_score=30,
                buyer_intent_score=82,
                trend_score=74,
                has_search_data=True,
                has_competitor_data=True,
                has_trend_data=True,
                has_price_data=True,
                has_sales_data=True,
            )
        )
        publish_seo_decision(bus, seo)

        marketing = build_marketing_plan(
            MarketingInput(
                seo=seo,
                economics=ProductEconomics(
                    sale_price=30.0,
                    production_cost=10.0,
                    platform_fees=3.0,
                    shipping_cost=5.0,
                ),
                target_segment="DIY buyers",
                positioning="Simple reliable kit",
                market="EU",
                language="en",
            )
        )
        publish_marketing_plan(bus, marketing)

        community = SimpleNamespace(
            community_name="r/example",
            opportunity_score=78,
            community_action="CONTRIBUTE",
            content_format="EDUCATIONAL_POST",
            human_approval_required=True,
        )
        publish_community_plan(bus, community, subject_id="PRODUCT-1")

        social_plan = SimpleNamespace(
            platform="PINTEREST",
            action="ORGANIC_CONTENT",
            content_format="PIN",
            link_allowed=True,
            human_approval_required=True,
        )
        social = SimpleNamespace(plan=social_plan, memory_recommendation="RETEST")
        publish_social_plan(bus, social, subject_id="PRODUCT-1")

        performance = ListingPerformance(
            platform="ETSY",
            listing_id="LISTING-1",
            visits=120,
            orders=4,
            revenue=120.0,
            fees=12.0,
            production_cost=40.0,
            advertising_cost=0.0,
            other_cost=8.0,
            data_source="official_api",
        )
        publish_listing_performance(bus, performance)

        publish_kpi_dashboard(
            bus,
            KPIDashboard(
                experiments=1,
                visits=120,
                orders=4,
                revenue=120.0,
                profit=60.0,
                conversion_rate=0.0333,
                profitable_experiments=1,
                scale_decisions=1,
                stop_decisions=0,
            ),
        )

        publish_learning_recommendation(
            bus,
            LearningRecommendation(
                preferred_channels=("PINTEREST",),
                avoid_channels=(),
                patterns=(),
                reason="Repeated profitable first-party evidence.",
            ),
            subject_id="PRODUCT-1",
        )

        self.assertEqual(
            event_names,
            [
                "SEO_ANALYZED",
                "MARKETING_PLAN_READY",
                "COMMUNITY_PLAN_READY",
                "SOCIAL_PLAN_READY",
                "PERFORMANCE_RECORDED",
                "SALE_COMPLETED",
                "KPI_UPDATED",
                "MEMORY_UPDATED",
            ],
        )
        self.assertEqual(sale_consumers, ["cfo", "memory"])
        self.assertEqual(len(bus.history), 8)
        self.assertEqual(bus.history[5].payload["profit"], 60.0)


if __name__ == "__main__":
    unittest.main()
