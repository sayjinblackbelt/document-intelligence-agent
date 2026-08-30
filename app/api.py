"""API REST demonstrativa para análise documental."""

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .analyzer import analyze_document, analyze_text_content
from .extractors import extract_text
from .ai_analysis import analyze_with_ai
from .history import get_analysis, list_analyses, save_analysis

app = FastAPI(
    title="Document Intelligence Agent",
    description="API demonstrativa para classificação e análise inicial de documentos.",
    version="0.6.0",
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


@app.post("/analyze/ai/file")
async def analyze_ai_file(
    file: UploadFile,
    provider: str = "local",
) -> dict:
    """Extrai texto do arquivo, executa análise base e IA e persiste o resultado."""
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
        text = extract_text(temporary_path)
        if not text.strip():
            raise ValueError("Não foi possível extrair texto útil do arquivo.")

        base = analyze_text_content(text, file.filename)
        assisted = analyze_with_ai(text, provider)
        return save_analysis(
            filename=file.filename,
            provider=provider,
            base_analysis=base,
            assisted_analysis=assisted,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Não foi possível processar o arquivo: {error}",
        ) from error
    finally:
        temporary_path.unlink(missing_ok=True)


@app.post("/analyze/ai")
def analyze_ai(document: AITextDocument) -> dict:
    """Executa análise base e camada opcional de IA assistida."""
    try:
        base = analyze_text_content(document.content, document.filename)
        assisted = analyze_with_ai(document.content, document.provider)
        record = save_analysis(
            filename=document.filename,
            provider=document.provider,
            base_analysis=base,
            assisted_analysis=assisted,
        )
        return record
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/history")
def analysis_history(
    limit: int = 20,
    provider: str | None = None,
    priority: str | None = None,
    filename: str | None = None,
) -> list[dict]:
    """Lista análises recentes com filtros opcionais."""
    return list_analyses(
        limit=limit,
        provider=provider,
        priority=priority,
        filename=filename,
    )


@app.get("/history/{analysis_id}")
def analysis_history_detail(analysis_id: int) -> dict:
    """Retorna uma análise persistida pelo identificador."""
    record = get_analysis(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Análise não encontrada.")
    return record


STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def web_interface():
    return FileResponse(STATIC_DIR / "index.html")
