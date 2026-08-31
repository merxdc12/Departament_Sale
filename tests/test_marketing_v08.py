import unittest

from marketing.experiment import ExperimentResult, evaluate_experiment
from marketing.niche import NicheSignals, classify_niche
from marketing.organic import organic_first_plan


class TestMarketingV08(unittest.TestCase):
    def test_hybrid_niche(self):
        self.assertEqual(classify_niche(NicheSignals(80, 75, 20)), "HYBRID")

    def test_trending_niche(self):
        self.assertEqual(classify_niche(NicheSignals(85, 40, 10)), "TRENDING")

    def test_seasonal_niche(self):
        self.assertEqual(classify_niche(NicheSignals(50, 50, 80)), "SEASONAL")

    def test_organic_plan_disables_paid_ads(self):
        plan = organic_first_plan("Etsy")
        self.assertFalse(plan.paid_ads_enabled)
        self.assertIn("PINTEREST_ORGANIC", plan.channels)

    def test_experiment_collects_data_before_decision(self):
        result = ExperimentResult(visits=50, orders=2, revenue=40, total_cost=10)
        self.assertEqual(evaluate_experiment(result), "COLLECT_DATA")

    def test_profitable_conversion_scales(self):
        result = ExperimentResult(visits=100, orders=4, revenue=80, total_cost=30)
        self.assertEqual(evaluate_experiment(result), "SCALE")

    def test_weak_conversion_stops(self):
        result = ExperimentResult(visits=100, orders=0, revenue=0, total_cost=0)
        self.assertEqual(evaluate_experiment(result), "STOP")

    def test_middle_result_modifies(self):
        result = ExperimentResult(visits=100, orders=2, revenue=40, total_cost=20)
        self.assertEqual(evaluate_experiment(result), "MODIFY")


if __name__ == "__main__":
    unittest.main()
