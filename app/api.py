"""API REST demonstrativa para análise documental."""

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel

from .analyzer import analyze_document

app = FastAPI(
    title="Document Intelligence Agent",
    description="API demonstrativa para classificação e análise inicial de documentos.",
    version="0.2.0",
)


class TextDocument(BaseModel):
    filename: str = "documento.txt"
    content: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "document-intelligence-agent"}


@app.post("/analyze/text")
def analyze_text(document: TextDocument) -> dict:
    suffix = Path(document.filename).suffix or ".txt"

    with NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=suffix,
        delete=False,
    ) as temporary:
        temporary.write(document.content)
        temporary_path = Path(temporary.name)

    try:
        result = analyze_document(temporary_path)
        result["arquivo"] = document.filename
        return result
    finally:
        temporary_path.unlink(missing_ok=True)


@app.post("/analyze/file")
async def analyze_file(file: UploadFile) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Arquivo sem nome.")

    allowed_extensions = (".txt", ".pdf", ".docx")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail="Formatos suportados: TXT, PDF e DOCX.",
        )

    suffix = Path(file.filename).suffix.lower()
    content = await file.read()

    with NamedTemporaryFile(suffix=suffix, delete=False) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)

    try:
        result = analyze_document(temporary_path)
        result["arquivo"] = file.filename
        return result
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Não foi possível analisar o arquivo: {error}",
        ) from error
    finally:
        temporary_path.unlink(missing_ok=True)
