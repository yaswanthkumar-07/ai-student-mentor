import pytest

from backend.app import create_app
from backend.config import get_env, resolve_config_name


def test_resolve_config_name(monkeypatch):
    monkeypatch.delenv("FLASK_ENV", raising=False)
    assert resolve_config_name() == "development"
    assert resolve_config_name("prod") == "production"
    assert resolve_config_name("nonsense") == "development"


def test_placeholder_values_are_ignored(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "your-gemini-api-key")
    assert get_env("GEMINI_API_KEY") == ""


def test_production_requires_secret_key(monkeypatch):
    from backend.config import ProductionConfig
    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", "")
    with pytest.raises(RuntimeError):
        create_app("production")


def test_overrides_apply():
    assert create_app("testing", {"CUSTOM": 1}).config["CUSTOM"] == 1
