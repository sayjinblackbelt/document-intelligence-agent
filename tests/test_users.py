from pathlib import Path

from app.users import authenticate_user, create_user


def test_user_password_authentication(tmp_path: Path):
    database = tmp_path / "users.db"
    create_user("alice", "strong-password", database_path=database)
    assert authenticate_user("alice", "strong-password", database)
    assert authenticate_user("alice", "wrong-password", database) is None
