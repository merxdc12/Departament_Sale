"""Internal product draft factory.

Creates planning artifacts only. It does not publish listings, place orders, spend
money, contact users, or call external marketplace/social APIs.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductDraft:
    product_id: str
    opportunity_id: str
    name: str
    business_line: str
    market: str
    sale_price: float
    status: str = "DRAFT"
    external_execution_allowed: bool = False


def create_product_draft(*, product_id: str, opportunity_id: str, name: str, business_line: str, market: str, sale_price: float, human_approved: bool) -> ProductDraft:
    if not human_approved:
        raise PermissionError("human approval is required before product draft creation")
    if not product_id.strip() or not name.strip() or not market.strip():
        raise ValueError("product_id, name and market are required")
    if sale_price <= 0:
        raise ValueError("sale_price must be positive")
    return ProductDraft(product_id.strip(), opportunity_id, name.strip(), business_line, market.strip(), sale_price)
