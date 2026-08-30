"""User persistence and password authentication."""

import os
import sqlite3
from pathlib import Path

from passlib.context import CryptContext

DEFAULT_DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "data/analyses.db"))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _connect(database_path=None):
    path = Path(database_path or DEFAULT_DATABASE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_users(database_path=None):
    with _connect(database_path) as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                is_active INTEGER NOT NULL DEFAULT 1
            )"""
        )


def create_user(username, password, role="user", database_path=None):
    initialize_users(database_path)
    with _connect(database_path) as connection:
        cursor = connection.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username.lower().strip(), pwd_context.hash(password), role),
        )
    return get_user_by_id(cursor.lastrowid, database_path)


def get_user_by_username(username, database_path=None):
    initialize_users(database_path)
    with _connect(database_path) as connection:
        return connection.execute(
            "SELECT * FROM users WHERE username = ?", (username.lower().strip(),)
        ).fetchone()


def get_user_by_id(user_id, database_path=None):
    initialize_users(database_path)
    with _connect(database_path) as connection:
        return connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def authenticate_user(username, password, database_path=None):
    user = get_user_by_username(username, database_path)
    if not user or not user["is_active"]:
        return None
    if not pwd_context.verify(password, user["password_hash"]):
        return None
    return user
