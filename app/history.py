"""Persistência SQLite para histórico de análises."""

import json
import os
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "data/analyses.db"))


def _connect(database_path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(database_path or DEFAULT_DATABASE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(database_path: Path | str | None = None) -> None:
    with _connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                filename TEXT NOT NULL,
                provider TEXT NOT NULL,
                owner_id TEXT NOT NULL DEFAULT "local",
                base_analysis TEXT NOT NULL,
                assisted_analysis TEXT NOT NULL
            )
            """
        )
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(analyses)")}
        if "owner_id" not in columns:
            connection.execute('ALTER TABLE analyses ADD COLUMN owner_id TEXT NOT NULL DEFAULT "local"')
        connection.execute("CREATE INDEX IF NOT EXISTS idx_analyses_provider ON analyses(provider)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_analyses_owner_id ON analyses(owner_id)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_analyses_filename ON analyses(filename)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at)")


def save_analysis(
    filename: str,
    provider: str,
    base_analysis: dict[str, Any],
    assisted_analysis: dict[str, Any],
    database_path: Path | str | None = None,
    owner_id: str = "local",
) -> dict[str, Any]:
    initialize_database(database_path)
    created_at = datetime.now(UTC).isoformat()

    with _connect(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO analyses (
                created_at, filename, provider, owner_id, base_analysis, assisted_analysis
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                created_at,
                filename,
                provider,
                owner_id,
                json.dumps(base_analysis, ensure_ascii=False),
                json.dumps(assisted_analysis, ensure_ascii=False),
            ),
        )
        analysis_id = cursor.lastrowid

    return get_analysis(analysis_id, database_path, owner_id=owner_id)


def _deserialize(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "filename": row["filename"],
        "provider": row["provider"],
        "owner_id": row["owner_id"],
        "analise_base": json.loads(row["base_analysis"]),
        "analise_assistida": json.loads(row["assisted_analysis"]),
    }


def list_analyses(
    limit: int = 20,
    provider: str | None = None,
    priority: str | None = None,
    filename: str | None = None,
    database_path: Path | str | None = None,
    owner_id: str | None = None,
) -> list[dict[str, Any]]:
    initialize_database(database_path)
    safe_limit = max(1, min(limit, 100))

    clauses: list[str] = []
    params: list[Any] = []

    if owner_id:
        clauses.append("owner_id = ?")
        params.append(owner_id)

    if provider:
        clauses.append("provider = ?")
        params.append(provider.lower())

    if filename:
        clauses.append("LOWER(filename) LIKE ?")
        params.append(f"%{filename.lower()}%")

    query = "SELECT * FROM analyses"
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY id DESC"

    with _connect(database_path) as connection:
        rows = connection.execute(query, params).fetchall()

    records = [_deserialize(row) for row in rows]
    if priority:
        normalized_priority = priority.lower()
        records = [
            record
            for record in records
            if record["analise_assistida"].get("prioridade_sugerida", "").lower()
            == normalized_priority
        ]

    return records[:safe_limit]


def get_analysis(
    analysis_id: int,
    database_path: Path | str | None = None,
    owner_id: str | None = None,
) -> dict[str, Any] | None:
    initialize_database(database_path)

    with _connect(database_path) as connection:
        query = "SELECT * FROM analyses WHERE id = ?"
        params: list[Any] = [analysis_id]
        if owner_id:
            query += " AND owner_id = ?"
            params.append(owner_id)
        row = connection.execute(query, params).fetchone()

    return _deserialize(row) if row else None
