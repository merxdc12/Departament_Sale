from dataclasses import dataclass
from .models import RiskLevel


@dataclass(frozen=True)
class SEORisk:
    level: RiskLevel
    penalty: int
    blocked: bool
    reasons: tuple[str, ...]


def evaluate_seo_risk(
    *,
    trademark_risk: bool = False,
    copyright_risk: bool = False,
    policy_risk: bool = False,
    prohibited_content: bool = False,
    misleading_claim_risk: bool = False,
) -> SEORisk:
    """Business/content risk only. Account access safety lives in performance.safety."""
    critical = []
    if prohibited_content:
        critical.append("Prohibited or restricted content detected.")
    if trademark_risk:
        critical.append("Potential trademark infringement detected.")
    if copyright_risk:
        critical.append("Potential copyright infringement detected.")
    if critical:
        return SEORisk("CRITICAL", 100, True, tuple(critical))

    reasons = []
    if policy_risk:
        reasons.append("Product/listing may conflict with platform policy.")
    if misleading_claim_risk:
        reasons.append("Potential misleading or unsupported marketing claim.")

    if policy_risk and misleading_claim_risk:
        return SEORisk("HIGH", 30, False, tuple(reasons))
    if reasons:
        return SEORisk("MEDIUM", 10, False, tuple(reasons))
    return SEORisk("LOW", 0, False, ())
