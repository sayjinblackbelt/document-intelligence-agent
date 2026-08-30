"""JWT authentication with local API-key compatibility."""

import os
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException, Request

from .users import authenticate_user

API_KEY_ENV = "DOCUMENT_AGENT_API_KEY"
JWT_SECRET_ENV = "JWT_SECRET"
JWT_ALGORITHM = "HS256"

@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: str
    role: str = "user"


def _jwt_secret():
    return os.getenv(JWT_SECRET_ENV)


def api_key_enabled():
    return bool(os.getenv(API_KEY_ENV))


def jwt_enabled():
    return bool(_jwt_secret())


def create_access_token(user_id: str, role: str):
    secret = _jwt_secret()
    if not secret:
        raise RuntimeError("JWT_SECRET não configurado.")
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.now(UTC) + timedelta(hours=8),
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def login(username: str, password: str):
    if not jwt_enabled():
        raise HTTPException(status_code=503, detail="Autenticação JWT não está configurada.")
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")
    return {
        "access_token": create_access_token(str(user["id"]), user["role"]),
        "token_type": "bearer",
        "role": user["role"],
    }


def require_user(request: Request):
    secret = _jwt_secret()
    auth_header = request.headers.get("Authorization", "")
    if secret and auth_header.startswith("Bearer "):
        token = auth_header.removeprefix("Bearer ").strip()
        try:
            payload = jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
            return AuthenticatedUser(str(payload["sub"]), payload.get("role", "user"))
        except jwt.PyJWTError as error:
            raise HTTPException(status_code=401, detail="Token inválido ou expirado.") from error

    expected = os.getenv(API_KEY_ENV)
    if expected:
        provided = request.headers.get("X-API-Key", "")
        if not provided or not secrets.compare_digest(provided, expected):
            raise HTTPException(status_code=401, detail="Não autorizado.")
        return AuthenticatedUser("legacy-api-key", "admin")

    return AuthenticatedUser("local", "admin")


def auth_status():
    return {"jwt_enabled": jwt_enabled(), "api_key_enabled": api_key_enabled()}
