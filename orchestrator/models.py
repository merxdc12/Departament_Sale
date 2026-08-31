from dataclasses import dataclass, field
from typing import Literal

from learning.models import ExperimentMemory, LearningRecommendation
from marketing.models import MarketingInput, MarketingPlan
from marketing.niche import NicheSignals, NicheType

OrchestratorAction = Literal["BLOCK", "RESEARCH", "ORGANIC_TEST", "TEST", "STOP", "MODIFY", "SCALE"]


@dataclass(frozen=True)
class OrchestratorInput:
    marketing: MarketingInput
    niche_signals: NicheSignals
    history: tuple[ExperimentMemory, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class OrchestratorResult:
    product_id: str
    niche_type: NicheType
    marketing_plan: MarketingPlan
    learning: LearningRecommendation
    action: OrchestratorAction
    reason: str
