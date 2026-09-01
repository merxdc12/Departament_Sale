import os
from dataclasses import dataclass
from typing import Mapping

from .models import SocialPlatform


@dataclass(frozen=True)
class ConnectorCredentials:
    platform: SocialPlatform
    access_token: str
    account_id: str = ""
    refresh_token: str = ""
    scopes: tuple[str, ...] = ()

    @property
    def configured(self) -> bool:
        return bool(self.access_token.strip())


ENV_PREFIXES: Mapping[SocialPlatform, str] = {
    "PINTEREST": "PINTEREST",
    "THREADS": "THREADS",
    "INSTAGRAM": "INSTAGRAM",
    "FACEBOOK": "FACEBOOK",
    "TIKTOK": "TIKTOK",
    "X": "X",
    "YOUTUBE": "YOUTUBE",
}


def load_credentials(platform: SocialPlatform) -> ConnectorCredentials:
    prefix = ENV_PREFIXES[platform]
    scopes_raw = os.getenv(f"{prefix}_SCOPES", "")
    scopes = tuple(s.strip() for s in scopes_raw.split(",") if s.strip())
    return ConnectorCredentials(
        platform=platform,
        access_token=os.getenv(f"{prefix}_ACCESS_TOKEN", ""),
        refresh_token=os.getenv(f"{prefix}_REFRESH_TOKEN", ""),
        account_id=os.getenv(f"{prefix}_ACCOUNT_ID", ""),
        scopes=scopes,
    )


def require_credentials(credentials: ConnectorCredentials, *, required_scopes: tuple[str, ...] = ()) -> None:
    if not credentials.configured:
        raise RuntimeError(f"REVIEW: {credentials.platform} credentials are not configured")
    missing = tuple(scope for scope in required_scopes if scope not in credentials.scopes)
    if missing:
        raise RuntimeError(f"REVIEW: missing required scopes: {', '.join(missing)}")
