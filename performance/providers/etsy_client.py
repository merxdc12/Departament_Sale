from __future__ import annotations
import time, requests
from dataclasses import dataclass

BASE_URL="https://api.etsy.com/v3"
class EtsyAPIError(RuntimeError): pass
class EtsyAuthError(EtsyAPIError): pass
class EtsyRateLimitError(EtsyAPIError): pass

@dataclass
class EtsySafeClient:
    keystring: str
    shared_secret: str
    access_token: str|None=None
    timeout: float=15.0
    max_retries: int=2

    def _headers(self, oauth=False):
        if not self.keystring or not self.shared_secret: raise EtsyAuthError("Missing Etsy API credentials.")
        h={"x-api-key":f"{self.keystring}:{self.shared_secret}","Accept":"application/json","User-Agent":"Dyrektor-Sales-SEO-Agent/0.5.1"}
        if oauth:
            if not self.access_token: raise EtsyAuthError("OAuth access token required.")
            h["Authorization"]=f"Bearer {self.access_token}"
        return h

    def _get(self,path,*,oauth=False,params=None):
        delay=1.0
        for attempt in range(self.max_retries+1):
            r=requests.get(BASE_URL+path,headers=self._headers(oauth),params=params,timeout=self.timeout)
            if r.status_code==429:
                wait=min(float(r.headers.get("retry-after") or delay),30.0)
                if attempt>=self.max_retries: raise EtsyRateLimitError("429: STOP/REVIEW")
                time.sleep(max(wait,delay)); delay*=2; continue
            if r.status_code in (401,403): raise EtsyAuthError(f"{r.status_code}: STOP/REVIEW; no fallback automation")
            if not r.ok: raise EtsyAPIError(f"Etsy API {r.status_code}: {r.text[:300]}")
            return r.json()
        raise EtsyAPIError("Unexpected request loop exit")

    def ping(self): return self._get("/application/openapi-ping")
    def get_listing(self,listing_id): return self._get(f"/application/listings/{listing_id}",oauth=True)
