from .models import ListingPerformance

def ctr(p: ListingPerformance) -> float:
    return p.clicks / p.impressions if p.impressions else 0.0

def conversion(p: ListingPerformance) -> float:
    return p.orders / p.visits if p.visits else 0.0

def profit(p: ListingPerformance) -> float:
    return p.revenue - p.fees - p.production_cost - p.advertising_cost - p.other_cost

def profit_per_1000_impressions(p: ListingPerformance) -> float:
    return profit(p) / p.impressions * 1000 if p.impressions else 0.0

def winner_status(p: ListingPerformance) -> str:
    if p.impressions < 100:
        return "INSUFFICIENT_DATA"
    if p.orders >= 1 and profit(p) > 0:
        return "WINNER"
    return "NOT_WINNER"
