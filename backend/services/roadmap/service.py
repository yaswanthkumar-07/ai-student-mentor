"""Roadmap service.

Generates a personalized stage-by-stage learning roadmap based on student skill gaps.
"""
from __future__ import annotations

import copy
import logging
from typing import Any

from ...utils.data_loader import get_by_id, load_dataset_safe
from ...utils.errors import APIError
from ..skills.service import analyze_skill_gap

logger = logging.getLogger(__name__)


def generate_personalized_roadmap(student_id: str, career_id: str | None = None) -> dict[str, Any]:
    """Generate a personalized roadmap tailored to the student's skill gap.

    Incorporates curriculum stages from roadmap.json and resources from learning_resources.json.
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

    # Perform skill gap analysis
    gap_analysis = analyze_skill_gap(student_id, career_id)
    skills_classified = gap_analysis["skills"]

    # Build quick lookup of student status per skill
    acquired_ids = {s["skill_id"] for s in skills_classified["acquired"]}
    needs_imp_ids = {s["skill_id"] for s in skills_classified["needs_improvement"]}
    missing_ids = {s["skill_id"] for s in skills_classified["missing"]}

    # Load resources map: skill_id -> list of resources
    all_resources = load_dataset_safe("learning_resources")
    skill_res_map: dict[str, list[dict]] = {}
    for res in all_resources:
        for sid in res.get("skill_ids", []):
            skill_res_map.setdefault(sid, []).append({
                "id": res.get("id"),
                "title": res.get("title"),
                "provider": res.get("provider"),
                "resource_type": res.get("resource_type"),
                "url": res.get("url"),
                "difficulty": res.get("difficulty")
            })

    skills_map = {s["id"]: s for s in load_dataset_safe("skills")}

    # Find matching curated roadmap from roadmap.json if available
    roadmaps = load_dataset_safe("roadmap")
    matching_roadmap = next((r for r in roadmaps if r.get("career_id") == career_id), None)

    stages_data: list[dict[str, Any]] = []

    if matching_roadmap and matching_roadmap.get("stages"):
        raw_stages = sorted(matching_roadmap["stages"], key=lambda st: st.get("order", 0))
        for st in raw_stages:
            stage_skills = []
            for sid in st.get("skills", []):
                s_info = skills_map.get(sid, {})
                s_name = s_info.get("name", sid.replace("_", " ").title())
                
                # Determine status for this student
                if sid in acquired_ids:
                    status = "acquired"
                    badge_label = "Mastered"
                elif sid in needs_imp_ids:
                    status = "needs_improvement"
                    badge_label = "Level Up"
                elif sid in missing_ids:
                    status = "missing"
                    badge_label = "To Learn"
                else:
                    status = "elective"
                    badge_label = "Elective"

                stage_skills.append({
                    "skill_id": sid,
                    "name": s_name,
                    "description": s_info.get("description", ""),
                    "category": s_info.get("category", "Technical"),
                    "status": status,
                    "badge_label": badge_label,
                    "resources": skill_res_map.get(sid, [])
                })

            stages_data.append({
                "order": st.get("order"),
                "title": st.get("title"),
                "estimated_weeks": st.get("estimated_weeks", 4),
                "milestones": st.get("milestones", []),
                "skills": stage_skills
            })
    else:
        # Fallback dynamic stage grouping if no curated roadmap file entry
        # 1. Foundation (missing foundational/general)
        # 2. Core Requirements (missing & needs improvement)
        # 3. Advanced & Recommended
        stage_1_skills = []
        stage_2_skills = []
        stage_3_skills = []

        for item in skills_classified["missing"]:
            sid = item["skill_id"]
            s_info = skills_map.get(sid, {})
            stage_entry = {
                "skill_id": sid,
                "name": item["name"],
                "description": item["description"],
                "category": s_info.get("category", "General"),
                "status": "missing",
                "badge_label": "To Learn",
                "resources": skill_res_map.get(sid, [])
            }
            if s_info.get("category") in ("Programming", "Foundations"):
                stage_1_skills.append(stage_entry)
            else:
                stage_2_skills.append(stage_entry)

        for item in skills_classified["needs_improvement"]:
            sid = item["skill_id"]
            s_info = skills_map.get(sid, {})
            stage_2_skills.append({
                "skill_id": sid,
                "name": item["name"],
                "description": item["description"],
                "category": s_info.get("category", "General"),
                "status": "needs_improvement",
                "badge_label": "Level Up",
                "resources": skill_res_map.get(sid, [])
            })

        for item in skills_classified["recommended"]:
            sid = item["skill_id"]
            s_info = skills_map.get(sid, {})
            stage_3_skills.append({
                "skill_id": sid,
                "name": item["name"],
                "description": item["description"],
                "category": s_info.get("category", "General"),
                "status": item["status"],
                "badge_label": "Recommended",
                "resources": skill_res_map.get(sid, [])
            })

        order_idx = 1
        if stage_1_skills:
            stages_data.append({
                "order": order_idx,
                "title": "Foundation & Prerequisites",
                "estimated_weeks": 4,
                "milestones": ["Build fundamental proficiency in key technologies"],
                "skills": stage_1_skills
            })
            order_idx += 1
        if stage_2_skills:
            stages_data.append({
                "order": order_idx,
                "title": "Core Technical Mastery",
                "estimated_weeks": 6,
                "milestones": ["Close required skill gaps for the role"],
                "skills": stage_2_skills
            })
            order_idx += 1
        if stage_3_skills:
            stages_data.append({
                "order": order_idx,
                "title": "Specialization & Recommended Electives",
                "estimated_weeks": 4,
                "milestones": ["Gain competitive edge with supplementary skills"],
                "skills": stage_3_skills
            })

    total_tasks = sum(len(st["skills"]) for st in stages_data)

    return {
        "student": {
            "id": student.get("id"),
            "name": student.get("name")
        },
        "career": {
            "id": career.get("id"),
            "title": career.get("title"),
            "category": career.get("category")
        },
        "roadmap_id": matching_roadmap.get("id") if matching_roadmap else f"dynamic_{career_id}",
        "title": matching_roadmap.get("title", f"{career.get('title')} Learning Path") if matching_roadmap else f"{career.get('title')} Roadmap",
        "total_stages": len(stages_data),
        "total_tasks": total_tasks,
        "stages": stages_data
    }
