from app.report import analysis_json, analysis_markdown, analysis_pdf


def record():
    return {
        "id": 1,
        "filename": "teste.txt",
        "created_at": "2026-08-30T12:00:00+00:00",
        "provider": "local",
        "analise_base": {"tipo_documento": "especificacao", "score_completude": 100},
        "analise_assistida": {
            "resumo_executivo": "Resumo de teste.",
            "requisitos": ["Registrar"],
            "pendencias": ["Revisar"],
            "riscos": ["Atraso"],
            "prioridade_sugerida": "alta",
        },
    }


def test_analysis_json_exports_record():
    assert '"filename": "teste.txt"' in analysis_json(record())


def test_analysis_markdown_exports_sections():
    output = analysis_markdown(record())
    assert "# Document Intelligence Agent" in output
    assert "## Requirements" in output
    assert "## Risks" in output


def test_analysis_pdf_returns_pdf_bytes():
    output = analysis_pdf(record())
    assert output.startswith(b"%PDF")
