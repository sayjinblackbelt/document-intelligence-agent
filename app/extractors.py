"""Extração de texto para formatos suportados pelo agente."""

from pathlib import Path


SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx"}


def extract_pdf_ocr(path: Path) -> str:
    try:
        import pytesseract
        from pdf2image import convert_from_path
    except ImportError as error:
        raise RuntimeError("Dependências de OCR não estão disponíveis.") from error

    images = convert_from_path(str(path), dpi=200)
    return "\n".join(pytesseract.image_to_string(image, lang="por+eng") for image in images)


def extract_text(path: Path) -> str:
    extension = path.suffix.lower()

    if extension == ".txt":
        return path.read_text(encoding="utf-8")

    if extension == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if text.strip():
            return text
        return extract_pdf_ocr(path)

    if extension == ".docx":
        from docx import Document

        document = Document(str(path))
        return "\n".join(
            paragraph.text for paragraph in document.paragraphs
        )

    raise ValueError(
        f"Formato não suportado: {extension or 'sem extensão'}"
    )
