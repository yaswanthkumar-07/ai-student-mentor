"""Centralised JSON error handling."""
from __future__ import annotations

import logging

from flask import Flask
from werkzeug.exceptions import HTTPException

from .responses import error

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Raise from routes/services to return a clean JSON error."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def register_error_handlers(app: Flask) -> None:
    """Register JSON handlers for API, HTTP and unexpected errors."""

    @app.errorhandler(APIError)
    def handle_api_error(exc: APIError):
        return error(exc.message, exc.status_code)

    @app.errorhandler(HTTPException)
    def handle_http_error(exc: HTTPException):
        return error(exc.description or exc.name, exc.code or 500)

    @app.errorhandler(Exception)
    def handle_unexpected(exc: Exception):
        logger.exception("Unhandled error: %s", exc)
        return error("An unexpected server error occurred.", 500)
