import unittest

from marketing.channel_portfolio import BASE_CHANNELS, MarketingChannelKPI, build_marketing_channel_portfolio


class TestMarketingChannelPortfolio(unittest.TestCase):
    def test_base_contains_full_marketing_core(self):
        names = {x[0] for x in BASE_CHANNELS}
        self.assertTrue({"GOOGLE_SEO", "PINTEREST", "INSTAGRAM", "FACEBOOK", "THREADS", "TIKTOK", "YOUTUBE", "X", "REDDIT", "EMAIL", "OWN_WEBSITE"}.issubset(names))

    def test_profitable_confident_channel_ranks_above_loser(self):
        rows = build_marketing_channel_portfolio((
            MarketingChannelKPI("YOUTUBE", "SOCIAL", 5, 500, 25, 500.0, 100.0, 1.0, 20),
            MarketingChannelKPI("X", "SOCIAL", 5, 500, 1, 20.0, -30.0, 1.0, 20),
        ))
        self.assertEqual(rows[0].channel, "YOUTUBE")
        self.assertEqual(rows[0].decision, "SCALE")
        self.assertEqual(rows[1].decision, "AVOID")

    def test_low_confidence_requires_research(self):
        row = build_marketing_channel_portfolio((MarketingChannelKPI("REDDIT", "COMMUNITY", 1, 50, 2, 20.0, 10.0, 0.2, 30),))[0]
        self.assertEqual(row.decision, "RESEARCH")

    def test_owned_channels_supported(self):
        rows = build_marketing_channel_portfolio((
            MarketingChannelKPI("EMAIL", "OWNED", 3, 200, 12, 200.0, 100.0, 0.8, 10),
            MarketingChannelKPI("OWN_WEBSITE", "OWNED", 3, 300, 9, 180.0, 80.0, 0.8, 10),
        ))
        self.assertEqual({x.channel_class for x in rows}, {"OWNED"})


if __name__ == "__main__":
    unittest.main()
