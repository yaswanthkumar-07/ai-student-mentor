from backend.config import MODULES


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {
        "status": "success",
        "application": "AI Student Mentor",
        "message": "Backend is running",
    }


def test_info_endpoint(client):
    data = client.get("/api/info").get_json()
    assert data["status"] == "success"
    assert data["application"] == "AI Student Mentor"
    assert data["modules"] == list(MODULES) and len(data["modules"]) == 8
    assert all(count > 0 for count in data["datasets"].values())
    assert set(data["integrations"]) == {"esco", "github", "youtube", "jobs", "gemini"}


def test_info_never_exposes_secrets(client, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "super-secret-value")
    assert "super-secret-value" not in client.get("/api/info").get_data(as_text=True)


def test_unknown_route_returns_json_404(client):
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404
    assert response.get_json()["status"] == "error"


def test_cors_header_present(client):
    response = client.get("/api/health", headers={"Origin": "http://localhost:5500"})
    assert response.headers.get("Access-Control-Allow-Origin") in ("*", "http://localhost:5500")
