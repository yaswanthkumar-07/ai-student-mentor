"""Career endpoints: career exploration, search, category filtering and details."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..services.career import (
    get_all_careers,
    get_career_by_id,
    get_career_categories,
)
from ..utils.responses import error, success

careers_bp = Blueprint("careers", __name__, url_prefix="/api/careers")


@careers_bp.get("")
@careers_bp.get("/")
def list_careers():
    """Return careers with optional category and search query filters."""
    category = request.args.get("category", default=None, type=str)
    search = request.args.get("search") or request.args.get("q")
    careers = get_all_careers(category=category, search=search)
    return jsonify({
        "status": "success",
        "count": len(careers),
        "careers": careers,
        "data": careers,
    })


@careers_bp.get("/categories")
def list_categories():
    """Return all unique career categories."""
    categories = get_career_categories()
    return jsonify({
        "status": "success",
        "count": len(categories),
        "categories": categories,
        "data": categories,
    })


@careers_bp.get("/<career_id>")
def get_career(career_id: str):
    """Return details for a single career path."""
    career = get_career_by_id(career_id)
    if not career:
        return error("Career not found", 404)
    return jsonify({
        "status": "success",
        "career": career,
        "data": career,
    })
