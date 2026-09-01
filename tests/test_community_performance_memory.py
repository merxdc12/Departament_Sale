import unittest

from community.memory import learn_community_history, remember
from community.performance import CommunityPerformance, evaluate_community_performance


class TestCommunityPerformanceMemory(unittest.TestCase):
    def performance(self, *, visits=100, orders=3, revenue=60.0, cost=10.0):
        return CommunityPerformance(
            community_name="r/example",
            content_format="ANSWER",
            pain_angle="looking for",
            impressions=1000,
            clicks=100,
            visits=visits,
            orders=orders,
            revenue=revenue,
            total_cost=cost,
        )

    def test_collects_data_before_minimum_sample(self):
        self.assertEqual(
            evaluate_community_performance(self.performance(visits=50, orders=1)),
            "COLLECT_DATA",
        )

    def test_profitable_conversion_scales(self):
        self.assertEqual(evaluate_community_performance(self.performance()), "SCALE")

    def test_losing_experiment_stops(self):
        result = self.performance(visits=100, orders=0, revenue=0.0, cost=10.0)
        self.assertEqual(evaluate_community_performance(result), "STOP")

    def test_memory_prefers_repeated_profitable_format(self):
        p1 = self.performance(visits=100, orders=4, revenue=80.0, cost=10.0)
        p2 = self.performance(visits=120, orders=5, revenue=100.0, cost=10.0)
        history = (
            remember(p1, evaluate_community_performance(p1)),
            remember(p2, evaluate_community_performance(p2)),
        )
        learning = learn_community_history(
            history,
            community_name="r/example",
            content_format="ANSWER",
        )
        self.assertEqual(learning.recommendation, "PREFER")
        self.assertGreater(learning.profit, 0)

    def test_memory_avoids_repeated_losing_format(self):
        p1 = self.performance(visits=100, orders=0, revenue=0.0, cost=10.0)
        p2 = self.performance(visits=100, orders=0, revenue=0.0, cost=8.0)
        history = (
            remember(p1, "STOP"),
            remember(p2, "STOP"),
        )
        learning = learn_community_history(
            history,
            community_name="r/example",
            content_format="ANSWER",
        )
        self.assertEqual(learning.recommendation, "AVOID")

    def test_invalid_metrics_fail_closed(self):
        with self.assertRaises(ValueError):
            CommunityPerformance(
                community_name="r/example",
                content_format="ANSWER",
                pain_angle="problem",
                visits=10,
                orders=11,
            )


if __name__ == "__main__":
    unittest.main()
