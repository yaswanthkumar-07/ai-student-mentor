"""Tests for career exploration endpoints and career service."""
from backend.services.career import (
    get_all_careers,
    get_career_by_id,
    get_career_categories,
)


def test_list_careers_endpoint(client):
    response = client.get("/api/careers")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "careers" in data
    assert len(data["careers"]) >= 12
    first = data["careers"][0]
    assert "id" in first
    assert "title" in first
    assert "category" in first


def test_get_career_by_valid_id(client):
    response = client.get("/api/careers/data_scientist")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    career = data["career"]
    assert career["id"] == "data_scientist"
    assert career["title"] == "Data Scientist"
    assert "required_skills_detail" in career
    assert len(career["required_skills_detail"]) > 0


def test_get_career_not_found(client):
    response = client.get("/api/careers/non_existent_career")
    assert response.status_code == 404
    data = response.get_json()
    assert data["status"] == "error"
    assert "Career not found" in data["message"]


def test_filter_careers_by_category(client):
    response = client.get("/api/careers?category=Data%20%26%20AI")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    for career in data["careers"]:
        assert career["category"].lower() == "data & ai"


def test_search_careers(client):
    response = client.get("/api/careers?search=machine")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    titles = [c["title"].lower() for c in data["careers"]]
    assert any("machine learning" in t for t in titles)


def test_get_career_categories(client):
    response = client.get("/api/careers/categories")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "categories" in data
    assert "Data & AI" in data["categories"]


def test_career_service_get_by_id():
    career = get_career_by_id("devops_engineer")
    assert career is not None
    assert career["title"] == "DevOps Engineer"
    assert get_career_by_id("invalid_id") is None
