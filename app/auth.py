"""Autenticação simples baseada em API key para o MVP."""

import hashlib
import os
import secrets

from fastapi import HTTPException, Request

API_KEY_ENV = "DOCUMENT_AGENT_API_KEY"

def api_key_enabled() -> bool:
    return bool(os.getenv(API_KEY_ENV))

def require_api_key(request: Request) -> None:
    expected = os.getenv(API_KEY_ENV)
    if not expected:
        return
    provided = request.headers.get("X-API-Key", "")
    if not provided or not secrets.compare_digest(provided, expected):
        raise HTTPException(status_code=401, detail="Não autorizado.")

def api_key_fingerprint() -> str | None:
    key = os.getenv(API_KEY_ENV)
    if not key:
        return None
    return hashlib.sha256(key.encode()).hexdigest()[:12]
