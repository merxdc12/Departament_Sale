from marketing.channel_portfolio import ChannelClass, MarketingChannelKPI

from .models import ChannelMetrics


def metrics_to_marketing_kpi(
    metrics: ChannelMetrics,
    *,
    channel_class: ChannelClass,
    experiments: int = 0,
    risk: int = 20,
) -> MarketingChannelKPI:
    """Convert verified/imported metrics to the Marketing Manager contract.

    Confidence is inherited from the data source rather than invented from missing
    platform metrics. A connector/export with incomplete evidence should provide a
    lower source_confidence value.
    """
    return MarketingChannelKPI(
        channel=metrics.channel,
        channel_class=channel_class,
        experiments=experiments,
        visits=metrics.visits,
        orders=metrics.orders,
        revenue=metrics.revenue,
        profit=metrics.profit,
        confidence=metrics.source_confidence,
        risk=risk,
    )
