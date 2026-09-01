import unittest

from business_core import (
    BusinessEvent,
    BusinessOpportunity,
    EventBus,
    FinanceRecord,
    OpportunitySignals,
)


class BusinessCoreTests(unittest.TestCase):
    def test_opportunity_signal_validation(self):
        with self.assertRaises(ValueError):
            OpportunitySignals(101, 20, 30, 40)

    def test_business_opportunity_can_be_shared_between_departments(self):
        signals = OpportunitySignals(
            demand_score=82,
            competition_score=47,
            buyer_intent_score=73,
            trend_score=69,
            evidence_sources=("community", "search", "competitors"),
        )
        opportunity = BusinessOpportunity(
            opportunity_id="OP-001",
            problem="Need simple local-first automatic watering",
            market="EU",
            signals=signals,
            possible_business_lines=("DIGITAL", "DIY_IOT"),
            score=71,
            confidence=0.8,
        )
        self.assertEqual(opportunity.status, "DISCOVERED")
        self.assertIn("DIY_IOT", opportunity.possible_business_lines)

    def test_event_bus_routes_sale_to_multiple_departments(self):
        bus = EventBus()
        received = []

        def cfo_handler(event):
            received.append(("cfo", event.subject_id))

        def memory_handler(event):
            received.append(("memory", event.subject_id))

        bus.subscribe("SALE_COMPLETED", cfo_handler)
        bus.subscribe("SALE_COMPLETED", memory_handler)
        bus.publish(
            BusinessEvent(
                name="SALE_COMPLETED",
                source_department="sales",
                subject_id="ORDER-7",
                payload={"revenue": 99.0},
            )
        )

        self.assertEqual(received, [("cfo", "ORDER-7"), ("memory", "ORDER-7")])
        self.assertEqual(len(bus.history), 1)

    def test_finance_record_exposes_profit(self):
        record = FinanceRecord("FIN-1", "PRODUCT-1", revenue=100.0, cost=63.45)
        self.assertEqual(record.profit, 36.55)


if __name__ == "__main__":
    unittest.main()
