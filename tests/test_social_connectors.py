import unittest

from metrics.models import ChannelMetrics
from social.connectors import PublishRequest, PublishResult, require_publish_permission, require_safe_connector


class FakeConnector:
    def __init__(self, platform="INSTAGRAM", official=True, publishing_enabled=False):
        self.platform = platform
        self.official = official
        self.read_only = not publishing_enabled
        self.publishing_enabled = publishing_enabled

    def fetch_metrics(self):
        return ChannelMetrics(self.platform, source="FAKE", source_confidence=1.0)

    def publish(self, request):
        require_publish_permission(self, request)
        return PublishResult(self.platform, "PUBLISHED", external_id="1")


class TestSocialConnectors(unittest.TestCase):
    def test_unofficial_connector_is_blocked(self):
        with self.assertRaises(RuntimeError):
            require_safe_connector(FakeConnector(official=False))

    def test_publish_requires_enabled_connector(self):
        connector = FakeConnector(publishing_enabled=False)
        request = PublishRequest("INSTAGRAM", "REEL", "hello", human_approved=True)
        with self.assertRaises(RuntimeError):
            require_publish_permission(connector, request)

    def test_publish_requires_human_approval(self):
        connector = FakeConnector(publishing_enabled=True)
        request = PublishRequest("INSTAGRAM", "REEL", "hello")
        with self.assertRaises(RuntimeError):
            require_publish_permission(connector, request)

    def test_approved_official_publish_can_pass_gate(self):
        connector = FakeConnector(publishing_enabled=True)
        request = PublishRequest("INSTAGRAM", "REEL", "hello", human_approved=True)
        result = connector.publish(request)
        self.assertEqual(result.status, "PUBLISHED")

    def test_cross_platform_request_is_rejected(self):
        connector = FakeConnector(platform="FACEBOOK", publishing_enabled=True)
        request = PublishRequest("INSTAGRAM", "REEL", "hello", human_approved=True)
        with self.assertRaises(ValueError):
            require_publish_permission(connector, request)


if __name__ == "__main__":
    unittest.main()
