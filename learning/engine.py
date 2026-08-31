from collections import defaultdict

from .models import ExperimentMemory, LearnedPattern, LearningRecommendation


def learn_from_history(
    history: tuple[ExperimentMemory, ...],
    *,
    niche_type,
    market: str,
    min_experiments: int = 2,
) -> LearningRecommendation:
    """Aggregate first-party experiment history into deterministic channel guidance.

    The learning layer does not invent missing results. Only stored experiments for
    the requested niche type and market participate in the recommendation.
    """
    relevant = [x for x in history if x.niche_type == niche_type and x.market == market]
    groups = defaultdict(list)
    for item in relevant:
        groups[item.channel].append(item)

    patterns = []
    for channel, items in groups.items():
        experiments = len(items)
        visits = sum(x.visits for x in items)
        orders = sum(x.orders for x in items)
        profit = round(sum(x.profit for x in items), 2)
        conversion = orders / visits if visits else 0.0
        avg_profit = profit / experiments if experiments else 0.0

        # Profit is primary; conversion is a secondary quality signal.
        score = round(avg_profit + conversion * 100, 2)
        patterns.append(
            LearnedPattern(
                niche_type=niche_type,
                channel=channel,
                experiments=experiments,
                total_visits=visits,
                total_orders=orders,
                total_profit=profit,
                conversion_rate=round(conversion, 4),
                average_profit_per_experiment=round(avg_profit, 2),
                score=score,
            )
        )

    patterns.sort(key=lambda x: (x.score, x.total_profit), reverse=True)
    trusted = [p for p in patterns if p.experiments >= min_experiments]
    preferred = tuple(p.channel for p in trusted if p.total_profit > 0)
    avoid = tuple(p.channel for p in trusted if p.total_profit < 0)

    if not trusted:
        reason = "Not enough first-party experiment history; keep collecting organic test data."
    elif preferred:
        reason = "Prioritize channels with repeated positive first-party profit and conversion evidence."
    else:
        reason = "No repeatedly profitable channel is proven yet; continue controlled organic experiments."

    return LearningRecommendation(preferred, avoid, tuple(patterns), reason)
