from .models import MarketingInput, MarketingPlan, TestGuardrails
from .organic import organic_first_plan


def _validate(data: MarketingInput) -> None:
    e = data.economics
    if e.sale_price <= 0:
        raise ValueError("sale_price must be greater than zero")
    for name, value in (
        ("production_cost", e.production_cost),
        ("platform_fees", e.platform_fees),
        ("shipping_cost", e.shipping_cost),
        ("other_variable_cost", e.other_variable_cost),
        ("available_test_budget", data.available_test_budget),
    ):
        if value < 0:
            raise ValueError(f"{name} cannot be negative")
    if not data.target_segment.strip():
        raise ValueError("target_segment is required")
    if not data.positioning.strip():
        raise ValueError("positioning is required")


def build_marketing_plan(data: MarketingInput) -> MarketingPlan:
    """Build a controlled strategy. Organic validation is preferred before paid spend."""
    _validate(data)
    seo = data.seo.analysis
    margin = data.economics.contribution_margin
    margin_rate = data.economics.margin_rate

    base = dict(
        product_id=data.seo.product_id,
        platform=data.seo.platform,
        target_segment=data.target_segment.strip(),
        positioning=data.positioning.strip(),
        market=data.market,
        language=data.language,
        contribution_margin=margin,
        margin_rate=margin_rate,
        niche_type=data.niche_type,
    )

    if seo.decision == "REJECT":
        return MarketingPlan(**base, action="BLOCK", reasons=("SEO Decision Layer rejected this opportunity.", seo.reason))
    if seo.decision == "REVIEW":
        return MarketingPlan(**base, action="RESEARCH", reasons=("SEO evidence is not strong enough for a market test.", seo.reason))
    if margin <= 0:
        return MarketingPlan(**base, action="BLOCK", reasons=("Product has no positive contribution margin.",))

    if data.organic_first:
        organic = organic_first_plan(data.seo.platform)
        guardrails = TestGuardrails(
            duration_days=7,
            max_budget=0.0,
            target_visits=100,
            stop_conversion_below=0.01,
            scale_conversion_at_or_above=0.03,
            require_manual_approval=True,
        )
        return MarketingPlan(
            **base,
            action="ORGANIC_TEST",
            channels=organic.channels,
            guardrails=guardrails,
            reasons=(
                "SEO approved testing and unit economics are positive.",
                organic.reason,
                "Paid acquisition remains disabled until organic evidence is evaluated.",
            ),
        )

    if data.available_test_budget <= 0:
        return MarketingPlan(**base, action="RESEARCH", reasons=("Paid testing requested but no test budget is available.",))

    max_budget = round(min(data.available_test_budget, max(5.0, margin * 5)), 2)
    guardrails = TestGuardrails(
        duration_days=7,
        max_budget=max_budget,
        target_visits=100,
        stop_conversion_below=0.01,
        scale_conversion_at_or_above=0.03,
        require_manual_approval=True,
    )
    return MarketingPlan(
        **base,
        action="TEST",
        channels=data.preferred_channels,
        guardrails=guardrails,
        reasons=(
            "SEO approved a controlled test.",
            "Positive contribution margin supports limited experimentation.",
            "Manual approval remains required before external spend or publishing.",
        ),
    )
