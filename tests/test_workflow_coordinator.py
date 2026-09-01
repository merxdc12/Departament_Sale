import unittest

from business_core import EventBus, OpportunitySignals, RiskAssessment
from business_intelligence import CompetitorSnapshot
from workflow import OpportunityWorkflowCoordinator, OpportunityWorkflowInput


class WorkflowCoordinatorTests(unittest.TestCase):
    def test_profitable_flow_reaches_human_gate(self):
        bus = EventBus()
        coordinator = OpportunityWorkflowCoordinator(bus)
        result = coordinator.run(
            OpportunityWorkflowInput(
                opportunity_id="OP-W1",
                problem="Need local-first watering automation",
                market="EU",
                signals=OpportunitySignals(88, 35, 82, 75, ("community", "search", "competitors", "price", "sales")),
                possible_business_lines=("DIY_IOT",),
                competitors=(
                    CompetitorSnapshot("C1", 89, 4.2, 100, weaknesses=("cloud required",)),
                    CompetitorSnapshot("C2", 109, 4.1, 80, weaknesses=("unclear setup",)),
                    CompetitorSnapshot("C3", 119, 4.0, 50),
                    CompetitorSnapshot("C4", 99, 4.3, 70),
                    CompetitorSnapshot("C5", 129, 4.4, 40),
                ),
                risk=RiskAssessment("OP-W1", "LOW"),
                sale_price=119,
                production_cost=40,
                platform_fees=12,
                shipping_cost=10,
                packaging_cost=3,
                fixed_test_cost=100,
            )
        )
        self.assertIsNone(result.stopped_at)
        self.assertTrue(result.economics.profitable)
        self.assertEqual([event.name for event in bus.history], ["OPPORTUNITY_FOUND", "COMPETITION_ANALYZED", "PRODUCT_VALIDATED", "ECONOMICS_APPROVED"])
        self.assertIn("Human approval", result.reason)

    def test_critical_risk_stops_before_economics(self):
        bus = EventBus()
        coordinator = OpportunityWorkflowCoordinator(bus)
        result = coordinator.run(
            OpportunityWorkflowInput(
                opportunity_id="OP-W2",
                problem="Risky product",
                market="EU",
                signals=OpportunitySignals(95, 10, 95, 90, ("search", "community", "competitors", "price", "sales")),
                possible_business_lines=("POD",),
                competitors=(CompetitorSnapshot("C1", 20, 4.0, 100),),
                risk=RiskAssessment("OP-W2", "CRITICAL", blocked=True, reasons=("policy",)),
                sale_price=50,
                production_cost=10,
            )
        )
        self.assertEqual(result.stopped_at, "PRODUCT_VALIDATION")
        self.assertIsNone(result.economics)
        self.assertEqual([event.name for event in bus.history], ["OPPORTUNITY_FOUND", "COMPETITION_ANALYZED", "PRODUCT_VALIDATED"])


if __name__ == "__main__":
    unittest.main()
