import unittest

from social.memory import SocialMemory
from social.orchestrator import close_social_campaign, plan_social_campaign
from social.performance import SocialPerformance
from social.policies import policy_for
from social.models import SocialSignals


class TestSocialPerformanceMemory(unittest.TestCase):
    def signals(self):
        return SocialSignals(90, 85, 75, 80)

    def memory(self, platform, profit, orders=4):
        return SocialMemory(platform, "VALUE_PIN" if platform == "PINTEREST" else "REEL_OR_CAROUSEL", 100, orders, max(profit, 0)+10, profit, "SCALE" if profit > 0 else "STOP")

    def test_pinterest_profitable_history_is_preferred(self):
        history = (self.memory("PINTEREST", 30), self.memory("PINTEREST", 40))
        decision = plan_social_campaign(policy_for("PINTEREST"), self.signals(), history)
        self.assertEqual(decision.memory_recommendation, "PREFER")
        self.assertEqual(decision.plan.content_format, "VALUE_PIN")

    def test_platform_memory_does_not_leak(self):
        history = (self.memory("INSTAGRAM", 30), self.memory("INSTAGRAM", 40))
        decision = plan_social_campaign(policy_for("PINTEREST"), self.signals(), history)
        self.assertEqual(decision.memory_recommendation, "INSUFFICIENT_DATA")

    def test_losing_history_pauses_format(self):
        history = (self.memory("INSTAGRAM", -10, 0), self.memory("INSTAGRAM", -5, 0))
        decision = plan_social_campaign(policy_for("INSTAGRAM"), self.signals(), history)
        self.assertEqual(decision.memory_recommendation, "AVOID")
        self.assertEqual(decision.plan.action, "RESEARCH")

    def test_close_profitable_campaign_scales_and_remembers(self):
        decision = plan_social_campaign(policy_for("FACEBOOK"), self.signals())
        performance = SocialPerformance("FACEBOOK", decision.plan.content_format, 1000, 100, 100, 4, 80.0, 10.0)
        closed = close_social_campaign(decision, performance)
        self.assertEqual(closed.experiment_decision, "SCALE")
        self.assertGreater(closed.memory_record.profit, 0)

    def test_invalid_cross_platform_performance_fails(self):
        decision = plan_social_campaign(policy_for("THREADS"), self.signals())
        performance = SocialPerformance("FACEBOOK", decision.plan.content_format, visits=100)
        with self.assertRaises(ValueError):
            close_social_campaign(decision, performance)


if __name__ == "__main__":
    unittest.main()
