import unittest

from social import SocialSignals, build_social_plan, policy_for


class TestSocialChannels(unittest.TestCase):
    def strong(self):
        return SocialSignals(90, 85, 75, 80)

    def test_pinterest_commercial_plan_allows_affiliate_link_with_disclosure(self):
        plan = build_social_plan(policy_for("PINTEREST"), self.strong(), commercial=True)
        self.assertEqual(plan.action, "COMMERCIAL_CONTENT")
        self.assertEqual(plan.content_format, "PRODUCT_PIN")
        self.assertTrue(plan.link_allowed)
        self.assertTrue(plan.disclosure_required)

    def test_instagram_commercial_plan_requires_disclosure(self):
        plan = build_social_plan(policy_for("INSTAGRAM"), self.strong(), commercial=True)
        self.assertEqual(plan.content_format, "REEL_OR_CAROUSEL")
        self.assertTrue(plan.disclosure_required)
        self.assertFalse(plan.link_allowed)

    def test_threads_organic_plan_uses_text_thread(self):
        plan = build_social_plan(policy_for("THREADS"), self.strong())
        self.assertEqual(plan.action, "ORGANIC_CONTENT")
        self.assertEqual(plan.content_format, "TEXT_THREAD")

    def test_facebook_organic_plan_uses_post_or_reel(self):
        plan = build_social_plan(policy_for("FACEBOOK"), self.strong())
        self.assertEqual(plan.content_format, "POST_OR_REEL")
        self.assertTrue(plan.human_approval_required)

    def test_weak_channel_is_blocked(self):
        signals = SocialSignals(20, 30, 10, 20)
        plan = build_social_plan(policy_for("PINTEREST"), signals)
        self.assertEqual(plan.action, "BLOCK")

    def test_invalid_signal_fails_closed(self):
        with self.assertRaises(ValueError):
            build_social_plan(policy_for("INSTAGRAM"), SocialSignals(101, 50, 50, 50))


if __name__ == "__main__":
    unittest.main()
