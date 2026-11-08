"""Student endpoints: demo profile listings and individual profile retrieval."""
from __future__ import annotations

from flask import Blueprint, jsonify

from ..services.student import get_all_students, get_student_by_id
from ..utils.responses import error, success

students_bp = Blueprint("students", __name__, url_prefix="/api/students")


@students_bp.get("")
@students_bp.get("/")
def list_students():
    """Return all demo student profiles."""
    students = get_all_students()
    return jsonify({
        "status": "success",
        "count": len(students),
        "students": students,
        "data": students,
    })


@students_bp.get("/<student_id>")
def get_student(student_id: str):
    """Return a single student profile by ID, enriched with details."""
    student = get_student_by_id(student_id)
    if not student:
        return error("Student not found", 404)
    return jsonify({
        "status": "success",
        "student": student,
        "data": student,
    })
