"""Shared outbound HTTP helper: timeouts, error handling, uniform result type."""
from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from typing import Any

import requests

from ..config import external_apis_enabled, http_timeout

logger = logging.getLogger(__name__)

SOURCE_LIVE = "live"
SOURCE_FALLBACK = "fallback"
SOURCE_UNAVAILABLE = "unavailable"


@dataclass
class ApiResult:
    """Uniform result returned by every integration client."""

    ok: bool
    data: Any = None
    error: str | None = None
    status_code: int | None = None
    source: str = SOURCE_LIVE
    rate_limited: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def fallback(cls, data: Any, reason: str | None = None, *, rate_limited: bool = False):
        """Local data served because the live service was not usable."""
        return cls(ok=True, data=data, error=reason, source=SOURCE_FALLBACK,
                   rate_limited=rate_limited)

    @classmethod
    def unavailable(cls, reason: str):
        """Feature unavailable and no fallback exists."""
        return cls(ok=False, error=reason, source=SOURCE_UNAVAILABLE)


def request_json(method: str, url: str, *, params: dict | None = None,
                 headers: dict | None = None, json_body: dict | None = None,
                 timeout: float | None = None) -> ApiResult:
    """Perform an HTTP request and return parsed JSON inside an ApiResult.

    Never raises. Error messages deliberately omit URLs and exception text,
    because request parameters may contain API keys.
    """
    if not external_apis_enabled():
        return ApiResult.unavailable(
            "External API calls are disabled (EXTERNAL_APIS_ENABLED=false)."
        )
    try:
        response = requests.request(method, url, params=params, headers=headers,
                                    json=json_body, timeout=timeout or http_timeout())
    except requests.Timeout:
        logger.warning("Request to %s timed out", url)
        return ApiResult.unavailable("The external service timed out.")
    except requests.RequestException as exc:
        logger.warning("Request to %s failed: %s", url, type(exc).__name__)
        return ApiResult.unavailable("The external service could not be reached.")

    status = response.status_code
    remaining = response.headers.get("X-RateLimit-Remaining")
    if status == 429 or (status == 403 and remaining == "0"):
        return ApiResult(ok=False, error="Rate limit reached for the external service.",
                         status_code=status, source=SOURCE_UNAVAILABLE, rate_limited=True)
    if not response.ok:
        return ApiResult(ok=False, error=f"External service returned HTTP {status}.",
                         status_code=status, source=SOURCE_UNAVAILABLE)
    try:
        payload = response.json()
    except ValueError:
        return ApiResult(ok=False, error="External service returned invalid JSON.",
                         status_code=status, source=SOURCE_UNAVAILABLE)
    return ApiResult(ok=True, data=payload, status_code=status)
