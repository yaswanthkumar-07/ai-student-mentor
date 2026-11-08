"""Skill gap analysis API routes."""
from __future__ import annotations

from flask import Blueprint, jsonify

from ..services.skills import analyze_skill_gap
from ..utils.responses import error, success

skill_gap_bp = Blueprint("skill_gap", __name__, url_prefix="/api/skill-gap")


@skill_gap_bp.get("/<student_id>")
def get_student_skill_gap_default(student_id: str):
    """Analyze skill gap against the student's primary career goal."""
    result = analyze_skill_gap(student_id, career_id=None)
    return jsonify({
        "status": "success",
        "data": result
    })


@skill_gap_bp.get("/<student_id>/<career_id>")
def get_student_skill_gap_for_career(student_id: str, career_id: str):
    """Analyze skill gap against a specific target career."""
    result = analyze_skill_gap(student_id, career_id=career_id)
    return jsonify({
        "status": "success",
        "data": result
    })
