from dataclasses import dataclass, field


@dataclass(frozen=True)
class CompetitorSnapshot:
    competitor_id: str
    price: float
    rating: float = 0.0
    reviews: int = 0
    strengths: tuple[str, ...] = field(default_factory=tuple)
    weaknesses: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CompetitorAnalysis:
    competitors: int
    average_price: float
    average_rating: float
    total_reviews: int
    gaps: tuple[str, ...]
    evidence_confidence: float


def analyze_competitors(items: tuple[CompetitorSnapshot, ...]) -> CompetitorAnalysis:
    if not items:
        return CompetitorAnalysis(0, 0.0, 0.0, 0, (), 0.0)
    for item in items:
        if item.price < 0 or not 0 <= item.rating <= 5 or item.reviews < 0:
            raise ValueError("invalid competitor metrics")
    gaps = sorted({gap.strip() for item in items for gap in item.weaknesses if gap.strip()})
    return CompetitorAnalysis(
        competitors=len(items),
        average_price=round(sum(x.price for x in items) / len(items), 2),
        average_rating=round(sum(x.rating for x in items) / len(items), 2),
        total_reviews=sum(x.reviews for x in items),
        gaps=tuple(gaps),
        evidence_confidence=round(min(1.0, len(items) / 5), 2),
    )
