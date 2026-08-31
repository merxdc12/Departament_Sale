from dataclasses import dataclass
from .models import ConfidenceLevel


@dataclass(frozen=True)
class SEOConfidence:
    score: float
    level: ConfidenceLevel
    missing_sources: tuple[str, ...]


def calculate_confidence(
    *,
    has_search_data: bool,
    has_competitor_data: bool,
    has_trend_data: bool,
    has_price_data: bool,
    has_sales_data: bool,
) -> SEOConfidence:
    weights = {
        "search_data": 0.30,
        "competitor_data": 0.20,
        "trend_data": 0.15,
        "price_data": 0.15,
        "sales_data": 0.20,
    }
    availability = {
        "search_data": has_search_data,
        "competitor_data": has_competitor_data,
        "trend_data": has_trend_data,
        "price_data": has_price_data,
        "sales_data": has_sales_data,
    }
    score = round(sum(weights[k] for k, present in availability.items() if present), 2)
    missing = tuple(k for k, present in availability.items() if not present)
    level: ConfidenceLevel = "HIGH" if score >= 0.80 else "MEDIUM" if score >= 0.60 else "LOW"
    return SEOConfidence(score, level, missing)
