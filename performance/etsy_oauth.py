from __future__ import annotations
import base64, hashlib, secrets
from dataclasses import dataclass
from urllib.parse import urlencode
import requests

AUTH_URL = "https://www.etsy.com/oauth/connect"
TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"
SAFE_READ_SCOPES = ("listings_r", "transactions_r")

@dataclass(frozen=True)
class PKCEPair:
    verifier: str
    challenge: str

def make_pkce() -> PKCEPair:
    verifier = secrets.token_urlsafe(64)[:96]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return PKCEPair(verifier, challenge)

def make_state() -> str:
    return secrets.token_urlsafe(32)

def build_authorization_url(client_id, redirect_uri, pkce, state, scopes=SAFE_READ_SCOPES):
    params = {"response_type":"code","redirect_uri":redirect_uri,"scope":" ".join(scopes),"client_id":client_id,"state":state,"code_challenge":pkce.challenge,"code_challenge_method":"S256"}
    return AUTH_URL + "?" + urlencode(params)

def exchange_code(*, client_id, code, code_verifier, redirect_uri=None, timeout=15.0):
    data={"grant_type":"authorization_code","client_id":client_id,"code":code,"code_verifier":code_verifier}
    if redirect_uri: data["redirect_uri"]=redirect_uri
    r=requests.post(TOKEN_URL,data=data,timeout=timeout); r.raise_for_status(); return r.json()

def refresh_access_token(*, client_id, refresh_token, timeout=15.0):
    r=requests.post(TOKEN_URL,data={"grant_type":"refresh_token","client_id":client_id,"refresh_token":refresh_token},timeout=timeout); r.raise_for_status(); return r.json()
