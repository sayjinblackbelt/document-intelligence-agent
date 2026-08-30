"""API REST demonstrativa para análise documental."""

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .analyzer import analyze_document, analyze_text_content
from .extractors import extract_text
from .ai_analysis import analyze_with_ai
from .history import get_analysis, list_analyses, save_analysis
from .auth import auth_status, login, require_user
from .users import create_user
from .report import analysis_json, analysis_markdown, analysis_pdf
from .dashboard import dashboard_metrics
from .batch import analyze_paths

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
    version="1.2.0",
)



class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next):
        import time

        client = request.client.host if request.client else "unknown"
        now = time.monotonic()
        timestamps = [
            timestamp for timestamp in self.requests.get(client, [])
            if now - timestamp < self.window_seconds
        ]
        if len(timestamps) >= self.limit:
            return Response(
                content='{"detail":"Limite de requisições excedido."}',
                status_code=429,
                media_type="application/json",
            )
        timestamps.append(now)
        self.requests[client] = timestamps
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        return response


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RateLimitMiddleware)

class AITextDocument(BaseModel):
    filename: str = "documento.txt"
    content: str
    provider: str = "local"
    language: str = "pt"


class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreateRequest(LoginRequest):
    role: str = "user"


class TextDocument(BaseModel):
    filename: str = "documento.txt"
    content: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "document-intelligence-agent"}


@app.get("/auth/status")
def auth_status_endpoint() -> dict:
    return auth_status()


@app.post("/auth/login")
def auth_login(credentials: LoginRequest) -> dict:
    return login(credentials.username, credentials.password)


@app.post("/auth/register")
def auth_register(payload: UserCreateRequest, request: Request) -> dict:
    current = require_user(request)
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado.")
    if payload.role not in {"admin", "user"}:
        raise HTTPException(status_code=400, detail="Perfil inválido.")
    if len(payload.username.strip()) < 3 or len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="Usuário ou senha não atendem aos requisitos mínimos.")
    try:
        user = create_user(payload.username, payload.password, payload.role)
        return {"id": user["id"], "username": user["username"], "role": user["role"]}
    except Exception as error:
        raise HTTPException(status_code=400, detail="Não foi possível criar o usuário.") from error


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
        raise HTTPException(status_code=400, detail="Não foi possível analisar o arquivo.") from error
    finally:
        temporary_path.unlink(missing_ok=True)


@app.post("/analyze/ai/file")
async def analyze_ai_file(
    request: Request,
    file: UploadFile,
    provider: str = "local",
    language: str = "pt",
) -> dict:
    """Extrai texto do arquivo, executa análise base e IA e persiste o resultado."""
    user = require_user(request)
    suffix, content = await read_upload(file)

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
            owner_id=user.user_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=400, detail="Não foi possível processar o arquivo.") from error
    finally:
        temporary_path.unlink(missing_ok=True)


@app.post("/analyze/ai/batch")
async def analyze_ai_batch(
    request: Request,
    files: list[UploadFile],
    provider: str = "local",
    language: str = "pt",
) -> dict:
    user = require_user(request)
    if not files or len(files) > 20:
        raise HTTPException(status_code=400, detail="Envie entre 1 e 20 arquivos.")
    provider = validate_provider(provider)
    language = validate_language(language)
    paths = []
    try:
        for file in files:
            suffix, content = await read_upload(file)
            temporary = NamedTemporaryFile(suffix=suffix, delete=False)
            temporary.write(content)
            temporary.close()
            paths.append(Path(temporary.name))
        result = analyze_paths(paths, provider, language, user.user_id)
        for item, file in zip(result["results"], files):
            item["uploaded_filename"] = file.filename
        return result
    finally:
        for path in paths:
            path.unlink(missing_ok=True)


@app.post("/analyze/ai")
def analyze_ai(document: AITextDocument, request: Request) -> dict:
    """Executa análise base e camada opcional de IA assistida."""
    user = require_user(request)
    try:
        provider = validate_provider(document.provider)
        language = validate_language(document.language)
        base = analyze_text_content(document.content, document.filename)
        assisted = analyze_with_ai(document.content, provider, language)
        record = save_analysis(
            filename=document.filename,
            provider=provider,
            base_analysis=base,
            assisted_analysis=assisted,
            owner_id=user.user_id,
        )
        return record
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/dashboard")
def dashboard(request: Request) -> dict:
    """Retorna métricas agregadas das análises do usuário autenticado."""
    user = require_user(request)
    records = list_analyses(limit=100, owner_id=user.user_id)
    return dashboard_metrics(records)


@app.get("/history")
def analysis_history(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    provider: str | None = None,
    priority: str | None = None,
    filename: str | None = None,
) -> list[dict]:
    """Lista análises recentes com filtros opcionais."""
    user = require_user(request)
    return list_analyses(
        limit=limit,
        provider=provider,
        priority=priority,
        filename=filename,
        owner_id=user.user_id,
    )


@app.get("/history/{analysis_id}")
def analysis_history_detail(analysis_id: int, request: Request) -> dict:
    """Retorna uma análise persistida pelo identificador."""
    user = require_user(request)
    record = get_analysis(analysis_id, owner_id=user.user_id)
    if not record:
        raise HTTPException(status_code=404, detail="Análise não encontrada.")
    return record


@app.get("/history/{analysis_id}/export")
def export_analysis(analysis_id: int, request: Request, format: str = "json", language: str = "pt"):
    """Exporta uma análise persistida em JSON, Markdown ou PDF."""
    user = require_user(request)
    record = get_analysis(analysis_id, owner_id=user.user_id)
    if not record:
        raise HTTPException(status_code=404, detail="Análise não encontrada.")

    normalized = format.lower()
    language = validate_language(language)
    filename = Path(record["filename"]).stem or "analysis"

    if normalized == "json":
        return Response(
            analysis_json(record),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{filename}-analysis.json"'},
        )
    if normalized in {"md", "markdown"}:
        return Response(
            analysis_markdown(record, language=language),
            media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}-analysis.md"'},
        )
    if normalized == "pdf":
        return Response(
            analysis_pdf(record, language=language),
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
