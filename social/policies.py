from .models import SocialPlatform, SocialPolicy


def policy_for(platform: SocialPlatform) -> SocialPolicy:
    if platform == "PINTEREST":
        return SocialPolicy(
            platform=platform,
            commercial_content_allowed=True,
            affiliate_links_allowed=True,
            disclosure_required=True,
            official_api_only=True,
            automation_allowed=False,
            human_approval_required=True,
        )
    if platform in ("INSTAGRAM", "FACEBOOK", "THREADS"):
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
