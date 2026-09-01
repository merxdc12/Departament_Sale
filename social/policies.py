from .models import SocialPlatform, SocialPolicy


def policy_for(platform: SocialPlatform) -> SocialPolicy:
    if platform == "PINTEREST":
        return SocialPolicy(platform, True, True, True, True, False, True)
    if platform in ("INSTAGRAM", "FACEBOOK", "THREADS", "TIKTOK", "X", "YOUTUBE"):
        return SocialPolicy(
            platform=platform,
            commercial_content_allowed=True,
            affiliate_links_allowed=False,
            disclosure_required=True,
            official_api_only=True,
            automation_allowed=False,
            human_approval_required=True,
        )
    raise ValueError(f"Unsupported platform: {platform}")
