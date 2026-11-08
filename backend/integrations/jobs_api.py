"""Replaceable job-provider architecture. Sample jobs are always available."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from ..config import external_apis_enabled, get_env
from ..utils.data_loader import load_dataset_safe, search_records
from ..utils.http import ApiResult
from .base import BaseAPIClient


class JobProvider(ABC):
    """Interface every job source implements."""

    name: ClassVar[str] = "provider"

    @abstractmethod
    def is_configured(self) -> bool:
        """True when credentials needed by this provider exist."""

    @abstractmethod
    def search(self, query: str, location: str, limit: int, timeout: float) -> ApiResult:
        """Return job dicts using the same fields as data/jobs.json."""


class SampleJobProvider(JobProvider):
    """Local demonstration listings from data/jobs.json."""

    name = "sample"

    def is_configured(self) -> bool:
        return True

    def search(self, query: str = "", location: str = "", limit: int = 10,
               timeout: float = 0) -> ApiResult:
        jobs = search_records(load_dataset_safe("jobs"), query,
                              ("title", "description", "required_skills", "company"))
        if location.strip():
            jobs = [j for j in jobs if location.lower() in j["location"].lower()]
        return ApiResult(ok=True, data=jobs[:limit], source="sample")


class AdzunaProvider(JobProvider):
    """Adzuna job search (requires ADZUNA_APP_ID and ADZUNA_APP_KEY)."""

    name = "adzuna"
    BASE_URL = "https://api.adzuna.com/v1/api/jobs"

    def __init__(self):
        self._app_id = get_env("ADZUNA_APP_ID")
        self._app_key = get_env("ADZUNA_APP_KEY")
        self._country = get_env("ADZUNA_COUNTRY", "in")

    def is_configured(self) -> bool:
        return bool(self._app_id and self._app_key)

    def search(self, query: str, location: str, limit: int, timeout: float) -> ApiResult:
        from ..utils.http import request_json
        params = {"app_id": self._app_id, "app_key": self._app_key,
                  "results_per_page": limit, "what": query, "content-type": "application/json"}
        if location.strip():
            params["where"] = location
        result = request_json("GET", f"{self.BASE_URL}/{self._country}/search/1",
                              params=params, timeout=timeout)
        if result.ok:
            result.data = [{
                "id": f"adzuna_{j.get('id')}", "title": j.get("title"),
                "company": (j.get("company") or {}).get("display_name"),
                "location": (j.get("location") or {}).get("display_name"),
                "job_type": j.get("contract_time"), "description": j.get("description"),
                "application_url": j.get("redirect_url"), "is_demo": False,
                "listing_label": "Live listing via Adzuna."}
                for j in (result.data or {}).get("results", [])]
        return result


class JobsAPIClient(BaseAPIClient):
    """Try configured live providers in order, then fall back to sample jobs."""

    name = "jobs"
    PROVIDER_REGISTRY: ClassVar[dict[str, type[JobProvider]]] = {"adzuna": AdzunaProvider}

    def __init__(self, providers: list[JobProvider] | None = None, timeout: float | None = None):
        super().__init__(timeout)
        if providers is None:
            names = [n.strip().lower() for n in get_env("JOBS_PROVIDERS", "adzuna").split(",")]
            providers = [self.PROVIDER_REGISTRY[n]() for n in names if n in self.PROVIDER_REGISTRY]
        self.providers = providers
        self.sample_provider = SampleJobProvider()

    @classmethod
    def register_provider(cls, name: str, provider_cls: type[JobProvider]) -> None:
        """Plug in a new provider without changing existing code."""
        cls.PROVIDER_REGISTRY[name.lower()] = provider_cls

    def is_configured(self) -> bool:
        return any(p.is_configured() for p in self.providers)

    def status(self) -> dict:
        info = super().status()
        info["providers"] = {p.name: p.is_configured() for p in self.providers}
        info["sample_fallback"] = True
        return info

    def search_jobs(self, query: str = "", location: str = "", limit: int = 10) -> ApiResult:
        """Return live results if any provider succeeds, otherwise labelled samples."""
        limit = max(1, min(int(limit), 50))
        reason = None
        if external_apis_enabled():
            for provider in self.providers:
                if not provider.is_configured():
                    continue
                result = provider.search(query, location, limit, self.timeout)
                if result.ok and result.data:
                    return result
                reason = result.error or reason
        sample = self.sample_provider.search(query, location, limit)
        return ApiResult.fallback(sample.data, reason or "No live job provider available.")
