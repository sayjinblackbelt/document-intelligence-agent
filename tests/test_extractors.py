from pathlib import Path

from docx import Document

from app.extractors import extract_text


def test_extract_txt(tmp_path: Path):
    path = tmp_path / "teste.txt"
    path.write_text("Documento de teste", encoding="utf-8")

    assert extract_text(path) == "Documento de teste"


def test_extract_docx(tmp_path: Path):
    path = tmp_path / "teste.docx"
    document = Document()
    document.add_paragraph("Requisito técnico de teste")
    document.save(path)

    assert "Requisito técnico" in extract_text(path)
