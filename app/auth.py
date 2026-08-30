"""Autenticação e autorização baseada em usuários para o MVP."""

import hashlib
import os
import secrets
from dataclasses import dataclass

from fastapi import HTTPException, Request

API_KEY_ENV = "DOCUMENT_AGENT_API_KEY"


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: str
    role: str = "user"


def _legacy_fingerprint() -> str | None:
    key = os.getenv(API_KEY_ENV)
    if not key:
        return None
    return hashlib.sha256(key.encode()).hexdigest()[:12]


def api_key_enabled() -> bool:
    return bool(_legacy_fingerprint())


def require_user(request: Request) -> AuthenticatedUser:
    expected = os.getenv(API_KEY_ENV)
    if not expected:
        return AuthenticatedUser(user_id="local", role="admin")

    provided = request.headers.get("X-API-Key", "")
    if not provided or not secrets.compare_digest(provided, expected):
        raise HTTPException(status_code=401, detail="Não autorizado.")
    return AuthenticatedUser(user_id=_legacy_fingerprint() or "default", role="admin")


def require_api_key(request: Request) -> None:
    require_user(request)


def api_key_fingerprint() -> str | None:
    return _legacy_fingerprint()
