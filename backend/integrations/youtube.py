"""YouTube Data API search. The API key is optional; falls back to local resources."""
from __future__ import annotations

from ..config import get_env
from ..utils.data_loader import load_dataset_safe, search_records
from ..utils.http import ApiResult
from .base import BaseAPIClient

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


class YouTubeClient(BaseAPIClient):
    """Find learning videos; without a key returns curated learning resources."""

    name = "youtube"
    requires_key = True

    def __init__(self, api_key: str | None = None, timeout: float | None = None):
        super().__init__(timeout)
        self._api_key = api_key if api_key is not None else get_env("YOUTUBE_API_KEY")

    def is_configured(self) -> bool:
        return bool(self._api_key)

    def search_videos(self, query: str, max_results: int = 5) -> ApiResult:
        """Return ``[{"title", "channel", "url", "video_id"}]`` or fallback resources."""
        max_results = max(1, min(int(max_results), 25))
        reason = None
        if self.is_available() and query.strip():
            result = self._get(YOUTUBE_SEARCH_URL,
                               params={"part": "snippet", "type": "video", "q": query,
                                       "maxResults": max_results, "key": self._api_key})
            if result.ok:
                result.data = [
                    {"title": i["snippet"]["title"], "channel": i["snippet"]["channelTitle"],
                     "video_id": i["id"]["videoId"],
                     "url": f"https://www.youtube.com/watch?v={i['id']['videoId']}"}
                    for i in (result.data or {}).get("items", [])
                    if i.get("id", {}).get("videoId")]
                return result
            reason = result.error
        elif not self.is_configured():
            reason = "YOUTUBE_API_KEY is not configured; showing curated resources."
        matches = search_records(load_dataset_safe("learning_resources"), query,
                                 ("title", "topic", "provider"))[:max_results]
        return ApiResult.fallback(
            [{"title": r["title"], "channel": r["provider"], "video_id": None,
              "url": r["url"]} for r in matches], reason)
