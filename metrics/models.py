from dataclasses import dataclass


@dataclass(frozen=True)
class ChannelMetrics:
    channel: str
    impressions: int = 0
    clicks: int = 0
    visits: int = 0
    orders: int = 0
    revenue: float = 0.0
    total_cost: float = 0.0
    source: str = "UNKNOWN"
    source_confidence: float = 0.0

    def __post_init__(self) -> None:
        for name in ("impressions", "clicks", "visits", "orders"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} cannot be negative")
        if self.revenue < 0 or self.total_cost < 0:
            raise ValueError("revenue and total_cost cannot be negative")
        if self.clicks > self.impressions and self.impressions:
            raise ValueError("clicks cannot exceed impressions")
        if self.orders > self.visits:
            raise ValueError("orders cannot exceed visits")
        if not 0 <= self.source_confidence <= 1:
            raise ValueError("source_confidence must be between 0 and 1")

    @property
    def profit(self) -> float:
        return self.revenue - self.total_cost
