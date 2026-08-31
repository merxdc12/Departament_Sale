from .etsy_client import EtsySafeClient
from ..models import ListingPerformance

class EtsyProvider:
    name="ETSY_OFFICIAL_API"
    official=True
    read_only=True
    def __init__(self,client:EtsySafeClient): self.client=client
    def connection_test(self): return self.client.ping()
    def fetch_listing_metadata(self,listing_id): return self.client.get_listing(listing_id)
    def fetch(self,listing_id):
        x=self.fetch_listing_metadata(listing_id)
        return ListingPerformance(platform="Etsy",listing_id=str(x.get("listing_id",listing_id)),shop_id=str(x.get("shop_id","")),platform_url=x.get("url","") or "",data_source="ETSY_OFFICIAL_API_METADATA")
