"""Blueprint registration. Attaches every feature blueprint to the Flask application."""
from flask import Flask

from .careers import careers_bp
from .roadmap import roadmap_bp
from .skill_gap import skill_gap_bp
from .students import students_bp
from .system import system_bp


def register_blueprints(app: Flask) -> None:
    """Attach every blueprint to the application."""
    app.register_blueprint(system_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(careers_bp)
    app.register_blueprint(skill_gap_bp)
    app.register_blueprint(roadmap_bp)
