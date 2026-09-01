from dataclasses import dataclass

from learning.models import ExperimentMemory


@dataclass(frozen=True)
class KPIDashboard:
    experiments: int
    visits: int
    orders: int
    revenue: float
    profit: float
    conversion_rate: float
    profitable_experiments: int
    scale_decisions: int
    stop_decisions: int


def build_kpi_dashboard(history: tuple[ExperimentMemory, ...]) -> KPIDashboard:
    experiments = len(history)
    visits = sum(x.visits for x in history)
    orders = sum(x.orders for x in history)
    revenue = round(sum(x.revenue for x in history), 2)
    profit = round(sum(x.profit for x in history), 2)
    conversion = round(orders / visits, 4) if visits else 0.0
    return KPIDashboard(
        experiments=experiments,
        visits=visits,
        orders=orders,
        revenue=revenue,
        profit=profit,
        conversion_rate=conversion,
        profitable_experiments=sum(1 for x in history if x.profit > 0),
        scale_decisions=sum(1 for x in history if x.outcome == "SCALE"),
        stop_decisions=sum(1 for x in history if x.outcome == "STOP"),
    )
