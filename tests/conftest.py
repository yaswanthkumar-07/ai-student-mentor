"""Shared fixtures. External API calls are disabled for deterministic tests."""
import os

os.environ["EXTERNAL_APIS_ENABLED"] = "false"

import pytest  # noqa: E402

from backend.app import create_app  # noqa: E402


@pytest.fixture()
def app():
    return create_app("testing")


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def no_api_keys(monkeypatch):
    """Remove every optional credential from the environment."""
    for key in ("GEMINI_API_KEY", "YOUTUBE_API_KEY", "GITHUB_TOKEN",
                "ADZUNA_APP_ID", "ADZUNA_APP_KEY"):
        monkeypatch.delenv(key, raising=False)
