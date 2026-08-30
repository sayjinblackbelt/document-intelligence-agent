from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


def test_health_returns_service_status():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "document-intelligence-agent",
    }


def test_analyze_text_returns_document_analysis():
    response = client.post(
        "/analyze/text",
        json={
            "filename": "projeto.txt",
            "content": (
                "REQUISITOS: registrar documentos.\n"
                "PENDÊNCIA: revisar documento.\n"
                "RISCO: atraso.\n"
            ),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["arquivo"] == "projeto.txt"
    assert data["tipo_documento"] == "especificacao"
    assert data["score_completude"] == 100


def test_analyze_file_accepts_txt_upload():
    response = client.post(
        "/analyze/file",
        files={
            "file": (
                "documento.txt",
                b"REQUISITOS: registrar documentos.\nRISCO: atraso.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["arquivo"] == "documento.txt"
    assert "palavras_chave" in data


def test_analyze_file_rejects_unsupported_extension():
    response = client.post(
        "/analyze/file",
        files={
            "file": (
                "documento.md",
                b"# Documento",
                "text/markdown",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Formatos suportados: TXT, PDF e DOCX."


def test_analyze_ai_returns_base_and_assisted_analysis():
    response = client.post(
        "/analyze/ai",
        json={
            "filename": "projeto.txt",
            "content": "REQUISITOS: registrar documentos. PENDÊNCIA: revisar.",
            "provider": "local",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "analise_base" in data
    assert "analise_assistida" in data
    assert data["analise_assistida"]["modo"] == "local-demonstrativo"


def test_analyze_ai_rejects_unknown_provider():
    response = client.post(
        "/analyze/ai",
        json={
            "filename": "projeto.txt",
            "content": "Documento de teste.",
            "provider": "unknown",
        },
    )

    assert response.status_code == 400
    assert "Provedor não configurado" in response.json()["detail"]
