"""Flask application factory for AI Student Mentor.

Run locally:   flask --app backend.app run --debug
or:            python -m backend.app
Production:    gunicorn "backend.app:create_app()"
"""
from __future__ import annotations

import logging

from flask import Flask
from flask_cors import CORS

from .config import CONFIG_MAP, get_env, resolve_config_name
from .routes import register_blueprints
from .utils.errors import register_error_handlers
from .utils.logging_config import configure_logging


def create_app(config_name: str | None = None, overrides: dict | None = None) -> Flask:
    """Build and configure the Flask application."""
    config_class = CONFIG_MAP[resolve_config_name(config_name)]
    config_class.validate()

    app = Flask(__name__)
    app.config.from_object(config_class)
    if overrides:
        app.config.update(overrides)
    app.json.sort_keys = False

    configure_logging(app.config["LOG_LEVEL"])
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    register_blueprints(app)
    register_error_handlers(app)

    logging.getLogger(__name__).info("Started in %s mode", app.config["ENV_NAME"])
    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=int(get_env("PORT", "5000")))
