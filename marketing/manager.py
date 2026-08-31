from .models import MarketingInput, MarketingPlan, TestGuardrails


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
    """Translate approved SEO intelligence and unit economics into a controlled plan.

    This manager does not publish listings, buy ads, or scale campaigns. It only
    prepares a strategy contract with conservative experiment guardrails.
    """
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
    )

    if seo.decision == "REJECT":
        return MarketingPlan(
            **base,
            action="BLOCK",
            reasons=("SEO Decision Layer rejected this opportunity.", seo.reason),
        )

    if seo.decision == "REVIEW":
        return MarketingPlan(
            **base,
            action="RESEARCH",
            reasons=("SEO evidence is not strong enough for a market test.", seo.reason),
        )

    if margin <= 0:
        return MarketingPlan(
            **base,
            action="BLOCK",
            reasons=("Product has no positive contribution margin.",),
        )

    if data.available_test_budget <= 0:
        return MarketingPlan(
            **base,
            action="RESEARCH",
            reasons=("SEO supports testing, but no test budget is available.",),
        )

    # v0.7 defaults are experiment guardrails, not autonomous spending authority.
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
            "SEO Decision Layer approved a controlled test.",
            "Positive contribution margin supports limited experimentation.",
            "Manual approval remains required before external spend or publishing.",
        ),
    )
