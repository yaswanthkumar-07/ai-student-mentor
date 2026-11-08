"""Student service: retrieval and profile resolution for demo students."""
from __future__ import annotations

import copy
import logging
from typing import Any

from ...utils.data_loader import get_by_id, load_dataset_safe
from ...utils.errors import APIError

logger = logging.getLogger(__name__)


def get_all_students() -> list[dict[str, Any]]:
    """Return all student records."""
    return load_dataset_safe("students")


def get_student_by_id(student_id: str, *, enrich: bool = True) -> dict[str, Any] | None:
    """Return a single student profile by ID, optionally enriched with skill/career metadata."""
    raw = get_by_id("students", student_id)
    if not raw:
        return None
    
    student = copy.deepcopy(raw)
    if enrich:
        student = enrich_student_profile(student)
    return student


def enrich_student_profile(student: dict[str, Any]) -> dict[str, Any]:
    """Enrich skill IDs and career goal IDs with human-readable titles and metadata."""
    skills_map = {s["id"]: s for s in load_dataset_safe("skills")}
    careers_map = {c["id"]: c for c in load_dataset_safe("careers")}

    enriched_skills = []
    for item in student.get("skills", []):
        sid = item.get("skill_id")
        skill_meta = skills_map.get(sid, {})
        enriched_skills.append({
            "skill_id": sid,
            "name": skill_meta.get("name", sid.replace("_", " ").title()),
            "category": skill_meta.get("category", "General"),
            "skill_type": skill_meta.get("skill_type", "technical"),
            "level": item.get("level", "beginner"),
            "description": skill_meta.get("description", ""),
        })
    student["skills_detail"] = enriched_skills

    enriched_careers = []
    for cid in student.get("career_goals", []):
        career_meta = careers_map.get(cid, {})
        enriched_careers.append({
            "id": cid,
            "title": career_meta.get("title", cid.replace("_", " ").title()),
            "category": career_meta.get("category", "Other"),
            "description": career_meta.get("description", ""),
        })
    student["career_goals_detail"] = enriched_careers
    return student
