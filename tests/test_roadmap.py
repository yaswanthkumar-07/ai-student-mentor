"""Tests for Learning Roadmap module."""
import pytest
from backend.services.roadmap import generate_personalized_roadmap
from backend.utils.errors import APIError


def test_roadmap_endpoint_valid_student_and_career(client):
    response = client.get("/api/roadmap/stu_001/data_scientist")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    result = data["data"]
    assert result["student"]["id"] == "stu_001"
    assert result["career"]["id"] == "data_scientist"
    assert "stages" in result
    assert len(result["stages"]) > 0
    first_stage = result["stages"][0]
    assert "title" in first_stage
    assert "skills" in first_stage
    assert len(first_stage["skills"]) > 0
    first_skill = first_stage["skills"][0]
    assert "skill_id" in first_skill
    assert "status" in first_skill
    assert "resources" in first_skill


def test_roadmap_endpoint_default_career(client):
    response = client.get("/api/roadmap/stu_001")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["data"]["career"]["id"] == "data_scientist"


def test_roadmap_endpoint_invalid_student(client):
    response = client.get("/api/roadmap/invalid_stu/data_scientist")
    assert response.status_code == 404
    data = response.get_json()
    assert data["status"] == "error"
    assert "not found" in data["message"].lower()


def test_roadmap_endpoint_invalid_career(client):
    response = client.get("/api/roadmap/stu_001/invalid_career")
    assert response.status_code == 404
    data = response.get_json()
    assert data["status"] == "error"
    assert "not found" in data["message"].lower()


def test_roadmap_service_dynamic_fallback():
    # Test a career that is in careers.json but not in roadmap.json to verify dynamic generation
    result = generate_personalized_roadmap("stu_001", "mobile_app_developer")
    assert result is not None
    assert "stages" in result
    assert result["total_stages"] >= 1
    # Check that resources only contain HTTPS URLs
    for st in result["stages"]:
        for s in st["skills"]:
            for r in s.get("resources", []):
                assert r["url"].startswith("https://")


def test_roadmap_contract_schema(client):
    """Regression test ensuring API response contract has expected keys for frontend consumption."""
    response = client.get("/api/roadmap/stu_001/data_scientist")
    data = response.get_json()
    assert "data" in data
    res = data["data"]
    assert "career" in res
    assert "title" in res
    assert "total_stages" in res
    assert "total_tasks" in res
    assert "stages" in res
    assert isinstance(res["stages"], list)
    for stage in res["stages"]:
        assert "order" in stage
        assert "title" in stage
        assert "skills" in stage
        for skill in stage["skills"]:
            assert "skill_id" in skill
            assert "name" in skill
            assert "status" in skill
            assert "resources" in skill
