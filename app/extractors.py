"""Extração de texto para formatos suportados pelo agente."""

from pathlib import Path


SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx"}


def extract_text(path: Path) -> str:
    extension = path.suffix.lower()

    if extension == ".txt":
        return path.read_text(encoding="utf-8")

    if extension == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if extension == ".docx":
        from docx import Document

        document = Document(str(path))
        return "\n".join(
            paragraph.text for paragraph in document.paragraphs
        )

    raise ValueError(
        f"Formato não suportado: {extension or 'sem extensão'}"
    )
