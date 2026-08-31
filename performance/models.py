from dataclasses import dataclass

@dataclass
class ListingPerformance:
    platform: str
    listing_id: str = ""
    shop_id: str = ""
    platform_url: str = ""
    published_at: str = ""
    impressions: int = 0
    clicks: int = 0
    visits: int = 0
    orders: int = 0
    revenue: float = 0.0
    fees: float = 0.0
    production_cost: float = 0.0
    advertising_cost: float = 0.0
    other_cost: float = 0.0
    data_source: str = ""
