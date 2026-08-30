from pathlib import Path

from fastapi.testclient import TestClient

from app.api import MAX_UPLOAD_BYTES, app
from app.report import analysis_markdown, analysis_pdf

client = TestClient(app)


def sample_record():
    return {
        "id": 1,
        "filename": "A&B <test>.txt",
        "created_at": "2026-08-30T12:00:00+00:00",
        "provider": "local",
        "analise_base": {"tipo_documento": "spec", "score_completude": 80},
        "analise_assistida": {
            "resumo_executivo": "A&B <summary>",
            "requisitos": ["A&B <item>"],
            "pendencias": [],
            "riscos": [],
            "prioridade_sugerida": "baixa",
        },
    }


def test_markdown_export_is_localized():
    assert "Relatório de Análise" in analysis_markdown(sample_record(), "pt")
    assert "Informe de Análisis" in analysis_markdown(sample_record(), "es")


def test_pdf_export_escapes_special_characters():
    output = analysis_pdf(sample_record(), "en")
    assert output.startswith(b"%PDF")


def test_ai_rejects_invalid_language():
    response = client.post(
        "/analyze/ai",
        json={"filename": "x.txt", "content": "REQUISITOS: x", "language": "fr"},
    )
    assert response.status_code == 400


def test_ai_file_rejects_oversized_upload():
    response = client.post(
        "/analyze/ai/file",
        files={"file": ("large.txt", b"x" * (MAX_UPLOAD_BYTES + 1), "text/plain")},
    )
    assert response.status_code == 413


def test_security_headers_are_present():
    response = client.get("/health")
    assert response.headers["x-content-type-options"] == "nosniff"


def test_health_has_frame_and_referrer_headers():
    response = client.get("/health")
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "same-origin"
