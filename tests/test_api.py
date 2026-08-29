from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_text():
    response = client.post(
        "/analyze/text",
        json={
            "filename": "teste.txt",
            "content": "O requisito deverá ser validado. Pendência aguardando aprovação.",
        },
    )
    assert response.status_code == 200
    assert response.json()["arquivo"] == "teste.txt"


def test_reject_unsupported_upload():
    response = client.post(
        "/analyze/file",
        files={"file": ("teste.xlsx", b"conteudo", "application/octet-stream")},
    )
    assert response.status_code == 400


def test_analyze_ai():
    response = client.post(
        "/analyze/ai",
        json={
            "filename": "teste.txt",
            "content": "Existe um requisito, uma pendência e um risco.",
            "provider": "local",
        },
    )
    assert response.status_code == 200
    assert "analise_assistida" in response.json()
