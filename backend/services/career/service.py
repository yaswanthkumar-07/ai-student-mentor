"""Career exploration and recommendation service."""
from __future__ import annotations

import copy
import logging
from typing import Any

from ...utils.data_loader import get_by_id, load_dataset_safe, search_records

logger = logging.getLogger(__name__)


def get_all_careers(
    category: str | None = None,
    search: str | None = None,
    *,
    enrich: bool = False,
) -> list[dict[str, Any]]:
    """Return career paths, optionally filtered by category and search query."""
    careers = load_dataset_safe("careers")

    if category and category.strip() and category.lower() != "all":
        cat_lower = category.strip().lower()
        careers = [c for c in careers if c.get("category", "").lower() == cat_lower]

    if search and search.strip():
        careers = search_records(
            careers,
            search.strip(),
            ("title", "description", "category", "required_skills", "recommended_skills"),
        )

    if enrich:
        careers = [enrich_career(copy.deepcopy(c)) for c in careers]

    return careers


def get_career_by_id(career_id: str, *, enrich: bool = True) -> dict[str, Any] | None:
    """Return a single career by ID, optionally enriched with skill details."""
    raw = get_by_id("careers", career_id)
    if not raw:
        return None

    career = copy.deepcopy(raw)
    if enrich:
        career = enrich_career(career)
    return career


def get_career_categories() -> list[str]:
    """Return a sorted list of unique career categories."""
    careers = load_dataset_safe("careers")
    categories = {c.get("category") for c in careers if c.get("category")}
    return sorted(categories)


def enrich_career(career: dict[str, Any]) -> dict[str, Any]:
    """Attach full skill metadata and related career titles."""
    skills_map = {s["id"]: s for s in load_dataset_safe("skills")}
    careers_map = {c["id"]: c.get("title", c["id"]) for c in load_dataset_safe("careers")}

    career["required_skills_detail"] = [
        {
            "id": sid,
            "name": skills_map.get(sid, {}).get("name", sid.replace("_", " ").title()),
            "category": skills_map.get(sid, {}).get("category", "Technical"),
            "description": skills_map.get(sid, {}).get("description", ""),
        }
        for sid in career.get("required_skills", [])
    ]

    career["recommended_skills_detail"] = [
        {
            "id": sid,
            "name": skills_map.get(sid, {}).get("name", sid.replace("_", " ").title()),
            "category": skills_map.get(sid, {}).get("category", "General"),
            "description": skills_map.get(sid, {}).get("description", ""),
        }
        for sid in career.get("recommended_skills", [])
    ]

    career["related_careers_detail"] = [
        {
            "id": cid,
            "title": careers_map.get(cid, cid.replace("_", " ").title()),
        }
        for cid in career.get("related_careers", [])
    ]

    return career
