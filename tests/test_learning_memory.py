import unittest

from learning.engine import learn_from_history
from learning.models import ExperimentMemory


class TestLearningMemory(unittest.TestCase):
    def item(self, experiment_id, channel, profit, visits=100, orders=3, **overrides):
        values = dict(
            experiment_id=experiment_id,
            product_id="POD-001",
            platform="Etsy",
            market="US",
            niche_type="EVERGREEN",
            channel=channel,
            target_segment="Developers",
            positioning="Useful gift",
            visits=visits,
            orders=orders,
            revenue=60.0,
            profit=profit,
            outcome="SCALE" if profit > 0 else "STOP",
        )
        values.update(overrides)
        return ExperimentMemory(**values)

    def test_repeated_profitable_channel_is_preferred(self):
        history = (
            self.item("E1", "PINTEREST_ORGANIC", 18.0, orders=4),
            self.item("E2", "PINTEREST_ORGANIC", 12.0, orders=3),
            self.item("E3", "INSTAGRAM_ORGANIC", -4.0, orders=1),
            self.item("E4", "INSTAGRAM_ORGANIC", -3.0, orders=1),
        )
        result = learn_from_history(history, niche_type="EVERGREEN", market="US")
        self.assertEqual(result.preferred_channels, ("PINTEREST_ORGANIC",))
        self.assertEqual(result.avoid_channels, ("INSTAGRAM_ORGANIC",))

    def test_single_experiment_does_not_create_trusted_pattern(self):
        history = (self.item("E1", "PINTEREST_ORGANIC", 50.0),)
        result = learn_from_history(history, niche_type="EVERGREEN", market="US")
        self.assertEqual(result.preferred_channels, ())
        self.assertIn("Not enough", result.reason)

    def test_other_market_does_not_leak_into_learning(self):
        history = (
            self.item("E1", "PINTEREST_ORGANIC", 20.0, market="UK"),
            self.item("E2", "PINTEREST_ORGANIC", 20.0, market="UK"),
        )
        result = learn_from_history(history, niche_type="EVERGREEN", market="US")
        self.assertEqual(result.patterns, ())

    def test_conversion_rate_is_aggregated(self):
        history = (
            self.item("E1", "SEO", 10.0, visits=100, orders=2),
            self.item("E2", "SEO", 20.0, visits=200, orders=8),
        )
        result = learn_from_history(history, niche_type="EVERGREEN", market="US")
        self.assertEqual(result.patterns[0].conversion_rate, 0.0333)
        self.assertEqual(result.patterns[0].total_profit, 30.0)


if __name__ == "__main__":
    unittest.main()
