"""Optional Gemini integration. Never required; reports clearly when unavailable."""
from __future__ import annotations

from ..config import get_env
from ..utils.http import ApiResult
from .base import BaseAPIClient

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


class GeminiClient(BaseAPIClient):
    """Generate text with Gemini when GEMINI_API_KEY is configured."""

    name = "gemini"
    requires_key = True
    UNAVAILABLE_MESSAGE = ("Gemini is not configured. Set GEMINI_API_KEY in the backend "
                           "environment to enable AI-generated responses.")

    def __init__(self, api_key: str | None = None, model: str | None = None,
                 timeout: float | None = None):
        super().__init__(timeout)
        self._api_key = api_key if api_key is not None else get_env("GEMINI_API_KEY")
        self.model = model or get_env("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)

    def is_configured(self) -> bool:
        return bool(self._api_key)

    def status(self) -> dict:
        info = super().status()
        info["mode"] = "live" if info["available"] else "unavailable"  # no fallback text
        return info

    def generate_text(self, prompt: str, system_instruction: str | None = None) -> ApiResult:
        """Return ``{"text", "model"}`` or an unavailable result (no fallback text)."""
        if not self.is_configured():
            return ApiResult.unavailable(self.UNAVAILABLE_MESSAGE)
        if not prompt or not prompt.strip():
            return ApiResult.unavailable("Prompt must not be empty.")
        body: dict = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
        if system_instruction:
            body["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        # Key travels in a header so it never appears in URLs or logs.
        result = self._post(f"{GEMINI_BASE_URL}/models/{self.model}:generateContent",
                            headers={"x-goog-api-key": self._api_key,
                                     "Content-Type": "application/json"}, json_body=body)
        if not result.ok:
            return result
        parts = (((result.data or {}).get("candidates") or [{}])[0]
                 .get("content", {}).get("parts", []))
        text = "".join(p.get("text", "") for p in parts).strip()
        if not text:
            return ApiResult.unavailable("Gemini returned an empty response.")
        result.data = {"text": text, "model": self.model}
        return result
