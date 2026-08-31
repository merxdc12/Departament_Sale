from learning.engine import learn_from_history
from marketing.manager import build_marketing_plan
from marketing.niche import classify_niche

from .models import OrchestratorInput, OrchestratorResult


def orchestrate(data: OrchestratorInput) -> OrchestratorResult:
    """Coordinate deterministic business layers without bypassing their gates."""
    niche_type = classify_niche(data.niche_signals)
    learning = learn_from_history(
        data.history,
        niche_type=niche_type,
        market=data.marketing.market,
    )
    plan = build_marketing_plan(data.marketing)

    action = plan.action
    reason = plan.reasons[0] if plan.reasons else "Marketing plan prepared."

    # Learning may advise channel selection, but cannot override SEO/IP/economics blocks.
    if action in ("ORGANIC_TEST", "TEST") and learning.preferred_channels:
        reason = (
            f"{reason} First-party memory prefers: "
            + ", ".join(learning.preferred_channels)
            + "."
        )
    if action in ("ORGANIC_TEST", "TEST") and learning.avoid_channels:
        reason += " Avoid proven losing channels: " + ", ".join(learning.avoid_channels) + "."

    return OrchestratorResult(
        product_id=plan.product_id,
        niche_type=niche_type,
        marketing_plan=plan,
        learning=learning,
        action=action,
        reason=reason,
    )
