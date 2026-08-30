"""API REST demonstrativa para análise documental."""

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .analyzer import analyze_document, analyze_text_content
from .ai_analysis import analyze_with_ai

app = FastAPI(
    title="Document Intelligence Agent",
    description="API demonstrativa para classificação e análise inicial de documentos.",
    version="0.4.0",
)


class AITextDocument(BaseModel):
    filename: str = "documento.txt"
    content: str
    provider: str = "local"


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


@app.post("/analyze/ai")
def analyze_ai(document: AITextDocument) -> dict:
    """Executa análise base e camada opcional de IA assistida."""
    try:
        base = analyze_text_content(document.content, document.filename)
        assisted = analyze_with_ai(document.content, document.provider)
        return {
            "analise_base": base,
            "analise_assistida": assisted,
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def web_interface():
    return FileResponse(STATIC_DIR / "index.html")
