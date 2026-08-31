import unittest

from marketing.manager import build_marketing_plan
from marketing.models import MarketingInput, ProductEconomics
from seo.decision import make_seo_decision
from seo.models import SEOInput


class TestMarketingManager(unittest.TestCase):
    def seo(self, **overrides):
        values = dict(
            product_id="POD-001",
            platform="Etsy",
            market="US",
            language="en",
            demand_score=78,
            competition_score=43,
            buyer_intent_score=91,
            trend_score=72,
            has_search_data=True,
            has_competitor_data=True,
            has_trend_data=True,
            has_price_data=True,
            has_sales_data=False,
        )
        values.update(overrides)
        return make_seo_decision(SEOInput(**values))

    def marketing_input(self, seo=None, economics=None, budget=25.0):
        return MarketingInput(
            seo=seo or self.seo(),
            economics=economics or ProductEconomics(
                sale_price=21.99,
                production_cost=8.00,
                platform_fees=2.50,
                shipping_cost=0.0,
            ),
            target_segment="Python developers",
            positioning="Useful gift with developer humor",
            market="US",
            language="en",
            available_test_budget=budget,
            preferred_channels=("SEO", "PINTEREST"),
        )

    def test_approved_profitable_product_gets_controlled_test(self):
        plan = build_marketing_plan(self.marketing_input())
        self.assertEqual(plan.action, "TEST")
        self.assertGreater(plan.contribution_margin, 0)
        self.assertIsNotNone(plan.guardrails)
        self.assertTrue(plan.guardrails.require_manual_approval)
        self.assertLessEqual(plan.guardrails.max_budget, 25.0)

    def test_seo_reject_blocks_marketing(self):
        plan = build_marketing_plan(
            self.marketing_input(seo=self.seo(trademark_risk=True))
        )
        self.assertEqual(plan.action, "BLOCK")
        self.assertIsNone(plan.guardrails)

    def test_unprofitable_product_is_blocked(self):
        economics = ProductEconomics(
            sale_price=10.0,
            production_cost=9.0,
            platform_fees=2.0,
        )
        plan = build_marketing_plan(self.marketing_input(economics=economics))
        self.assertEqual(plan.action, "BLOCK")

    def test_no_budget_uses_organic_test_without_autospend(self):
        plan = build_marketing_plan(self.marketing_input(budget=0.0))
        self.assertEqual(plan.action, "ORGANIC_TEST")
        self.assertIsNotNone(plan.guardrails)
        self.assertEqual(plan.guardrails.max_budget, 0.0)
        self.assertTrue(plan.guardrails.require_manual_approval)
        self.assertTrue(plan.channels)

    def test_low_confidence_does_not_reach_market_test(self):
        seo = self.seo(
            has_competitor_data=False,
            has_trend_data=False,
            has_price_data=False,
            has_sales_data=False,
        )
        plan = build_marketing_plan(self.marketing_input(seo=seo))
        self.assertEqual(plan.action, "RESEARCH")


if __name__ == "__main__":
    unittest.main()
