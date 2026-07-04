from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_contract():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "service" in payload
    assert "version" in payload
