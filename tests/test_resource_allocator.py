import unittest

from marketing.channel_portfolio import MarketingChannelKPI, build_marketing_channel_portfolio
from marketing.resource_allocator import allocate_channel_resources


class TestResourceAllocator(unittest.TestCase):
    def test_paid_budget_only_goes_to_proven_scale_channels(self):
        portfolio = build_marketing_channel_portfolio((
            MarketingChannelKPI("YOUTUBE", "SOCIAL", 5, 500, 25, 500, 100, 1.0, 20),
            MarketingChannelKPI("TIKTOK", "SOCIAL", 1, 50, 2, 30, 10, 0.2, 20),
        ))
        allocations = allocate_channel_resources(portfolio, paid_budget=100)
        by_channel = {x.channel: x for x in allocations}
        self.assertEqual(by_channel["YOUTUBE"].mode, "PAID_SCALE")
        self.assertEqual(by_channel["YOUTUBE"].paid_budget, 100.0)
        self.assertEqual(by_channel["TIKTOK"].paid_budget, 0.0)

    def test_zero_budget_keeps_everything_organic(self):
        portfolio = build_marketing_channel_portfolio((
            MarketingChannelKPI("PINTEREST", "SOCIAL", 5, 500, 25, 500, 100, 1.0, 20),
        ))
        allocation = allocate_channel_resources(portfolio)[0]
        self.assertEqual(allocation.mode, "ORGANIC")
        self.assertEqual(allocation.paid_budget, 0.0)

    def test_avoid_channels_receive_no_resources(self):
        portfolio = build_marketing_channel_portfolio((
            MarketingChannelKPI("X", "SOCIAL", 5, 500, 1, 20, -30, 1.0, 20),
            MarketingChannelKPI("EMAIL", "OWNED", 3, 200, 12, 200, 100, 0.8, 10),
        ))
        allocations = allocate_channel_resources(portfolio)
        self.assertNotIn("X", {x.channel for x in allocations})

    def test_attention_shares_sum_to_one(self):
        portfolio = build_marketing_channel_portfolio((
            MarketingChannelKPI("EMAIL", "OWNED", 3, 200, 12, 200, 100, 0.8, 10),
            MarketingChannelKPI("OWN_WEBSITE", "OWNED", 3, 300, 9, 180, 80, 0.8, 10),
        ))
        allocations = allocate_channel_resources(portfolio)
        self.assertAlmostEqual(sum(x.attention_share for x in allocations), 1.0, places=3)


if __name__ == "__main__":
    unittest.main()
