import unittest

from dashboard.kpi import build_kpi_dashboard
from learning.models import ExperimentMemory
from marketing.manager import build_marketing_plan
from marketing.models import MarketingInput, ProductEconomics
from marketing.niche import NicheSignals
from orchestrator.engine import orchestrate
from orchestrator.models import OrchestratorInput
from seo.decision import make_seo_decision
from seo.models import SEOInput


class TestOrchestratorDashboard(unittest.TestCase):
    def seo(self):
        return make_seo_decision(SEOInput(
            product_id="POD-001", platform="Etsy", market="US", language="en",
            demand_score=80, competition_score=40, buyer_intent_score=85, trend_score=75,
            has_search_data=True, has_competitor_data=True, has_trend_data=True,
            has_price_data=True, has_sales_data=False,
        ))

    def marketing(self):
        return MarketingInput(
            seo=self.seo(),
            economics=ProductEconomics(24.0, 9.0, platform_fees=3.0),
            target_segment="Python developers",
            positioning="Funny debugging gift",
            market="US", language="en", available_test_budget=0,
        )

    def test_orchestrator_preserves_organic_first(self):
        result = orchestrate(OrchestratorInput(
            marketing=self.marketing(),
            niche_signals=NicheSignals(80, 75, 10),
        ))
        self.assertEqual(result.niche_type, "HYBRID")
        self.assertEqual(result.action, "ORGANIC_TEST")

    def test_dashboard_aggregates_profit_first_kpis(self):
        history = (
            ExperimentMemory("e1", "p1", "Etsy", "US", "EVERGREEN", "PINTEREST_ORGANIC", "devs", "gift", visits=100, orders=4, revenue=80, profit=30, outcome="SCALE"),
            ExperimentMemory("e2", "p2", "Etsy", "US", "EVERGREEN", "MARKETPLACE_SEO", "devs", "gift", visits=100, orders=1, revenue=20, profit=-5, outcome="STOP"),
        )
        kpi = build_kpi_dashboard(history)
        self.assertEqual(kpi.experiments, 2)
        self.assertEqual(kpi.visits, 200)
        self.assertEqual(kpi.orders, 5)
        self.assertEqual(kpi.profit, 25)
        self.assertEqual(kpi.conversion_rate, 0.025)
        self.assertEqual(kpi.scale_decisions, 1)
        self.assertEqual(kpi.stop_decisions, 1)


if __name__ == "__main__":
    unittest.main()
