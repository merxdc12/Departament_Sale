import unittest

from business_core import EventBus, OpportunitySignals, RiskAssessment
from business_core.integrations import publish_competitor_analysis, publish_opportunity, publish_product_validation, publish_unit_economics
from business_intelligence import CompetitorSnapshot, analyze_competitors, discover_opportunity, validate_product
from economics import calculate_unit_economics


class BusinessIntelligenceFlowTests(unittest.TestCase):
    def test_opportunity_to_economics_events(self):
        bus = EventBus()
        signals = OpportunitySignals(82, 47, 73, 69, ("community", "search", "competitors", "price"))
        opportunity = discover_opportunity(opportunity_id="OP-1", problem="Need local-first watering automation", market="EU", signals=signals, possible_business_lines=("DIY_IOT", "DIGITAL"))
        competitors = analyze_competitors((
            CompetitorSnapshot("C1", 89.0, 4.2, 120, weaknesses=("unclear setup",)),
            CompetitorSnapshot("C2", 109.0, 4.0, 80, weaknesses=("cloud required",)),
        ))
        validation = validate_product(opportunity, competitors, RiskAssessment("OP-1", "LOW", penalty=0))
        economics = calculate_unit_economics(sale_price=99, production_cost=35, platform_fees=10, shipping_cost=12, packaging_cost=2, fixed_test_cost=100)

        publish_opportunity(bus, opportunity)
        publish_competitor_analysis(bus, competitors, subject_id="OP-1")
        publish_product_validation(bus, validation)
        publish_unit_economics(bus, economics, subject_id="OP-1")

        self.assertEqual([x.name for x in bus.history], ["OPPORTUNITY_FOUND", "COMPETITION_ANALYZED", "PRODUCT_VALIDATED", "ECONOMICS_APPROVED"])
        self.assertGreaterEqual(opportunity.score, 60)
        self.assertTrue(economics.profitable)
        self.assertEqual(economics.break_even_orders, 3)

    def test_risk_gate_can_reject_product(self):
        signals = OpportunitySignals(90, 20, 90, 90, ("search", "community", "competitors", "price", "sales"))
        opportunity = discover_opportunity(opportunity_id="OP-2", problem="Test", market="EU", signals=signals, possible_business_lines=("POD",))
        competitors = analyze_competitors((CompetitorSnapshot("C1", 20, 4.0, 10),))
        result = validate_product(opportunity, competitors, RiskAssessment("OP-2", "CRITICAL", blocked=True, reasons=("policy",)))
        self.assertEqual(result.decision, "REJECT")


if __name__ == "__main__":
    unittest.main()
