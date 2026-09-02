def _validate_score(name: str, value: int | float) -> None:
    if not 0 <= value <= 100:
        raise ValueError(f"{name} must be between 0 and 100. Received: {value}")


def opportunity_score(
    demand_score: int,
    competition_score: int,
    buyer_intent_score: int,
    trend_score: int,
) -> int:
    """Score market opportunity without double-counting business risk."""
    for name, value in (
        ("demand_score", demand_score),
        ("competition_score", competition_score),
        ("buyer_intent_score", buyer_intent_score),
        ("trend_score", trend_score),
    ):
        _validate_score(name, value)

    competition_advantage = 100 - competition_score
    score = (
        demand_score * 0.30
        + buyer_intent_score * 0.30
        + trend_score * 0.15
        + competition_advantage * 0.25
    )
    return round(score)
