from pathlib import Path

from app.analyzer import analyze_document, analyze_directory


def test_analyze_document_extracts_categories(tmp_path: Path):
    document = tmp_path / "example.txt"
    document.write_text(
        "REQUISITOS: registrar documentos.\n"
        "PENDÊNCIA: revisar documento.\n"
        "RISCO: atraso.\n",
        encoding="utf-8",
    )

    result = analyze_document(document)

    assert result["tipo_documento"] == "especificacao"
    assert result["score_completude"] == 100
    assert "requisitos" in result["palavras_chave"]
    assert "pendencias" in result["palavras_chave"]
    assert "riscos" in result["palavras_chave"]


def test_analyze_directory_reads_text_files(tmp_path: Path):
    (tmp_path / "a.txt").write_text("memorial do projeto", encoding="utf-8")
    (tmp_path / "b.txt").write_text("relatório de acompanhamento", encoding="utf-8")
    (tmp_path / "ignore.md").write_text("não ler", encoding="utf-8")

    results = analyze_directory(tmp_path)

    assert len(results) == 2
    assert {item["arquivo"] for item in results} == {"a.txt", "b.txt"}
