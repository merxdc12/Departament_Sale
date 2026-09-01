import unittest

from social.memory import SocialLearning
from social.models import SocialSignals
from social.policies import policy_for
from social.portfolio import build_channel_portfolio
from social.strategy import build_social_plan


class TestExtendedSocialChannels(unittest.TestCase):
    def test_native_formats(self):
        expected = {"TIKTOK": "SHORT_VIDEO", "X": "POST_OR_THREAD", "YOUTUBE": "SHORT_OR_VIDEO"}
        signals = SocialSignals(90, 90, 70, 80)
        for platform, content_format in expected.items():
            with self.subTest(platform=platform):
                plan = build_social_plan(policy_for(platform), signals)
                self.assertEqual(plan.action, "ORGANIC_CONTENT")
                self.assertEqual(plan.content_format, content_format)
                self.assertTrue(plan.human_approval_required)

    def test_commercial_content_requires_disclosure(self):
        signals = SocialSignals(90, 90, 80, 80)
        for platform in ("TIKTOK", "X", "YOUTUBE"):
            plan = build_social_plan(policy_for(platform), signals, commercial=True)
            self.assertTrue(plan.disclosure_required)
            self.assertFalse(plan.link_allowed)

    def test_portfolio_ranks_business_outcomes(self):
        rows = build_channel_portfolio((
            SocialLearning("PINTEREST", "VALUE_PIN", 3, 300, 12, 80.0, 0.04, "PREFER"),
            SocialLearning("TIKTOK", "SHORT_VIDEO", 3, 300, 6, 20.0, 0.02, "RETEST"),
            SocialLearning("YOUTUBE", "SHORT_OR_VIDEO", 1, 100, 5, 40.0, 0.05, "INSUFFICIENT_DATA"),
        ))
        self.assertEqual(rows[0].channel, "PINTEREST")
        self.assertGreater(rows[0].priority_score, rows[-1].priority_score)

    def test_invalid_risk_fails_closed(self):
        learning = SocialLearning("X", "POST_OR_THREAD", 2, 200, 4, 10.0, 0.02, "RETEST")
        with self.assertRaises(ValueError):
            build_channel_portfolio((learning,), risks={"X": 101})


if __name__ == "__main__":
    unittest.main()
