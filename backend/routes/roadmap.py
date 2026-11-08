"""Learning Roadmap API routes."""
from __future__ import annotations

from flask import Blueprint, jsonify

from ..services.roadmap import generate_personalized_roadmap
from ..utils.responses import error, success

roadmap_bp = Blueprint("roadmap", __name__, url_prefix="/api/roadmap")


@roadmap_bp.get("/<student_id>")
def get_student_roadmap_default(student_id: str):
    """Generate roadmap based on student's primary career goal."""
    result = generate_personalized_roadmap(student_id, career_id=None)
    return jsonify({
        "status": "success",
        "data": result
    })


@roadmap_bp.get("/<student_id>/<career_id>")
def get_student_roadmap_for_career(student_id: str, career_id: str):
    """Generate roadmap for a specific target career."""
    result = generate_personalized_roadmap(student_id, career_id=career_id)
    return jsonify({
        "status": "success",
        "data": result
    })
