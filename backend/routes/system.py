"""System endpoints: health check and application info."""
from __future__ import annotations

from flask import Blueprint, current_app, jsonify

from ..config import APP_NAME, APP_TAGLINE, MODULES
from ..integrations import get_integration_status
from ..utils.data_loader import DATASET_NAMES, load_dataset_safe

system_bp = Blueprint("system", __name__, url_prefix="/api")


@system_bp.get("/health")
def health():
    """Liveness probe used by Render and the frontend."""
    return jsonify({"status": "success", "application": APP_NAME,
                    "message": "Backend is running"})


@system_bp.get("/info")
def info():
    """Application metadata, module names, dataset sizes and integration readiness."""
    return jsonify({
        "status": "success",
        "application": APP_NAME,
        "tagline": APP_TAGLINE,
        "version": current_app.config["APP_VERSION"],
        "environment": current_app.config["ENV_NAME"],
        "modules": list(MODULES),
        "datasets": {name: len(load_dataset_safe(name)) for name in DATASET_NAMES},
        "integrations": get_integration_status(),
    })
