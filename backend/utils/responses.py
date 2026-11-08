"""Consistent JSON response helpers."""
from __future__ import annotations

from typing import Any

from flask import jsonify


def success(message: str | None = None, status_code: int = 200, **payload: Any):
    """Return ``{"status": "success", ...}``."""
    body: dict[str, Any] = {"status": "success"}
    if message:
        body["message"] = message
    body.update(payload)
    return jsonify(body), status_code


def error(message: str, status_code: int = 400, **payload: Any):
    """Return ``{"status": "error", "message": ...}``."""
    return jsonify({"status": "error", "message": message, **payload}), status_code
