import json
import os
from dataclasses import dataclass
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from metrics.models import ChannelMetrics
from .auth import ConnectorCredentials, require_credentials
from .connectors import PublishRequest, PublishResult, require_publish_permission
from .official_adapters import official_api_profile


class PinterestTransport(Protocol):
    def request(self, method: str, url: str, *, headers: dict[str, str], body: dict | None = None) -> tuple[int, dict]: ...


class UrllibPinterestTransport:
    def request(self, method: str, url: str, *, headers: dict[str, str], body: dict | None = None) -> tuple[int, dict]:
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(req, timeout=20) as response:
                payload = response.read().decode("utf-8")
                return response.status, json.loads(payload) if payload else {}
        except HTTPError as exc:
            if exc.code in (401, 403, 429):
                raise RuntimeError(f"REVIEW: Pinterest API stopped on HTTP {exc.code}") from exc
            raise RuntimeError(f"Pinterest API HTTP {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError("Pinterest API network error") from exc


@dataclass
class PinterestConnector:
    credentials: ConnectorCredentials
    board_id: str
    transport: PinterestTransport
    publishing_enabled: bool = False
    platform: str = "PINTEREST"
    official: bool = True
    read_only: bool = False

    @classmethod
    def from_env(cls, credentials: ConnectorCredentials, *, transport: PinterestTransport | None = None) -> "PinterestConnector":
        return cls(
            credentials=credentials,
            board_id=os.getenv("PINTEREST_BOARD_ID", ""),
            transport=transport or UrllibPinterestTransport(),
            publishing_enabled=os.getenv("PINTEREST_PUBLISHING_ENABLED", "false").lower() == "true",
        )

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.credentials.access_token}",
            "Content-Type": "application/json",
        }

    def fetch_metrics(self) -> ChannelMetrics:
        require_credentials(self.credentials, required_scopes=("pins:read",))
        profile = official_api_profile("PINTEREST")
        status, payload = self.transport.request(
            "GET",
            f"{profile.api_base}/pins?pin_metrics=true&page_size=25",
            headers=self._headers,
        )
        if status != 200:
            raise RuntimeError(f"Pinterest metrics request failed with HTTP {status}")

        impressions = 0
        clicks = 0
        for item in payload.get("items", []):
            metrics = item.get("pin_metrics", {}) or {}
            lifetime = metrics.get("lifetime_metrics", metrics)
            impressions += int(lifetime.get("IMPRESSION", 0) or 0)
            clicks += int(lifetime.get("OUTBOUND_CLICK", 0) or 0)

        return ChannelMetrics(
            channel="PINTEREST",
            impressions=impressions,
            clicks=clicks,
            source="PINTEREST_OFFICIAL_API",
            source_confidence=0.9,
        )

    def publish(self, request: PublishRequest) -> PublishResult:
        require_publish_permission(self, request)
        require_credentials(self.credentials, required_scopes=("boards:read", "pins:read", "pins:write"))
        if not self.board_id.strip():
            raise RuntimeError("REVIEW: PINTEREST_BOARD_ID is not configured")
        if not request.media_refs:
            raise ValueError("Pinterest image Pin requires an image URL")

        image_url = request.media_refs[0]
        if not image_url.startswith("https://"):
            raise ValueError("Pinterest image URL must use HTTPS")

        profile = official_api_profile("PINTEREST")
        body = {
            "board_id": self.board_id,
            "description": request.text.strip(),
            "media_source": {
                "source_type": "image_url",
                "url": image_url,
                "is_standard": True,
            },
        }
        if request.link:
            body["link"] = request.link

        status, payload = self.transport.request(
            "POST",
            f"{profile.api_base}{profile.publish_endpoint}",
            headers=self._headers,
            body=body,
        )
        if status != 201:
            raise RuntimeError(f"Pinterest publish failed with HTTP {status}")

        pin_id = str(payload.get("id", ""))
        return PublishResult(
            platform="PINTEREST",
            status="PUBLISHED",
            external_id=pin_id,
            url=f"https://www.pinterest.com/pin/{pin_id}/" if pin_id else "",
        )
