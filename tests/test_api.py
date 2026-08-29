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


def test_reject_non_txt_upload():
    response = client.post(
        "/analyze/file",
        files={"file": ("teste.pdf", b"conteudo", "application/pdf")},
    )
    assert response.status_code == 400
