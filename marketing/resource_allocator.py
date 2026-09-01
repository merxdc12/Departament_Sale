from dataclasses import dataclass

from .channel_portfolio import MarketingChannelRow


@dataclass(frozen=True)
class ChannelAllocation:
    channel: str
    attention_share: float
    paid_budget: float
    mode: str
    reason: str


def allocate_channel_resources(
    portfolio: tuple[MarketingChannelRow, ...],
    *,
    paid_budget: float = 0.0,
) -> tuple[ChannelAllocation, ...]:
    """Allocate attention first; paid budget only to evidence-backed winners."""
    if paid_budget < 0:
        raise ValueError("paid_budget cannot be negative")
    active = tuple(x for x in portfolio if x.decision != "AVOID")
    if not active:
        return ()

    weights = []
    for row in active:
        if row.decision == "SCALE":
            weight = max(row.priority_score, 1.0) * 1.5
        elif row.decision == "PREFER":
            weight = max(row.priority_score, 1.0)
        elif row.decision == "RETEST":
            weight = max(row.priority_score, 1.0) * 0.5
        else:  # RESEARCH
            weight = 10.0
        weights.append((row, weight))

    total_weight = sum(x[1] for x in weights)
    paid_candidates = tuple(row for row, _ in weights if row.decision == "SCALE" and row.profit > 0 and row.confidence >= 0.6)
    paid_weight = sum(max(row.priority_score, 1.0) for row in paid_candidates)

    allocations = []
    for row, weight in weights:
        attention = round(weight / total_weight, 4) if total_weight else 0.0
        if row in paid_candidates and paid_budget > 0 and paid_weight:
            budget = round(paid_budget * max(row.priority_score, 1.0) / paid_weight, 2)
            mode = "PAID_SCALE"
            reason = "Profitable, sufficiently confident SCALE channel; eligible for controlled paid expansion."
        else:
            budget = 0.0
            mode = "ORGANIC"
            reason = "Organic-first: collect or strengthen evidence before paid spend."
        allocations.append(ChannelAllocation(row.channel, attention, budget, mode, reason))
    return tuple(allocations)
