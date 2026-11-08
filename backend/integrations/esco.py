"""ESCO (European occupations and skills) client with local dataset fallback."""
from __future__ import annotations

from ..config import get_env
from ..utils.data_loader import load_dataset_safe, search_records
from ..utils.http import ApiResult
from .base import BaseAPIClient

DEFAULT_ESCO_BASE_URL = "https://ec.europa.eu/esco/api"


class ESCOClient(BaseAPIClient):
    """Search ESCO occupations and skills; falls back to careers/skills datasets."""

    name = "esco"

    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        super().__init__(timeout)
        self.base_url = (base_url or get_env("ESCO_BASE_URL", DEFAULT_ESCO_BASE_URL)).rstrip("/")

    def search_occupations(self, query: str, limit: int = 5) -> ApiResult:
        """Return ``[{"title", "uri", "description"}]`` for matching occupations."""
        return self._search(query, "occupation", limit)

    def search_skills(self, query: str, limit: int = 5) -> ApiResult:
        """Return ``[{"title", "uri", "description"}]`` for matching skills."""
        return self._search(query, "skill", limit)

    def _search(self, query: str, kind: str, limit: int) -> ApiResult:
        limit = max(1, min(int(limit), 25))
        reason = None
        if self.is_available() and query.strip():
            result = self._get(f"{self.base_url}/search",
                               params={"text": query, "type": kind, "language": "en",
                                       "limit": limit})
            if result.ok:
                items = (result.data or {}).get("_embedded", {}).get("results", [])
                result.data = [{"title": i.get("title"), "uri": i.get("uri"),
                                "description": None} for i in items][:limit]
                return result
            reason = result.error
        return ApiResult.fallback(self._local_search(query, kind, limit), reason)

    @staticmethod
    def _local_search(query: str, kind: str, limit: int) -> list[dict]:
        if kind == "occupation":
            records = search_records(load_dataset_safe("careers"), query,
                                     ("title", "description", "category"))
            return [{"title": r["title"], "uri": None, "description": r["description"]}
                    for r in records[:limit]]
        records = search_records(load_dataset_safe("skills"), query,
                                 ("name", "description", "category"))
        return [{"title": r["name"], "uri": None, "description": r["description"]}
                for r in records[:limit]]
