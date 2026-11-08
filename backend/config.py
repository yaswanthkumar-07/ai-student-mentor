"""Centralised configuration for the AI Student Mentor backend.

All settings come from environment variables (optionally loaded from a local
``.env`` file). Secrets are only ever read here on the backend and are never
sent to the frontend.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"

load_dotenv(PROJECT_ROOT / ".env")

APP_NAME = "AI Student Mentor"
APP_TAGLINE = "Your Career Journey, Simplified."
APP_VERSION = "0.1.0"
MODULES = (
    "Career Recommendation",
    "Skill Gap Analysis",
    "Learning Roadmap",
    "Project Suggestions",
    "Job Recommendations",
    "Resume Builder",
    "Resume Analyzer",
    "Career Assistant",
)

DEFAULT_HTTP_TIMEOUT = 8.0
# Values copied verbatim from .env.example are treated as "not set".
_PLACEHOLDER_PREFIXES = ("your-", "your_", "change-me", "changeme")


def get_env(name: str, default: str = "") -> str:
    """Return a stripped environment variable, ignoring blanks and placeholders."""
    value = os.environ.get(name, "").strip()
    if not value or value.lower().startswith(_PLACEHOLDER_PREFIXES):
        return default
    return value


def env_flag(name: str, default: bool = True) -> bool:
    """Parse a boolean environment variable."""
    value = get_env(name)
    if not value:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def http_timeout() -> float:
    """Timeout (seconds) applied to every outbound HTTP request."""
    try:
        return float(get_env("HTTP_TIMEOUT_SECONDS", str(DEFAULT_HTTP_TIMEOUT)))
    except ValueError:
        return DEFAULT_HTTP_TIMEOUT


def external_apis_enabled() -> bool:
    """Global switch; when false every integration uses local fallback data."""
    return env_flag("EXTERNAL_APIS_ENABLED", True)


def parse_origins(raw: str) -> list[str]:
    """Split a comma-separated CORS origin string."""
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


class BaseConfig:
    """Settings shared by every environment."""

    ENV_NAME = "base"
    DEBUG = False
    TESTING = False
    APP_NAME = APP_NAME
    APP_VERSION = APP_VERSION
    LOG_LEVEL = get_env("LOG_LEVEL", "INFO").upper()
    SECRET_KEY = get_env("SECRET_KEY", "")
    CORS_ORIGINS = ["*"]

    @classmethod
    def validate(cls) -> None:
        """Raise if the configuration is unsafe to run."""


class DevelopmentConfig(BaseConfig):
    """Local development: debug on, permissive CORS, throwaway secret key."""

    ENV_NAME = "development"
    DEBUG = True
    LOG_LEVEL = get_env("LOG_LEVEL", "DEBUG").upper()
    SECRET_KEY = get_env("SECRET_KEY", "dev-only-insecure-key")
    CORS_ORIGINS = parse_origins(get_env("CORS_ORIGINS", "*"))


class ProductionConfig(BaseConfig):
    """Deployed backend: requires a real SECRET_KEY and explicit CORS origins."""

    ENV_NAME = "production"
    CORS_ORIGINS = parse_origins(
        get_env("CORS_ORIGINS", "https://ai-student-mentor.pages.dev")
    )

    @classmethod
    def validate(cls) -> None:
        if not cls.SECRET_KEY:
            raise RuntimeError("SECRET_KEY must be set when FLASK_ENV=production.")


class TestingConfig(DevelopmentConfig):
    """Automated tests: quiet logging."""

    ENV_NAME = "testing"
    DEBUG = False
    TESTING = True
    LOG_LEVEL = "WARNING"


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
_ALIASES = {"dev": "development", "prod": "production", "test": "testing"}


def resolve_config_name(name: str | None = None) -> str:
    """Resolve a config name from an argument or FLASK_ENV (default: development)."""
    raw = (name or get_env("FLASK_ENV", "development")).lower()
    raw = _ALIASES.get(raw, raw)
    return raw if raw in CONFIG_MAP else "development"
