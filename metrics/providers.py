from dataclasses import dataclass
from typing import Protocol

from .models import ChannelMetrics


class MetricsProvider(Protocol):
    name: str
    official: bool
    read_only: bool

    def fetch(self) -> ChannelMetrics: ...


@dataclass(frozen=True)
class ManualExportProvider:
    """Safe bridge for platforms without an approved API connector yet."""

    metrics: ChannelMetrics
    name: str = "MANUAL_OR_OFFICIAL_EXPORT"
    official: bool = False
    read_only: bool = True

    def fetch(self) -> ChannelMetrics:
        return self.metrics


def require_read_only_provider(provider: MetricsProvider) -> None:
    if not getattr(provider, "read_only", False):
        raise RuntimeError("REVIEW: metrics providers must be read-only")
