"""API REST demonstrativa para análise documental."""

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .analyzer import analyze_document, analyze_text_content
from .extractors import extract_text
from .ai_analysis import analyze_with_ai
from .history import get_analysis, list_analyses, save_analysis
from .report import analysis_json, analysis_markdown, analysis_pdf

ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
SUPPORTED_LANGUAGES = {"pt", "en", "es"}
SUPPORTED_PROVIDERS = {"local", "openai", "ollama"}


def validate_language(language: str) -> str:
    normalized = language.lower()
    if normalized not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail="Idiomas suportados: pt, en e es.")
    return normalized


def validate_provider(provider: str) -> str:
    normalized = provider.lower()
    if normalized not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail="Providers suportados: local, openai e ollama.")
    return normalized


async def read_upload(file: UploadFile) -> tuple[str, bytes]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Arquivo sem nome.")
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Formatos suportados: TXT, PDF e DOCX.")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Arquivo excede o limite de 10 MB.")
    return suffix, content

app = FastAPI(
    title="Document Intelligence Agent",
    description="API demonstrativa para classificação e análise inicial de documentos.",
    version="0.9.0",
)



class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        return response


app.add_middleware(SecurityHeadersMiddleware)

class AITextDocument(BaseModel):
    filename: str = "documento.txt"
    content: str
    provider: str = "local"
    language: str = "pt"


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
    suffix, content = await read_upload(file)

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
    language: str = "pt",
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

    provider = validate_provider(provider)
    language = validate_language(language)

    try:
        text = extract_text(temporary_path)
        if not text.strip():
            raise ValueError("Não foi possível extrair texto útil do arquivo.")

        base = analyze_text_content(text, file.filename)
        assisted = analyze_with_ai(text, provider, language)
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
        assisted = analyze_with_ai(document.content, document.provider, document.language)
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
    limit: int = Query(default=20, ge=1, le=100),
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


@app.get("/history/{analysis_id}/export")
def export_analysis(analysis_id: int, format: str = "json"):
    """Exporta uma análise persistida em JSON, Markdown ou PDF."""
    record = get_analysis(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Análise não encontrada.")

    normalized = format.lower()
    filename = Path(record["filename"]).stem or "analysis"

    if normalized == "json":
        return Response(
            analysis_json(record),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{filename}-analysis.json"'},
        )
    if normalized in {"md", "markdown"}:
        return Response(
            analysis_markdown(record),
            media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}-analysis.md"'},
        )
    if normalized == "pdf":
        return Response(
            analysis_pdf(record),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}-analysis.pdf"'},
        )

    raise HTTPException(
        status_code=400,
        detail="Formatos suportados: json, md e pdf.",
    )


STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def web_interface():
    return FileResponse(STATIC_DIR / "index.html")
