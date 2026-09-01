"""Controlled workflow coordinator for cross-department business decisions.

This coordinator only invokes deterministic internal analysis. It does not publish
content, spend money, contact customers, create accounts, or bypass approval gates.
"""

from dataclasses import dataclass

from business_core import EventBus, OpportunitySignals, RiskAssessment
from business_core.integrations import (
    publish_competitor_analysis,
    publish_opportunity,
    publish_product_validation,
    publish_unit_economics,
)
from business_intelligence import (
    CompetitorSnapshot,
    ProductValidation,
    analyze_competitors,
    discover_opportunity,
    validate_product,
)
from economics import UnitEconomics, calculate_unit_economics


@dataclass(frozen=True)
class OpportunityWorkflowInput:
    opportunity_id: str
    problem: str
    market: str
    signals: OpportunitySignals
    possible_business_lines: tuple[str, ...]
    competitors: tuple[CompetitorSnapshot, ...]
    risk: RiskAssessment
    sale_price: float
    production_cost: float
    platform_fees: float = 0.0
    payment_fees: float = 0.0
    shipping_cost: float = 0.0
    advertising_cost_per_order: float = 0.0
    expected_refund_cost_per_order: float = 0.0
    packaging_cost: float = 0.0
    other_variable_cost: float = 0.0
    fixed_test_cost: float = 0.0


@dataclass(frozen=True)
class OpportunityWorkflowResult:
    opportunity_id: str
    validation: ProductValidation
    economics: UnitEconomics | None
    stopped_at: str | None
    reason: str


class OpportunityWorkflowCoordinator:
    """Run opportunity -> competition -> validation -> economics in order."""

    def __init__(self, bus: EventBus) -> None:
        self.bus = bus

    def run(self, data: OpportunityWorkflowInput) -> OpportunityWorkflowResult:
        opportunity = discover_opportunity(
            opportunity_id=data.opportunity_id,
            problem=data.problem,
            market=data.market,
            signals=data.signals,
            possible_business_lines=data.possible_business_lines,
        )
        publish_opportunity(self.bus, opportunity)

        competitors = analyze_competitors(data.competitors)
        publish_competitor_analysis(self.bus, competitors, subject_id=data.opportunity_id)

        validation = validate_product(opportunity, competitors, data.risk)
        publish_product_validation(self.bus, validation)

        if validation.decision == "REJECT":
            return OpportunityWorkflowResult(
                data.opportunity_id,
                validation,
                None,
                "PRODUCT_VALIDATION",
                validation.reason,
            )

        if validation.decision == "HOLD":
            return OpportunityWorkflowResult(
                data.opportunity_id,
                validation,
                None,
                "EVIDENCE_GATE",
                validation.reason,
            )

        economics = calculate_unit_economics(
            sale_price=data.sale_price,
            production_cost=data.production_cost,
            platform_fees=data.platform_fees,
            payment_fees=data.payment_fees,
            shipping_cost=data.shipping_cost,
            advertising_cost_per_order=data.advertising_cost_per_order,
            expected_refund_cost_per_order=data.expected_refund_cost_per_order,
            packaging_cost=data.packaging_cost,
            other_variable_cost=data.other_variable_cost,
            fixed_test_cost=data.fixed_test_cost,
        )
        publish_unit_economics(self.bus, economics, subject_id=data.opportunity_id)

        if not economics.profitable:
            return OpportunityWorkflowResult(
                data.opportunity_id,
                validation,
                economics,
                "ECONOMICS_GATE",
                "Unit economics are not profitable; do not proceed to market testing.",
            )

        return OpportunityWorkflowResult(
            data.opportunity_id,
            validation,
            economics,
            None,
            "Internal analysis passed. Human approval is still required before external execution.",
        )
