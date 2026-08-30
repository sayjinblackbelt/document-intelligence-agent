from fastapi.testclient import TestClient

from app.api import app
from app.auth import create_access_token

client = TestClient(app)


def test_jwt_status(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    assert client.get("/auth/status").json()["jwt_enabled"] is True


def test_login_requires_valid_credentials(monkeypatch, tmp_path):
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    response = client.post("/auth/login", json={"username": "missing", "password": "password"})
    assert response.status_code == 401
