"""GitHub public repository search with rate-limit handling and fallback."""
from __future__ import annotations

from ..config import get_env
from ..utils.data_loader import load_dataset_safe, search_records
from ..utils.http import ApiResult
from .base import BaseAPIClient

GITHUB_API_URL = "https://api.github.com"


class GitHubClient(BaseAPIClient):
    """Search public repositories by topic/language. Token is optional."""

    name = "github"

    def __init__(self, token: str | None = None, timeout: float | None = None):
        super().__init__(timeout)
        self._token = token if token is not None else get_env("GITHUB_TOKEN")

    def status(self) -> dict:
        info = super().status()
        info["authenticated"] = bool(self._token)  # higher rate limits when True
        return info

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json",
                   "X-GitHub-Api-Version": "2022-11-28",
                   "User-Agent": "ai-student-mentor"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def search_repositories(self, query: str | None = None, topic: str | None = None,
                            language: str | None = None, per_page: int = 5) -> ApiResult:
        """Return ``[{"name", "url", "description", "stars", "language", "topics"}]``."""
        parts = [p for p in (query, f"topic:{topic}" if topic else None,
                             f"language:{language}" if language else None) if p]
        if not parts:
            return ApiResult.unavailable("Provide a query, topic or language.")
        per_page = max(1, min(int(per_page), 30))
        reason, rate_limited = None, False
        if self.is_available():
            result = self._get(f"{GITHUB_API_URL}/search/repositories", headers=self._headers(),
                               params={"q": " ".join(parts), "sort": "stars",
                                       "order": "desc", "per_page": per_page})
            if result.ok:
                result.data = [{"name": r.get("full_name"), "url": r.get("html_url"),
                                "description": r.get("description"),
                                "stars": r.get("stargazers_count"),
                                "language": r.get("language"), "topics": r.get("topics", [])}
                               for r in (result.data or {}).get("items", [])]
                return result
            reason, rate_limited = result.error, result.rate_limited
        return ApiResult.fallback(self._local_search(" ".join(p for p in (query, topic, language) if p),
                                                     per_page), reason, rate_limited=rate_limited)

    @staticmethod
    def _local_search(text: str, limit: int) -> list[dict]:
        matches = search_records(load_dataset_safe("projects"), text,
                                 ("title", "description", "technologies"))
        return [{"name": p["title"], "url": None, "description": p["description"],
                 "stars": None, "language": None, "topics": p["technologies"],
                 "source_project_id": p["id"]} for p in matches[:limit]]
