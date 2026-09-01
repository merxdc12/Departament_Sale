"""Deterministic product unit economics; no payments or external actions."""

from dataclasses import dataclass
from math import ceil


@dataclass(frozen=True)
class UnitEconomics:
    sale_price: float
    variable_cost: float
    contribution_margin: float
    margin_rate: float
    break_even_orders: int | None
    profitable: bool


def calculate_unit_economics(*, sale_price: float, production_cost: float, platform_fees: float = 0.0, payment_fees: float = 0.0, shipping_cost: float = 0.0, advertising_cost_per_order: float = 0.0, expected_refund_cost_per_order: float = 0.0, packaging_cost: float = 0.0, other_variable_cost: float = 0.0, fixed_test_cost: float = 0.0) -> UnitEconomics:
    costs = (production_cost, platform_fees, payment_fees, shipping_cost, advertising_cost_per_order, expected_refund_cost_per_order, packaging_cost, other_variable_cost, fixed_test_cost)
    if sale_price <= 0 or any(value < 0 for value in costs):
        raise ValueError("sale price must be positive and costs cannot be negative")
    variable_cost = round(sum(costs[:-1]), 2)
    margin = round(sale_price - variable_cost, 2)
    margin_rate = round(margin / sale_price, 4)
    break_even = ceil(fixed_test_cost / margin) if fixed_test_cost > 0 and margin > 0 else (0 if fixed_test_cost == 0 and margin > 0 else None)
    return UnitEconomics(sale_price, variable_cost, margin, margin_rate, break_even, margin > 0)
