import unittest

from community.discovery import RankedCommunity
from community.intelligence import RedditIntelligenceInput
from community.memory import CommunityMemory
from community.orchestrator import close_reddit_campaign, plan_reddit_campaign
from community.pain import PainMiningResult
from community.performance import CommunityPerformance
from community.rules import RuleEvidence


class TestRedditCampaignOrchestrator(unittest.TestCase):
    def data(self, rules=("no self promotion",)):
        return RedditIntelligenceInput(
            ranked_community=RankedCommunity(
                name="r/example", relevance_score=90, activity_score=80, audience_score=70, total_score=84
            ),
            rule_evidence=RuleEvidence(
                community_name="r/example", rule_texts=rules, source_verified=True
            ),
            pain_result=PainMiningResult(pains=(), intent_mentions=3, question_mentions=2, sample_count=10),
            problem_fit=90,
            reputation_fit=80,
        )

    def test_plan_runs_full_safe_pipeline(self):
        plan = plan_reddit_campaign(self.data())
        self.assertEqual(plan.community_name, "r/example")
        self.assertEqual(plan.community_action, "CONTRIBUTE")
        self.assertEqual(plan.content_format, "ANSWER")
        self.assertFalse(plan.link_allowed)
        self.assertTrue(plan.human_approval_required)
        self.assertIsNone(plan.experiment_decision)

    def test_plan_uses_memory(self):
        history = (
            CommunityMemory("r/example", "ANSWER", "question", 100, 4, 50.0, 40.0, "SCALE"),
            CommunityMemory("r/example", "ANSWER", "question", 100, 5, 60.0, 50.0, "SCALE"),
        )
        plan = plan_reddit_campaign(self.data(), history)
        self.assertEqual(plan.memory_recommendation, "PREFER")
        self.assertEqual(plan.content_format, "ANSWER")

    def test_close_campaign_creates_scale_memory(self):
        plan = plan_reddit_campaign(self.data())
        performance = CommunityPerformance(
            community_name="r/example",
            content_format="ANSWER",
            pain_angle=plan.pain_angle,
            impressions=1000,
            clicks=100,
            visits=100,
            orders=4,
            revenue=80.0,
            total_cost=10.0,
        )
        closed = close_reddit_campaign(plan, performance)
        self.assertEqual(closed.experiment_decision, "SCALE")
        self.assertIsNotNone(closed.memory_record)
        self.assertGreater(closed.memory_record.profit, 0)

    def test_close_rejects_wrong_community(self):
        plan = plan_reddit_campaign(self.data())
        performance = CommunityPerformance(
            community_name="r/other", content_format="ANSWER", pain_angle="question"
        )
        with self.assertRaises(ValueError):
            close_reddit_campaign(plan, performance)


if __name__ == "__main__":
    unittest.main()
