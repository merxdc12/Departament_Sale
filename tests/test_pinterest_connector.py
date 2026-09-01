import unittest

from social.auth import ConnectorCredentials
from social.connectors import PublishRequest
from social.pinterest_connector import PinterestConnector


class FakeTransport:
    def __init__(self, status=200, payload=None):
        self.status = status
        self.payload = payload or {}
        self.calls = []

    def request(self, method, url, *, headers, body=None):
        self.calls.append((method, url, headers, body))
        return self.status, self.payload


class TestPinterestConnector(unittest.TestCase):
    def _creds(self):
        return ConnectorCredentials(
            platform="PINTEREST",
            access_token="token",
            scopes=("boards:read", "pins:read", "pins:write"),
        )

    def test_publish_disabled_by_default(self):
        connector = PinterestConnector(self._creds(), "123", FakeTransport(status=201, payload={"id": "42"}))
        req = PublishRequest("PINTEREST", "PRODUCT_PIN", "Test", ("https://example.com/pin.jpg",), human_approved=True)
        with self.assertRaises(RuntimeError):
            connector.publish(req)

    def test_human_approval_required(self):
        connector = PinterestConnector(self._creds(), "123", FakeTransport(status=201, payload={"id": "42"}), publishing_enabled=True)
        req = PublishRequest("PINTEREST", "PRODUCT_PIN", "Test", ("https://example.com/pin.jpg",), human_approved=False)
        with self.assertRaises(RuntimeError):
            connector.publish(req)

    def test_publish_uses_official_v5_pins_endpoint(self):
        transport = FakeTransport(status=201, payload={"id": "42"})
        connector = PinterestConnector(self._creds(), "123", transport, publishing_enabled=True)
        req = PublishRequest("PINTEREST", "PRODUCT_PIN", "Test description", ("https://example.com/pin.jpg",), link="https://shop.example.com", human_approved=True)
        result = connector.publish(req)
        self.assertEqual(result.external_id, "42")
        method, url, _, body = transport.calls[0]
        self.assertEqual(method, "POST")
        self.assertEqual(url, "https://api.pinterest.com/v5/pins")
        self.assertEqual(body["board_id"], "123")
        self.assertEqual(body["media_source"]["source_type"], "image_url")

    def test_metrics_are_normalized_from_pin_metrics(self):
        transport = FakeTransport(status=200, payload={"items": [
            {"pin_metrics": {"lifetime_metrics": {"IMPRESSION": 100, "OUTBOUND_CLICK": 5}}},
            {"pin_metrics": {"lifetime_metrics": {"IMPRESSION": 50, "OUTBOUND_CLICK": 2}}},
        ]})
        connector = PinterestConnector(self._creds(), "123", transport)
        metrics = connector.fetch_metrics()
        self.assertEqual(metrics.impressions, 150)
        self.assertEqual(metrics.clicks, 7)
        self.assertEqual(metrics.channel, "PINTEREST")

    def test_non_https_image_is_rejected(self):
        connector = PinterestConnector(self._creds(), "123", FakeTransport(status=201), publishing_enabled=True)
        req = PublishRequest("PINTEREST", "PRODUCT_PIN", "Test", ("http://example.com/pin.jpg",), human_approved=True)
        with self.assertRaises(ValueError):
            connector.publish(req)


if __name__ == "__main__":
    unittest.main()
