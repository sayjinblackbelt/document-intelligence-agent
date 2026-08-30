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


def test_analyze_ai_openai_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.post(
        "/analyze/ai",
        json={
            "filename": "projeto.txt",
            "content": "Documento de teste.",
            "provider": "openai",
        },
    )

    assert response.status_code == 400
    assert "OPENAI_API_KEY" in response.json()["detail"]


def test_analyze_ai_persists_history_record():
    response = client.post(
        "/analyze/ai",
        json={
            "filename": "historico.txt",
            "content": "REQUISITOS: registrar documentos.",
            "provider": "local",
        },
    )

    assert response.status_code == 200
    assert isinstance(response.json()["id"], int)

    history = client.get(f"/history/{response.json()['id']}")

    assert history.status_code == 200
    assert history.json()["filename"] == "historico.txt"


def test_history_returns_recent_analyses():
    response = client.get("/history?limit=5")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_history_returns_404_for_unknown_analysis():
    response = client.get("/history/999999")

    assert response.status_code == 404


def test_analyze_ai_file_accepts_txt_upload():
    response = client.post(
        "/analyze/ai/file?provider=local",
        files={
            "file": (
                "assistido.txt",
                b"REQUISITOS: registrar documentos. RISCO: atraso.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "assistido.txt"
    assert data["provider"] == "local"
    assert "analise_assistida" in data


def test_analyze_ai_file_rejects_unsupported_extension():
    response = client.post(
        "/analyze/ai/file",
        files={
            "file": (
                "assistido.md",
                b"# Documento",
                "text/markdown",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Formatos suportados: TXT, PDF e DOCX."


def test_history_export_supports_json_markdown_and_pdf():
    created = client.post(
        "/analyze/ai",
        json={
            "filename": "export.txt",
            "content": "REQUISITOS: registrar. RISCO: atraso.",
            "provider": "local",
        },
    ).json()

    for export_format, media_type in [
        ("json", "application/json"),
        ("md", "text/markdown"),
        ("pdf", "application/pdf"),
    ]:
        response = client.get(
            f"/history/{created['id']}/export?format={export_format}"
        )
        assert response.status_code == 200
        assert media_type in response.headers["content-type"]


def test_history_export_rejects_unknown_format():
    response = client.get("/history/1/export?format=xml")
    assert response.status_code == 400


def test_analyze_ai_accepts_language_selection():
    response = client.post(
        "/analyze/ai",
        json={
            "filename": "english.txt",
            "content": "REQUISITOS: registrar.",
            "provider": "local",
            "language": "en",
        },
    )
    assert response.status_code == 200
    assert "analysis identified" in response.json()["analise_assistida"]["resumo_executivo"].lower()
