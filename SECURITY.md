# Account Safety Policy — v0.5.1

1. Etsy: official Open API v3 only.
2. OAuth uses Authorization Code + PKCE S256 and random one-time state.
3. Read scopes only: `listings_r`, `transactions_r`.
4. No write/delete marketplace scopes in this release.
5. No Selenium/Playwright seller-dashboard scraping, CAPTCHA bypass, cookie/session reuse, proxy rotation, fingerprint spoofing, or rate-limit evasion.
6. 401/403 => STOP/REVIEW.
7. 429 => respect Retry-After and bounded backoff; then STOP/REVIEW.
8. Secrets stay local in `.env` / `.secrets/`, never GitHub, Google Sheets, logs or chat.
9. Redbubble account automation remains disabled until an approved official integration is verified.
10. No fabricated analytics: unavailable metrics remain unknown.
11. Automatic publishing/editing/deletion remains disabled.
12. Automation is conservative and account-safety-first; platform rules always override desired speed.
