"""Skill gap analysis service.

Compares student skills against target career requirements and recommended skills.
"""
from __future__ import annotations

import logging
from typing import Any

from ...utils.data_loader import get_by_id, load_dataset_safe
from ...utils.errors import APIError

logger = logging.getLogger(__name__)

# Proficiency rank map based on proficiency_scale in skills.json
PROFICIENCY_RANK = {
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3,
}


def analyze_skill_gap(student_id: str, career_id: str | None = None) -> dict[str, Any]:
    """Perform skill gap comparison for a student and a career.

    If career_id is None, uses the student's first career goal if available.
    """
    student = get_by_id("students", student_id)
    if not student:
        raise APIError(f"Student with ID '{student_id}' not found.", 404)

    if not career_id:
        goals = student.get("career_goals", [])
        if not goals:
            raise APIError("No target career specified and student has no career goals.", 400)
        career_id = goals[0]

    career = get_by_id("careers", career_id)
    if not career:
        raise APIError(f"Career with ID '{career_id}' not found.", 404)

    skills_map = {s["id"]: s for s in load_dataset_safe("skills")}
    resources = load_dataset_safe("learning_resources")

    # Map skill_id -> list of resources for actionable suggestions
    skill_resources_map: dict[str, list[dict]] = {}
    for res in resources:
        for sid in res.get("skill_ids", []):
            skill_resources_map.setdefault(sid, []).append({
                "title": res.get("title"),
                "provider": res.get("provider"),
                "type": res.get("resource_type"),
                "url": res.get("url"),
                "difficulty": res.get("difficulty")
            })

    # Student skills dict: skill_id -> level
    student_skills_dict = {
        item["skill_id"]: item.get("level", "beginner")
        for item in student.get("skills", [])
        if "skill_id" in item
    }

    required_skills_ids = career.get("required_skills", [])
    # Filter recommended skills to avoid duplicate classification with required
    recommended_skills_ids = [
        sid for sid in career.get("recommended_skills", [])
        if sid not in required_skills_ids
    ]

    acquired_skills: list[dict[str, Any]] = []
    needs_improvement: list[dict[str, Any]] = []
    missing_skills: list[dict[str, Any]] = []
    recommended_additional_skills: list[dict[str, Any]] = []

    # 1. Analyze Required Skills
    for sid in required_skills_ids:
        skill_info = skills_map.get(sid, {})
        skill_name = skill_info.get("name", sid.replace("_", " ").title())
        description = skill_info.get("description", "")
        available_resources = skill_resources_map.get(sid, [])

        if sid in student_skills_dict:
            curr_level = student_skills_dict[sid]
            rank = PROFICIENCY_RANK.get(curr_level.lower(), 1)
            # Intermediate or advanced is considered acquired; beginner for core required needs improvement
            if rank >= 2:
                acquired_skills.append({
                    "skill_id": sid,
                    "name": skill_name,
                    "description": description,
                    "current_level": curr_level,
                    "status": "acquired",
                    "type": "required",
                    "action": "Maintain mastery through advanced projects or mentoring.",
                    "resources": available_resources[:2]
                })
            else:
                needs_improvement.append({
                    "skill_id": sid,
                    "name": skill_name,
                    "description": description,
                    "current_level": curr_level,
                    "status": "needs_improvement",
                    "type": "required",
                    "action": f"Elevate proficiency from {curr_level} to intermediate/advanced.",
                    "resources": available_resources[:2]
                })
        else:
            missing_skills.append({
                "skill_id": sid,
                "name": skill_name,
                "description": description,
                "current_level": None,
                "status": "missing",
                "type": "required",
                "action": f"Start foundational study in {skill_name} as a core requirement.",
                "resources": available_resources[:2]
            })

    # 2. Analyze Recommended Skills
    for sid in recommended_skills_ids:
        skill_info = skills_map.get(sid, {})
        skill_name = skill_info.get("name", sid.replace("_", " ").title())
        description = skill_info.get("description", "")
        available_resources = skill_resources_map.get(sid, [])

        curr_level = student_skills_dict.get(sid)
        if curr_level:
            recommended_additional_skills.append({
                "skill_id": sid,
                "name": skill_name,
                "description": description,
                "current_level": curr_level,
                "status": "acquired",
                "type": "recommended",
                "action": f"Leverage existing {skill_name} skills for competitive advantage.",
                "resources": available_resources[:2]
            })
        else:
            recommended_additional_skills.append({
                "skill_id": sid,
                "name": skill_name,
                "description": description,
                "current_level": None,
                "status": "recommended_missing",
                "type": "recommended",
                "action": f"Optional growth area: explore {skill_name} after core requirements.",
                "resources": available_resources[:2]
            })

    total_required = len(required_skills_ids)
    # Coverage calculation:
    # acquired required counts as 1.0, needs_improvement counts as 0.5
    acquired_count = len(acquired_skills)
    needs_improvement_count = len(needs_improvement)
    missing_count = len(missing_skills)

    if total_required > 0:
        coverage_score = round(((acquired_count + (0.5 * needs_improvement_count)) / total_required) * 100, 1)
    else:
        coverage_score = 100.0

    return {
        "student": {
            "id": student.get("id"),
            "name": student.get("name"),
            "education": student.get("education")
        },
        "career": {
            "id": career.get("id"),
            "title": career.get("title"),
            "category": career.get("category"),
            "description": career.get("description")
        },
        "summary": {
            "total_required_skills": total_required,
            "acquired_count": acquired_count,
            "needs_improvement_count": needs_improvement_count,
            "missing_count": missing_count,
            "recommended_count": len(recommended_additional_skills),
            "coverage_percentage": coverage_score
        },
        "skills": {
            "acquired": acquired_skills,
            "needs_improvement": needs_improvement,
            "missing": missing_skills,
            "recommended": recommended_additional_skills
        }
    }
