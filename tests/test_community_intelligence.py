import unittest

from community.discovery import SubredditCandidate, rank_subreddits
from community.intelligence import RedditIntelligenceInput, build_reddit_opportunity
from community.pain import DiscussionSample, mine_pains
from community.rules import RuleEvidence, analyze_rule_evidence


class TestCommunityIntelligence(unittest.TestCase):
    def test_discovery_prefers_relevant_active_community(self):
        ranked = rank_subreddits(
            (
                SubredditCandidate(
                    name="r/python",
                    title="Python programming",
                    description="Python developers, coding, libraries and tools",
                    subscribers=1000000,
                    active_users=3000,
                ),
                SubredditCandidate(
                    name="r/random",
                    title="General chat",
                    description="Everything and anything",
                    subscribers=5000000,
                    active_users=5000,
                ),
            ),
            target_terms=("python", "developers", "coding"),
        )
        self.assertEqual(ranked[0].name, "r/python")
        self.assertGreater(ranked[0].relevance_score, ranked[1].relevance_score)

    def test_unverified_rules_fail_closed(self):
        policy = analyze_rule_evidence(
            RuleEvidence(
                community_name="r/example",
                rule_texts=("Self promotion allowed; links allowed",),
                source_verified=False,
            )
        )
        self.assertFalse(policy.rules_checked)
        self.assertFalse(policy.self_promotion_allowed)
        self.assertFalse(policy.links_allowed)

    def test_explicit_no_promotion_overrides_positive_phrase(self):
        policy = analyze_rule_evidence(
            RuleEvidence(
                community_name="r/example",
                rule_texts=("Promotion allowed in weekly thread. No self promotion elsewhere.",),
                source_verified=True,
            )
        )
        self.assertTrue(policy.rules_checked)
        self.assertFalse(policy.self_promotion_allowed)

    def test_pain_mining_uses_supplied_discussion_evidence(self):
        result = mine_pains(
            (
                DiscussionSample("Looking for a better Python gift. Any recommendation?", score=50, comments=20),
                DiscussionSample("I need help finding a useful developer gift alternative.", score=10, comments=5),
            )
        )
        self.assertEqual(result.sample_count, 2)
        self.assertGreater(result.intent_mentions, 0)
        self.assertTrue(any(x.phrase == "looking for" for x in result.pains))

    def test_integrated_pipeline_contributes_when_promotion_forbidden(self):
        ranked = rank_subreddits(
            (
                SubredditCandidate(
                    name="r/python",
                    title="Python developers",
                    description="Programming, Python and developer tools",
                    subscribers=1000000,
                    active_users=5000,
                ),
            ),
            target_terms=("python", "developers"),
        )[0]
        pain = mine_pains(
            (
                DiscussionSample("Looking for Python gifts, what do you recommend?", score=50, comments=30),
                DiscussionSample("Need help finding a developer gift alternative?", score=20, comments=10),
            )
        )
        result = build_reddit_opportunity(
            RedditIntelligenceInput(
                ranked_community=ranked,
                rule_evidence=RuleEvidence(
                    community_name="r/python",
                    rule_texts=("No self promotion. No external links.",),
                    source_verified=True,
                ),
                pain_result=pain,
                problem_fit=90,
                reputation_fit=80,
            )
        )
        self.assertEqual(result.action, "CONTRIBUTE")
        self.assertFalse(result.link_allowed)

    def test_integrated_pipeline_allows_direct_promotion_only_when_explicitly_allowed(self):
        ranked = rank_subreddits(
            (
                SubredditCandidate(
                    name="r/pythonproducts",
                    title="Python products for developers",
                    description="Python developer products, gifts and recommendations",
                    subscribers=100000,
                    active_users=1000,
                ),
            ),
            target_terms=("python", "developers", "products"),
        )[0]
        pain = mine_pains(
            (
                DiscussionSample("Looking for the best Python product to buy. Any recommendation?", score=75, comments=50),
                DiscussionSample("Where can I find a Python developer gift worth it?", score=60, comments=40),
            )
        )
        result = build_reddit_opportunity(
            RedditIntelligenceInput(
                ranked_community=ranked,
                rule_evidence=RuleEvidence(
                    community_name="r/pythonproducts",
                    rule_texts=(
                        "Self promotion allowed. External links allowed. Disclose your affiliation.",
                    ),
                    source_verified=True,
                ),
                pain_result=pain,
                problem_fit=95,
                reputation_fit=90,
            )
        )
        self.assertEqual(result.action, "DIRECT_PROMOTION")
        self.assertTrue(result.link_allowed)
        self.assertTrue(result.human_approval_required)


if __name__ == "__main__":
    unittest.main()
