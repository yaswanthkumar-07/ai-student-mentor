"""Tests for demo student endpoints and student service."""
from backend.services.student import get_all_students, get_student_by_id


def test_list_students_endpoint(client):
    response = client.get("/api/students")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "students" in data
    assert len(data["students"]) >= 5
    first = data["students"][0]
    assert "id" in first
    assert "name" in first
    assert "education" in first
    assert "skills" in first


def test_get_student_by_valid_id(client):
    response = client.get("/api/students/stu_001")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    student = data["student"]
    assert student["id"] == "stu_001"
    assert student["name"] == "Ananya Reddy"
    assert "skills_detail" in student
    assert len(student["skills_detail"]) > 0
    assert "career_goals_detail" in student


def test_get_student_not_found(client):
    response = client.get("/api/students/stu_does_not_exist")
    assert response.status_code == 404
    data = response.get_json()
    assert data["status"] == "error"
    assert "Student not found" in data["message"]


def test_student_service_get_all():
    students = get_all_students()
    assert isinstance(students, list)
    assert len(students) >= 5
    ids = [s["id"] for s in students]
    assert "stu_001" in ids


def test_student_service_get_by_id():
    student = get_student_by_id("stu_002")
    assert student is not None
    assert student["name"] == "Rahul Verma"
    assert get_student_by_id("invalid_id") is None
