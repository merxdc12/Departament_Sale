from dataclasses import dataclass

@dataclass(frozen=True)
class AccountSafetyPolicy:
    read_only_default: bool = True
    official_api_only: bool = True
    browser_scraping_allowed: bool = False
    credential_sharing_allowed: bool = False
    automatic_publish_allowed: bool = False
    max_retries: int = 2
    fail_closed: bool = True

def require_safe_provider(provider, policy: AccountSafetyPolicy = AccountSafetyPolicy()):
    if policy.official_api_only and not getattr(provider, "official", False):
        raise RuntimeError("REVIEW: provider is not an approved official API source.")
    if policy.read_only_default and not getattr(provider, "read_only", False):
        raise RuntimeError("REVIEW: provider is not read-only.")
    return True
