import requests

from backend.integrations import (
    ESCOClient, GeminiClient, GitHubClient, JobsAPIClient, YouTubeClient,
    get_integration_status,
)
from backend.utils.http import request_json


class FakeResponse:
    def __init__(self, status_code=200, payload=None, headers=None):
        self.status_code = status_code
        self._payload = payload
        self.headers = headers or {}
        self.ok = status_code < 400

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


def test_clients_initialise_without_keys(no_api_keys):
    status = get_integration_status()
    assert status["gemini"]["configured"] is False
    assert status["youtube"]["configured"] is False
    assert status["gemini"]["mode"] == "unavailable"
    assert all(s["mode"] == "fallback" for k, s in status.items() if k != "gemini")


def test_esco_falls_back_to_local_data():
    result = ESCOClient().search_occupations("data")
    assert result.ok and result.source == "fallback" and result.data
    assert ESCOClient().search_skills("python").data[0]["title"] == "Python"


def test_github_requires_a_search_term_and_falls_back():
    assert GitHubClient().search_repositories().ok is False
    result = GitHubClient().search_repositories(topic="flask", language="python")
    assert result.ok and result.source == "fallback" and result.data


def test_youtube_without_key_returns_resources(no_api_keys):
    result = YouTubeClient().search_videos("python")
    assert result.ok and result.source == "fallback"
    assert "YOUTUBE_API_KEY" in result.error and result.data


def test_jobs_fall_back_to_labelled_samples(no_api_keys):
    result = JobsAPIClient().search_jobs("data")
    assert result.ok and result.source == "fallback" and result.data
    assert all(job["is_demo"] for job in result.data)


def test_gemini_unavailable_without_key(no_api_keys):
    result = GeminiClient().generate_text("Hello")
    assert result.ok is False and result.source == "unavailable"
    assert "GEMINI_API_KEY" in result.error


def test_timeout_is_handled(monkeypatch):
    monkeypatch.setenv("EXTERNAL_APIS_ENABLED", "true")

    def boom(*args, **kwargs):
        raise requests.Timeout("secret-key-in-url")

    monkeypatch.setattr(requests, "request", boom)
    result = request_json("GET", "https://example.com", params={"key": "secret-key-in-url"})
    assert result.ok is False and "timed out" in result.error
    assert "secret" not in result.error


def test_rate_limit_is_detected(monkeypatch):
    monkeypatch.setenv("EXTERNAL_APIS_ENABLED", "true")
    monkeypatch.setattr(requests, "request", lambda *a, **k: FakeResponse(
        403, {}, {"X-RateLimit-Remaining": "0"}))
    result = GitHubClient().search_repositories(topic="python")
    assert result.source == "fallback" and result.rate_limited and result.data


def test_live_github_response_is_parsed(monkeypatch):
    monkeypatch.setenv("EXTERNAL_APIS_ENABLED", "true")
    payload = {"items": [{"full_name": "a/b", "html_url": "https://github.com/a/b",
                          "description": "d", "stargazers_count": 5,
                          "language": "Python", "topics": ["flask"]}]}
    monkeypatch.setattr(requests, "request", lambda *a, **k: FakeResponse(200, payload))
    result = GitHubClient().search_repositories(topic="flask")
    assert result.source == "live" and result.data[0]["name"] == "a/b"


def test_live_gemini_response_is_parsed_and_key_not_in_url(monkeypatch):
    monkeypatch.setenv("EXTERNAL_APIS_ENABLED", "true")
    seen = {}

    def fake(method, url, **kwargs):
        seen.update(url=url, headers=kwargs["headers"])
        return FakeResponse(200, {"candidates": [{"content": {"parts": [{"text": "Hi"}]}}]})

    monkeypatch.setattr(requests, "request", fake)
    result = GeminiClient(api_key="abc123").generate_text("Hello")
    assert result.ok and result.data["text"] == "Hi"
    assert "abc123" not in seen["url"] and seen["headers"]["x-goog-api-key"] == "abc123"
