from dataclasses import dataclass
from typing import Literal

from .models import SocialPlatform

AuthKind = Literal["OAUTH2", "USER_ACCESS_TOKEN"]


@dataclass(frozen=True)
class OfficialAPIProfile:
    platform: SocialPlatform
    api_base: str
    publish_endpoint: str
    auth_kind: AuthKind
    publish_scope: str
    supports_direct_publish: bool
    requires_app_review_or_audit: bool = True
    publishing_enabled_by_default: bool = False


OFFICIAL_API_PROFILES: dict[SocialPlatform, OfficialAPIProfile] = {
    "PINTEREST": OfficialAPIProfile(
        platform="PINTEREST",
        api_base="https://api.pinterest.com/v5",
        publish_endpoint="/pins",
        auth_kind="OAUTH2",
        publish_scope="pins:write",
        supports_direct_publish=True,
    ),
    "TIKTOK": OfficialAPIProfile(
        platform="TIKTOK",
        api_base="https://open.tiktokapis.com",
        publish_endpoint="/v2/post/publish/video/init/",
        auth_kind="OAUTH2",
        publish_scope="video.publish",
        supports_direct_publish=True,
    ),
    "X": OfficialAPIProfile(
        platform="X",
        api_base="https://api.x.com",
        publish_endpoint="/2/tweets",
        auth_kind="USER_ACCESS_TOKEN",
        publish_scope="tweet.write",
        supports_direct_publish=True,
    ),
    "YOUTUBE": OfficialAPIProfile(
        platform="YOUTUBE",
        api_base="https://www.googleapis.com/upload/youtube/v3",
        publish_endpoint="/videos",
        auth_kind="OAUTH2",
        publish_scope="https://www.googleapis.com/auth/youtube.upload",
        supports_direct_publish=True,
    ),
}


def official_api_profile(platform: SocialPlatform) -> OfficialAPIProfile:
    try:
        return OFFICIAL_API_PROFILES[platform]
    except KeyError as exc:
        raise RuntimeError(f"REVIEW: no verified official publish adapter registered for {platform}") from exc
