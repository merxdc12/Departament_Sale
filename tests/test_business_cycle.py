import unittest

from business_core import EventBus, OpportunitySignals, RiskAssessment
from business_intelligence import CompetitorSnapshot
from marketing.experiment import ExperimentResult
from workflow import BusinessCycleCoordinator, BusinessCycleInput, OpportunityWorkflowInput


class BusinessCycleTests(unittest.TestCase):
    def _opportunity(self):
        competitors = tuple(CompetitorSnapshot(f"C{i}", 99 + i, 4.2, 50 + i) for i in range(5))
        return OpportunityWorkflowInput(
            opportunity_id="OP-CYCLE",
            problem="Need simple local-first watering automation",
            market="EU",
            signals=OpportunitySignals(90, 25, 88, 85, ("search", "community", "competitors", "price", "sales")),
            possible_business_lines=("DIY_IOT",),
            competitors=competitors,
            risk=RiskAssessment("OP-CYCLE", "LOW", penalty=0),
            sale_price=120,
            production_cost=40,
            platform_fees=10,
            shipping_cost=10,
            packaging_cost=2,
            fixed_test_cost=100,
        )

    def test_waits_at_human_gate_without_approval(self):
        bus = EventBus()
        result = BusinessCycleCoordinator(bus).run(BusinessCycleInput(
            opportunity=self._opportunity(), human_approved=False,
            product_id="P-1", product_name="Watering Kit", business_line="DIY_IOT",
        ))
        self.assertEqual(result.final_action, "WAIT_APPROVAL")
        self.assertIsNone(result.product_draft)
        self.assertFalse(result.external_execution_allowed)
        self.assertIn("HUMAN_APPROVAL_REQUIRED", [event.name for event in bus.history])
        self.assertNotIn("PRODUCT_DRAFT_CREATED", [event.name for event in bus.history])

    def test_full_cycle_reaches_memory_kpi_and_orchestrator_without_external_execution(self):
        bus = EventBus()
        observed = ExperimentResult(impressions=1000, clicks=120, visits=120, orders=6, revenue=600, total_cost=300)
        result = BusinessCycleCoordinator(bus).run(BusinessCycleInput(
            opportunity=self._opportunity(), human_approved=True,
            product_id="P-2", product_name="Watering Kit", business_line="DIY_IOT",
            observed_result=observed,
        ))
        names = [event.name for event in bus.history]
        for required in (
            "HUMAN_APPROVAL_GRANTED", "PRODUCT_DRAFT_CREATED", "MARKETING_PLAN_READY",
            "SOCIAL_PLAN_READY", "COMMUNITY_PLAN_READY", "PERFORMANCE_RECORDED",
            "EXPERIMENT_COMPLETED", "KPI_UPDATED", "MEMORY_UPDATED",
            "ORCHESTRATOR_RECOMMENDATION", "WORKFLOW_COMPLETED",
        ):
            self.assertIn(required, names)
        self.assertEqual(result.final_action, "SCALE")
        self.assertFalse(result.external_execution_allowed)
        self.assertFalse(result.product_draft.external_execution_allowed)


if __name__ == "__main__":
    unittest.main()
