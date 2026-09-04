"""Marketing/Sales Manager decision support layer."""

from .manager import build_marketing_plan
from .models import MarketingInput, MarketingPlan, ProductEconomics

__all__ = ["MarketingInput", "MarketingPlan", "ProductEconomics", "build_marketing_plan"]
