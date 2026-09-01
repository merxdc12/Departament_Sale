import unittest

from community.models import CommunityPolicy, CommunitySignals
from community.reddit import analyze_reddit_opportunity


class TestRedditCommunityMarketing(unittest.TestCase):
    def strong_signals(self):
        return CommunitySignals(90, 85, 80, 75, 80)

    def test_rules_must_be_checked_first(self):
        result = analyze_reddit_opportunity(
            CommunityPolicy(community_name="r/example"),
            self.strong_signals(),
        )
        self.assertEqual(result.action, "RESEARCH")
        self.assertFalse(result.link_allowed)

    def test_no_self_promotion_means_contribute_only(self):
        result = analyze_reddit_opportunity(
            CommunityPolicy(
                community_name="r/example",
                rules_checked=True,
                self_promotion_allowed=False,
            ),
            self.strong_signals(),
        )
        self.assertEqual(result.action, "CONTRIBUTE")
        self.assertFalse(result.link_allowed)

    def test_direct_promotion_requires_rules_and_strong_fit(self):
        result = analyze_reddit_opportunity(
            CommunityPolicy(
                community_name="r/example",
                rules_checked=True,
                self_promotion_allowed=True,
                links_allowed=True,
            ),
            self.strong_signals(),
        )
        self.assertEqual(result.action, "DIRECT_PROMOTION")
        self.assertTrue(result.link_allowed)
        self.assertTrue(result.human_approval_required)

    def test_weak_fit_is_blocked(self):
        result = analyze_reddit_opportunity(
            CommunityPolicy(
                community_name="r/example",
                rules_checked=True,
                self_promotion_allowed=True,
                links_allowed=True,
            ),
            CommunitySignals(20, 20, 30, 10, 20),
        )
        self.assertEqual(result.action, "BLOCK")

    def test_invalid_signal_fails_closed(self):
        with self.assertRaises(ValueError):
            analyze_reddit_opportunity(
                CommunityPolicy(community_name="r/example", rules_checked=True),
                CommunitySignals(101, 50, 50, 50, 50),
            )


if __name__ == "__main__":
    unittest.main()
