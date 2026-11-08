"""Load and validate the JSON demonstration datasets in ``data/``.

Each file holds one top-level object whose collection key holds a list of
records (e.g. ``careers.json`` -> ``{"careers": [...]}``).

Run ``python -m backend.utils.data_loader`` to validate every dataset.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from ..config import DATA_DIR

logger = logging.getLogger(__name__)

DATASET_NAMES = ("students", "careers", "skills", "projects", "jobs", "roadmap",
                 "learning_resources")
# File name -> key that holds the record list inside the file.
COLLECTION_KEYS = {name: name for name in DATASET_NAMES} | {"roadmap": "roadmaps"}

REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "students": ("id", "name", "education", "interests", "skills", "career_goals"),
    "careers": ("id", "title", "category", "description", "required_skills",
                "prerequisites"),
    "skills": ("id", "name", "category", "skill_type", "description"),
    "projects": ("id", "title", "difficulty", "description", "technologies",
                 "required_skills", "estimated_completion", "career_ids"),
    "jobs": ("id", "title", "company", "location", "job_type", "experience_level",
             "required_skills", "application_url", "is_demo"),
    "roadmap": ("id", "career_id", "title", "stages"),
    "learning_resources": ("id", "title", "topic", "skill_ids", "resource_type",
                           "url", "difficulty"),
}
MIN_RECORDS = {"students": 5, "careers": 12, "skills": 30, "projects": 20,
               "jobs": 15, "roadmap": 8, "learning_resources": 20}


class DatasetError(Exception):
    """Raised when a dataset is missing or malformed."""


def _dataset_path(name: str, data_dir: Path | None) -> Path:
    if name not in COLLECTION_KEYS:
        raise DatasetError(f"Unknown dataset '{name}'.")
    return Path(data_dir or DATA_DIR) / f"{name}.json"


def load_dataset(name: str, *, data_dir: Path | None = None) -> list[dict[str, Any]]:
    """Return the records of a dataset or raise DatasetError."""
    path = _dataset_path(name, data_dir)
    if not path.is_file():
        raise DatasetError(f"Dataset file not found: {path.name}")
    try:
        with path.open(encoding="utf-8") as handle:
            content = json.load(handle)
    except json.JSONDecodeError as exc:
        raise DatasetError(f"{path.name} is not valid JSON: {exc}") from exc
    records = content.get(COLLECTION_KEYS[name]) if isinstance(content, dict) else None
    if not isinstance(records, list):
        raise DatasetError(f"{path.name} must contain a '{COLLECTION_KEYS[name]}' list.")
    return records


def load_dataset_safe(name: str, default: list | None = None) -> list[dict[str, Any]]:
    """Like load_dataset but logs and returns ``default`` (empty list) on failure."""
    try:
        return load_dataset(name)
    except DatasetError as exc:
        logger.error("Dataset '%s' unavailable: %s", name, exc)
        return [] if default is None else default


def get_by_id(name: str, record_id: str) -> dict[str, Any] | None:
    """Return one record by its ``id`` (or None)."""
    return next((r for r in load_dataset_safe(name) if r.get("id") == record_id), None)


def search_records(records: list[dict], query: str, fields: tuple[str, ...]) -> list[dict]:
    """Case-insensitive keyword search ranked by number of matching words."""
    tokens = [t for t in query.lower().split() if t]
    if not tokens:
        return list(records)
    scored = []
    for record in records:
        text = " ".join(
            " ".join(map(str, v)) if isinstance(v, list) else str(v)
            for v in (record.get(f, "") for f in fields)
        ).lower()
        score = sum(token in text for token in tokens)
        if score:
            scored.append((score, record))
    return [record for _, record in sorted(scored, key=lambda item: -item[0])]


def validate_dataset(name: str, *, data_dir: Path | None = None) -> list[str]:
    """Return a list of problems found in one dataset (empty list = valid)."""
    try:
        records = load_dataset(name, data_dir=data_dir)
    except DatasetError as exc:
        return [str(exc)]
    errors: list[str] = []
    if len(records) < MIN_RECORDS[name]:
        errors.append(f"{name}: expected at least {MIN_RECORDS[name]} records, "
                      f"found {len(records)}.")
    seen: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"{name}[{index}]: record must be an object.")
            continue
        missing = [f for f in REQUIRED_FIELDS[name] if f not in record]
        if missing:
            errors.append(f"{name}[{index}]: missing fields {missing}.")
        record_id = record.get("id")
        if record_id in seen:
            errors.append(f"{name}[{index}]: duplicate id '{record_id}'.")
        seen.add(record_id)
    return errors


def validate_relationships(*, data_dir: Path | None = None) -> list[str]:
    """Check that ids referenced across datasets actually exist."""
    try:
        ids = {n: {r["id"] for r in load_dataset(n, data_dir=data_dir)}
               for n in ("skills", "careers")}
        students = load_dataset("students", data_dir=data_dir)
        projects = load_dataset("projects", data_dir=data_dir)
        jobs = load_dataset("jobs", data_dir=data_dir)
        roadmaps = load_dataset("roadmap", data_dir=data_dir)
        resources = load_dataset("learning_resources", data_dir=data_dir)
        careers = load_dataset("careers", data_dir=data_dir)
    except (DatasetError, KeyError) as exc:
        return [f"Cannot check relationships: {exc}"]

    errors: list[str] = []

    def check(label: str, values, kind: str) -> None:
        for value in values:
            if value not in ids[kind]:
                errors.append(f"{label}: unknown {kind[:-1]} id '{value}'.")

    for c in careers:
        check(f"career {c['id']}", c["required_skills"] + c.get("recommended_skills", []), "skills")
    for s in students:
        check(f"student {s['id']}", [x["skill_id"] for x in s["skills"]], "skills")
        check(f"student {s['id']}", s["career_goals"], "careers")
    for p in projects:
        check(f"project {p['id']}", p["required_skills"], "skills")
        check(f"project {p['id']}", p["career_ids"], "careers")
    for j in jobs:
        check(f"job {j['id']}", j["required_skills"], "skills")
        check(f"job {j['id']}", [j["career_id"]] if j.get("career_id") else [], "careers")
    for r in roadmaps:
        check(f"roadmap {r['id']}", [r["career_id"]], "careers")
        check(f"roadmap {r['id']}", [s for st in r["stages"] for s in st["skills"]], "skills")
    for res in resources:
        check(f"resource {res['id']}", res["skill_ids"], "skills")
    return errors


def validate_all(*, data_dir: Path | None = None) -> dict[str, list[str]]:
    """Validate every dataset plus cross-dataset references."""
    report = {name: validate_dataset(name, data_dir=data_dir) for name in DATASET_NAMES}
    report["relationships"] = validate_relationships(data_dir=data_dir)
    return report


def main() -> int:
    """CLI entry point: print a validation report; non-zero exit on problems."""
    report = validate_all()
    failed = False
    for name, problems in report.items():
        count = "" if name == "relationships" else f" ({len(load_dataset_safe(name))} records)"
        print(f"{'OK  ' if not problems else 'FAIL'} {name}{count}")
        for problem in problems:
            print(f"     - {problem}")
        failed = failed or bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
