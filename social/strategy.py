from .models import SocialPlan, SocialPolicy, SocialSignals

FORMATS = {
    "PINTEREST": ("VALUE_PIN", "PRODUCT_PIN"),
    "INSTAGRAM": ("REEL_OR_CAROUSEL", "REEL_OR_CAROUSEL"),
    "FACEBOOK": ("POST_OR_REEL", "POST_OR_REEL"),
    "THREADS": ("TEXT_THREAD", "TEXT_THREAD"),
    "TIKTOK": ("SHORT_VIDEO", "COMMERCIAL_SHORT_VIDEO"),
    "X": ("POST_OR_THREAD", "COMMERCIAL_POST_OR_THREAD"),
    "YOUTUBE": ("SHORT_OR_VIDEO", "COMMERCIAL_SHORT_OR_VIDEO"),
}


def _validate(signals: SocialSignals) -> None:
    for name, value in (("audience_fit", signals.audience_fit), ("content_fit", signals.content_fit), ("purchase_intent", signals.purchase_intent), ("engagement_fit", signals.engagement_fit)):
        if not 0 <= value <= 100:
            raise ValueError(f"{name} must be between 0 and 100")


def build_social_plan(policy: SocialPolicy, signals: SocialSignals, *, commercial: bool = False) -> SocialPlan:
    _validate(signals)
    score = round(signals.audience_fit * 0.35 + signals.content_fit * 0.30 + signals.purchase_intent * 0.20 + signals.engagement_fit * 0.15)
    if score < 45:
        return SocialPlan(policy.platform, "BLOCK", score, "NO_CONTENT", False, False, True, "Do not invest in this channel yet.", ("Channel fit is too weak.",))
    if score < 65:
        return SocialPlan(policy.platform, "RESEARCH", score, "RESEARCH", False, False, True, "Collect more audience and content evidence.", ("Evidence is not strong enough for a campaign.",))
    organic_format, commercial_format = FORMATS[policy.platform]
    if commercial:
        if not policy.commercial_content_allowed:
            return SocialPlan(policy.platform, "BLOCK", score, "NO_CONTENT", False, False, True, "Commercial content is not allowed by the active policy.", ("Policy blocks commercial content.",))
        return SocialPlan(policy.platform, "COMMERCIAL_CONTENT", score, commercial_format, policy.affiliate_links_allowed, policy.disclosure_required, policy.human_approval_required, "Run a transparent commercial content test.", ("Commercial relationship must be disclosed where required.", "No artificial engagement or account manipulation."))
    return SocialPlan(policy.platform, "ORGANIC_CONTENT", score, organic_format, False, False, policy.human_approval_required, "Build organic reach with useful platform-native content.", ("Start organic-first and measure performance before paid escalation.",))
