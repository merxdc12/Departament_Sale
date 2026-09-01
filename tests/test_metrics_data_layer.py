import unittest

from metrics import ChannelMetrics, ManualExportProvider, metrics_to_marketing_kpi, require_read_only_provider


class TestMetricsDataLayer(unittest.TestCase):
    def test_metrics_convert_to_marketing_kpi(self):
        metrics = ChannelMetrics("YOUTUBE", 1000, 100, 80, 4, 120.0, 20.0, "OFFICIAL_EXPORT", 0.9)
        kpi = metrics_to_marketing_kpi(metrics, channel_class="SOCIAL", experiments=3, risk=15)
        self.assertEqual(kpi.channel, "YOUTUBE")
        self.assertEqual(kpi.profit, 100.0)
        self.assertEqual(kpi.confidence, 0.9)

    def test_manual_export_provider_is_read_only(self):
        provider = ManualExportProvider(ChannelMetrics("PINTEREST", source_confidence=0.6))
        require_read_only_provider(provider)
        self.assertTrue(provider.read_only)

    def test_orders_cannot_exceed_visits(self):
        with self.assertRaises(ValueError):
            ChannelMetrics("INSTAGRAM", visits=2, orders=3)

    def test_invalid_confidence_fails_closed(self):
        with self.assertRaises(ValueError):
            ChannelMetrics("X", source_confidence=1.1)


if __name__ == "__main__":
    unittest.main()
