import unittest

from social.official_adapters import official_api_profile


class TestOfficialAPIProfiles(unittest.TestCase):
    def test_verified_platform_profiles(self):
        pinterest = official_api_profile("PINTEREST")
        self.assertEqual(pinterest.publish_endpoint, "/pins")
        self.assertEqual(pinterest.publish_scope, "pins:write")

        tiktok = official_api_profile("TIKTOK")
        self.assertEqual(tiktok.publish_endpoint, "/v2/post/publish/video/init/")
        self.assertEqual(tiktok.publish_scope, "video.publish")

        x = official_api_profile("X")
        self.assertEqual(x.publish_endpoint, "/2/tweets")

        youtube = official_api_profile("YOUTUBE")
        self.assertEqual(youtube.publish_endpoint, "/videos")
        self.assertIn("youtube.upload", youtube.publish_scope)

    def test_publishing_is_disabled_by_default(self):
        for platform in ("PINTEREST", "TIKTOK", "X", "YOUTUBE"):
            self.assertFalse(official_api_profile(platform).publishing_enabled_by_default)

    def test_unverified_profile_fails_closed(self):
        with self.assertRaises(RuntimeError):
            official_api_profile("INSTAGRAM")


if __name__ == "__main__":
    unittest.main()
