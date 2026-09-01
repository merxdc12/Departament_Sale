import unittest

from community.adaptive_strategy import build_adaptive_content_strategy
from community.memory import CommunityMemory
from community.models import CommunityOpportunity, CommunityPolicy
from community.pain import PainMiningResult


class TestAdaptiveCommunityStrategy(unittest.TestCase):
    def pain(self):
        return PainMiningResult(pains=(), intent_mentions=2, question_mentions=2, sample_count=10)

    def opportunity(self, action="CONTRIBUTE"):
        return CommunityOpportunity(
            platform="REDDIT",
            community_name="r/example",
            score=80,
            action=action,
            risk_level="LOW",
            link_allowed=action == "DIRECT_PROMOTION",
        )

    def policy(self, promotion=False, links=False):
        return CommunityPolicy(
            community_name="r/example",
            rules_checked=True,
            self_promotion_allowed=promotion,
            links_allowed=links,
        )

    def memory(self, profit, orders=4, visits=100, outcome="SCALE", content_format="ANSWER"):
        return CommunityMemory(
            community_name="r/example",
            content_format=content_format,
            pain_angle="question",
            visits=visits,
            orders=orders,
            revenue=max(profit, 0) + 10,
            profit=profit,
            outcome=outcome,
        )

    def test_profitable_history_prioritizes_safe_format(self):
        history = (self.memory(20), self.memory(30))
        result = build_adaptive_content_strategy(self.opportunity(), self.policy(), self.pain(), history)
        self.assertEqual(result.learning.recommendation, "PREFER")
        self.assertTrue(result.memory_applied)
        self.assertEqual(result.strategy.format, "ANSWER")
        self.assertFalse(result.strategy.link_allowed)

    def test_losing_history_pauses_format(self):
        history = (self.memory(-10, orders=0, outcome="STOP"), self.memory(-5, orders=0, outcome="STOP"))
        result = build_adaptive_content_strategy(self.opportunity(), self.policy(), self.pain(), history)
        self.assertEqual(result.learning.recommendation, "AVOID")
        self.assertEqual(result.strategy.format, "NO_CONTENT")
        self.assertEqual(result.strategy.mention_level, "NONE")

    def test_memory_cannot_override_current_block(self):
        history = (
            self.memory(50, content_format="NO_CONTENT"),
            self.memory(60, content_format="NO_CONTENT"),
        )
        result = build_adaptive_content_strategy(
            self.opportunity(action="BLOCK"), self.policy(), self.pain(), history
        )
        self.assertEqual(result.strategy.format, "NO_CONTENT")
        self.assertFalse(result.memory_applied)

    def test_memory_cannot_enable_links(self):
        history = (self.memory(20), self.memory(30))
        result = build_adaptive_content_strategy(self.opportunity(), self.policy(), self.pain(), history)
        self.assertFalse(result.strategy.link_allowed)
        self.assertEqual(result.strategy.mention_level, "NONE")

    def test_direct_promotion_still_requires_current_permission(self):
        with self.assertRaises(ValueError):
            build_adaptive_content_strategy(
                self.opportunity(action="DIRECT_PROMOTION"),
                self.policy(promotion=False, links=False),
                self.pain(),
                (),
            )


if __name__ == "__main__":
    unittest.main()
