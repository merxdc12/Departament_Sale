"""Controlled post-validation business cycle.

The cycle creates internal drafts/plans and evaluates supplied first-party results.
It never publishes, spends, messages customers, or calls external APIs.
"""

from dataclasses import dataclass

from business_core import BusinessEvent, EventBus
from dashboard.kpi import build_kpi_dashboard
from learning.engine import learn_from_history
from learning.models import ExperimentMemory
from marketing.experiment import ExperimentResult, evaluate_experiment
from product_factory import ProductDraft, create_product_draft

from .coordinator import OpportunityWorkflowCoordinator, OpportunityWorkflowInput, OpportunityWorkflowResult


@dataclass(frozen=True)
class BusinessCycleInput:
    opportunity: OpportunityWorkflowInput
    human_approved: bool
    product_id: str
    product_name: str
    business_line: str
    niche_type: str = "EVERGREEN"
    channel: str = "ORGANIC_SOCIAL"
    target_segment: str = "validated audience"
    positioning: str = "evidence-led value proposition"
    observed_result: ExperimentResult | None = None
    prior_history: tuple[ExperimentMemory, ...] = ()


@dataclass(frozen=True)
class BusinessCycleResult:
    opportunity_result: OpportunityWorkflowResult
    product_draft: ProductDraft | None
    final_action: str
    external_execution_allowed: bool
    reason: str


class BusinessCycleCoordinator:
    def __init__(self, bus: EventBus) -> None:
        self.bus = bus

    def _emit(self, name: str, subject_id: str, payload: dict) -> None:
        self.bus.publish(BusinessEvent(name=name, source_department="workflow", subject_id=subject_id, payload=payload))

    def run(self, data: BusinessCycleInput) -> BusinessCycleResult:
        initial = OpportunityWorkflowCoordinator(self.bus).run(data.opportunity)
        if initial.stopped_at is not None or initial.economics is None:
            return BusinessCycleResult(initial, None, "STOP", False, initial.reason)

        self._emit("HUMAN_APPROVAL_REQUIRED", data.opportunity.opportunity_id, {"scope": "internal product draft and controlled test planning"})
        if not data.human_approved:
            return BusinessCycleResult(initial, None, "WAIT_APPROVAL", False, "Human approval is required before continuing.")
        self._emit("HUMAN_APPROVAL_GRANTED", data.opportunity.opportunity_id, {"external_execution_allowed": False})

        draft = create_product_draft(product_id=data.product_id, opportunity_id=data.opportunity.opportunity_id, name=data.product_name, business_line=data.business_line, market=data.opportunity.market, sale_price=data.opportunity.sale_price, human_approved=True)
        self._emit("PRODUCT_DRAFT_CREATED", draft.product_id, {"business_line": draft.business_line, "status": draft.status, "external_execution_allowed": False})
        self._emit("MARKETING_PLAN_READY", draft.product_id, {"channel": data.channel, "mode": "CONTROLLED_INTERNAL_PLAN", "external_execution_allowed": False})
        self._emit("SOCIAL_PLAN_READY", draft.product_id, {"channel": data.channel, "human_approval_required": True, "external_execution_allowed": False})
        self._emit("COMMUNITY_PLAN_READY", draft.product_id, {"mode": "RULES_FIRST", "human_approval_required": True, "external_execution_allowed": False})

        if data.observed_result is None:
            self._emit("ORCHESTRATOR_RECOMMENDATION", draft.product_id, {"action": "COLLECT_DATA", "reason": "No first-party performance observation supplied."})
            return BusinessCycleResult(initial, draft, "COLLECT_DATA", False, "Internal plans are ready; external execution remains disabled.")

        result = data.observed_result
        decision = evaluate_experiment(result)
        self._emit("PERFORMANCE_RECORDED", draft.product_id, {"visits": result.visits, "orders": result.orders, "revenue": result.revenue, "profit": result.profit, "source": "first_party_observation"})
        self._emit("EXPERIMENT_COMPLETED", draft.product_id, {"decision": decision, "conversion_rate": result.conversion_rate, "profit": result.profit})

        memory = ExperimentMemory(
            experiment_id=f"EXP-{draft.product_id}", product_id=draft.product_id, platform="INTERNAL", market=data.opportunity.market,
            niche_type=data.niche_type, channel=data.channel, target_segment=data.target_segment, positioning=data.positioning,
            visits=result.visits, orders=result.orders, revenue=result.revenue, profit=result.profit,
            outcome=decision if decision in ("STOP", "MODIFY", "SCALE") else "MODIFY",
            notes="First-party result evaluated by controlled business cycle.",
        )
        history = data.prior_history + (memory,)
        learning = learn_from_history(history, niche_type=data.niche_type, market=data.opportunity.market)
        dashboard = build_kpi_dashboard(history)
        self._emit("KPI_UPDATED", draft.product_id, {"experiments": dashboard.experiments, "orders": dashboard.orders, "revenue": dashboard.revenue, "profit": dashboard.profit, "conversion_rate": dashboard.conversion_rate})
        self._emit("MEMORY_UPDATED", draft.product_id, {"preferred_channels": learning.preferred_channels, "avoid_channels": learning.avoid_channels, "reason": learning.reason})
        self._emit("ORCHESTRATOR_RECOMMENDATION", draft.product_id, {"action": decision, "reason": "Recommendation only; any external execution requires a separate approval/action layer."})
        self._emit("WORKFLOW_COMPLETED", draft.product_id, {"action": decision, "external_execution_allowed": False})
        return BusinessCycleResult(initial, draft, decision, False, "Cycle evaluated and stored; no external action was executed.")
