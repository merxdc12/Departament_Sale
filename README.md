# Dyrektor Sales — SEO / POD Discovery Agent

Sales-department module for POD SEO automation.

Current baseline: **v0.5.1 Etsy Safe Connector**.

**Account safety → SEO quality → visibility → click → sale → profit → learning.**

## Current modules
- Performance Engine
- Account Safety Gate
- Etsy official Open API v3 safe connector
- OAuth 2.0 Authorization Code + PKCE S256
- least-privilege read scopes: `listings_r`, `transactions_r`
- conservative rate-limit handling
- Redbubble provider disabled for account automation until an approved official method is verified

## Security
Never commit `.env`, API keys, OAuth tokens, passwords, `credentials.json`, or marketplace session cookies.

See `SECURITY.md` for hard safety rules.
