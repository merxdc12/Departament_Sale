from dataclasses import dataclass
from typing import Protocol

from metrics.models import ChannelMetrics
from .models import SocialPlatform


@dataclass(frozen=True)
class PublishRequest:
    platform: SocialPlatform
    content_format: str
    text: str
    media_refs: tuple[str, ...] = ()
    link: str = ""
    disclosure: str = ""
    human_approved: bool = False


@dataclass(frozen=True)
class PublishResult:
    platform: SocialPlatform
    status: str
    external_id: str = ""
    url: str = ""
    reason: str = ""


class SocialConnector(Protocol):
    platform: SocialPlatform
    official: bool
    read_only: bool
    publishing_enabled: bool

    def fetch_metrics(self) -> ChannelMetrics: ...
    def publish(self, request: PublishRequest) -> PublishResult: ...


def require_safe_connector(connector: SocialConnector) -> None:
    if not getattr(connector, "official", False):
        raise RuntimeError("REVIEW: only official platform integrations are allowed for network interaction")


def require_publish_permission(connector: SocialConnector, request: PublishRequest) -> None:
    require_safe_connector(connector)
    if not getattr(connector, "publishing_enabled", False):
        raise RuntimeError("REVIEW: publishing is disabled for this connector")
    if request.platform != connector.platform:
        raise ValueError("publish request platform must match connector platform")
    if not request.human_approved:
        raise RuntimeError("REVIEW: human approval is required before publishing")
    if not request.text.strip() and not request.media_refs:
        raise ValueError("publish request must contain text or media")
