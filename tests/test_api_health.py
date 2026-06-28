from fastapi.testclient import TestClient

from backend.server import app


def test_api_health():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
