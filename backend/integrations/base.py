"""Base class shared by all external API clients."""
from __future__ import annotations

from typing import Any

from ..config import external_apis_enabled, http_timeout
from ..utils.http import ApiResult, request_json


class BaseAPIClient:
    """Common timeout handling, availability checks and status reporting."""

    name = "base"
    requires_key = False

    def __init__(self, timeout: float | None = None):
        self.timeout = timeout or http_timeout()

    def is_configured(self) -> bool:
        """True when required credentials/settings exist (override if keys needed)."""
        return True

    def is_available(self) -> bool:
        """True when live calls are allowed and the client is configured."""
        return external_apis_enabled() and self.is_configured()

    def status(self) -> dict[str, Any]:
        """Return non-sensitive readiness information (never includes secrets)."""
        available = self.is_available()
        return {
            "name": self.name,
            "requires_key": self.requires_key,
            "configured": self.is_configured(),
            "available": available,
            "mode": "live" if available else "fallback",
        }

    def _get(self, url: str, **kwargs: Any) -> ApiResult:
        return request_json("GET", url, timeout=self.timeout, **kwargs)

    def _post(self, url: str, **kwargs: Any) -> ApiResult:
        return request_json("POST", url, timeout=self.timeout, **kwargs)
