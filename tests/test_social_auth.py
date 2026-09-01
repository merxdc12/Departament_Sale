import os
import unittest
from unittest.mock import patch

from social.auth import ConnectorCredentials, load_credentials, require_credentials


class TestSocialAuth(unittest.TestCase):
    def test_missing_credentials_fail_closed(self):
        with self.assertRaises(RuntimeError):
            require_credentials(ConnectorCredentials("YOUTUBE", ""))

    def test_required_scope_is_enforced(self):
        credentials = ConnectorCredentials("PINTEREST", "token", scopes=("pins:read",))
        with self.assertRaises(RuntimeError):
            require_credentials(credentials, required_scopes=("pins:write",))

    def test_environment_loader_reads_token_account_and_scopes(self):
        env = {
            "YOUTUBE_ACCESS_TOKEN": "secret-token",
            "YOUTUBE_REFRESH_TOKEN": "refresh-token",
            "YOUTUBE_ACCOUNT_ID": "channel-123",
            "YOUTUBE_SCOPES": "youtube.readonly,youtube.upload",
        }
        with patch.dict(os.environ, env, clear=True):
            credentials = load_credentials("YOUTUBE")
        self.assertEqual(credentials.access_token, "secret-token")
        self.assertEqual(credentials.account_id, "channel-123")
        self.assertIn("youtube.upload", credentials.scopes)

    def test_tokens_are_not_required_as_source_code_constants(self):
        with patch.dict(os.environ, {}, clear=True):
            credentials = load_credentials("X")
        self.assertEqual(credentials.access_token, "")


if __name__ == "__main__":
    unittest.main()
