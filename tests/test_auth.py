from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)

def test_auth_status_is_available():
    response = client.get("/auth/status")
    assert response.status_code == 200
    assert "authentication_enabled" in response.json()

def test_api_key_protects_history(monkeypatch):
    monkeypatch.setenv("DOCUMENT_AGENT_API_KEY", "test-secret")
    unauthorized = client.get("/history")
    assert unauthorized.status_code == 401
    authorized = client.get("/history", headers={"X-API-Key": "test-secret"})
    assert authorized.status_code == 200
