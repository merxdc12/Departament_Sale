import unittest

from community.content_strategy import build_content_strategy
from community.models import CommunityOpportunity, CommunityPolicy
from community.pain import PainMiningResult, PainSignal


class TestContentStrategy(unittest.TestCase):
    def pain(self, *, questions=2):
        return PainMiningResult(
            pains=(PainSignal("looking for", 3, 6),),
            intent_mentions=3,
            question_mentions=questions,
            sample_count=5,
        )

    def opportunity(self, action, *, link_allowed=False):
        return CommunityOpportunity(
            platform="REDDIT",
            community_name="r/example",
            score=80,
            action=action,
            risk_level="LOW",
            link_allowed=link_allowed,
        )

    def test_research_generates_no_content(self):
        strategy = build_content_strategy(
            self.opportunity("RESEARCH"),
            CommunityPolicy("r/example"),
            self.pain(),
        )
        self.assertEqual(strategy.format, "NO_CONTENT")
        self.assertEqual(strategy.mention_level, "NONE")
        self.assertFalse(strategy.link_allowed)

    def test_contribute_uses_answer_without_product_mention(self):
        strategy = build_content_strategy(
            self.opportunity("CONTRIBUTE"),
            CommunityPolicy("r/example", rules_checked=True),
            self.pain(),
        )
        self.assertEqual(strategy.format, "ANSWER")
        self.assertEqual(strategy.mention_level, "NONE")
        self.assertEqual(strategy.cta, "DISCUSS")

    def test_soft_mention_is_contextual_and_has_no_link(self):
        strategy = build_content_strategy(
            self.opportunity("SOFT_MENTION"),
            CommunityPolicy(
                "r/example",
                rules_checked=True,
                self_promotion_allowed=True,
                links_allowed=False,
                commercial_disclosure_required=True,
            ),
            self.pain(),
        )
        self.assertEqual(strategy.mention_level, "CONTEXTUAL")
        self.assertFalse(strategy.link_allowed)
        self.assertTrue(strategy.disclosure_required)

    def test_direct_promotion_requires_explicit_permissions(self):
        with self.assertRaises(ValueError):
            build_content_strategy(
                self.opportunity("DIRECT_PROMOTION", link_allowed=True),
                CommunityPolicy(
                    "r/example",
                    rules_checked=True,
                    self_promotion_allowed=True,
                    links_allowed=False,
                ),
                self.pain(),
            )

    def test_direct_promotion_is_transparent_and_human_approved(self):
        strategy = build_content_strategy(
            self.opportunity("DIRECT_PROMOTION", link_allowed=True),
            CommunityPolicy(
                "r/example",
                rules_checked=True,
                self_promotion_allowed=True,
                links_allowed=True,
                commercial_disclosure_required=True,
            ),
            self.pain(),
        )
        self.assertEqual(strategy.format, "PROMO_POST")
        self.assertEqual(strategy.mention_level, "DIRECT")
        self.assertEqual(strategy.cta, "VISIT_LINK")
        self.assertTrue(strategy.link_allowed)
        self.assertTrue(strategy.disclosure_required)
        self.assertTrue(strategy.human_approval_required)


if __name__ == "__main__":
    unittest.main()
