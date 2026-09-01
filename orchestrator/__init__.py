"""Business orchestration layer for Departament_Sale."""

from .engine import orchestrate
from .models import OrchestratorInput, OrchestratorResult

__all__ = ["OrchestratorInput", "OrchestratorResult", "orchestrate"]
