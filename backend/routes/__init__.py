"""Blueprint registration. Later batches add one blueprint per module here."""
from flask import Flask

from .system import system_bp


def register_blueprints(app: Flask) -> None:
    """Attach every blueprint to the application."""
    app.register_blueprint(system_bp)
