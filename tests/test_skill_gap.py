"""Tests for Skill Gap Analysis module."""
import pytest
from backend.services.skills import analyze_skill_gap
from backend.utils.errors import APIError


def test_skill_gap_endpoint_valid_student_and_career(client):
    response = client.get("/api/skill-gap/stu_001/data_scientist")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    result = data["data"]
    assert result["student"]["id"] == "stu_001"
    assert result["career"]["id"] == "data_scientist"
    assert "summary" in result
    assert result["summary"]["total_required_skills"] == 6
    assert 0 <= result["summary"]["coverage_percentage"] <= 100
    assert "skills" in result
    assert "acquired" in result["skills"]
    assert "needs_improvement" in result["skills"]
    assert "missing" in result["skills"]
    assert "recommended" in result["skills"]


def test_skill_gap_endpoint_default_career(client):
    # stu_001 has career_goals = ['data_scientist']
    response = client.get("/api/skill-gap/stu_001")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["data"]["career"]["id"] == "data_scientist"


def test_skill_gap_endpoint_invalid_student(client):
    response = client.get("/api/skill-gap/non_existent_stu/data_scientist")
    assert response.status_code == 404
    data = response.get_json()
    assert data["status"] == "error"
    assert "not found" in data["message"].lower()


def test_skill_gap_endpoint_invalid_career(client):
    response = client.get("/api/skill-gap/stu_001/non_existent_career")
    assert response.status_code == 404
    data = response.get_json()
    assert data["status"] == "error"
    assert "not found" in data["message"].lower()


def test_skill_gap_classification_consistency():
    result = analyze_skill_gap("stu_001", "data_scientist")
    skills = result["skills"]
    # Verify no required skill is counted as missing recommended
    req_ids = {s["skill_id"] for s in skills["acquired"] + skills["needs_improvement"] + skills["missing"]}
    rec_ids = {s["skill_id"] for s in skills["recommended"]}
    assert req_ids.isdisjoint(rec_ids)

    # Check action strings and resources are present
    for category in ["acquired", "needs_improvement", "missing", "recommended"]:
        for s in skills[category]:
            assert "action" in s and s["action"]
            assert "resources" in s


def test_skill_gap_contract_schema(client):
    """Regression test ensuring API response contract has expected keys for frontend consumption."""
    response = client.get("/api/skill-gap/stu_001/data_scientist")
    data = response.get_json()
    assert "data" in data
    res = data["data"]
    # Required keys matching frontend adapter
    assert "career" in res
    assert "id" in res["career"] and "title" in res["career"] and "category" in res["career"]
    assert "summary" in res
    assert all(k in res["summary"] for k in [
        "total_required_skills", "acquired_count", "needs_improvement_count",
        "missing_count", "recommended_count", "coverage_percentage"
    ])
    assert "skills" in res
    assert all(k in res["skills"] for k in ["acquired", "needs_improvement", "missing", "recommended"])
