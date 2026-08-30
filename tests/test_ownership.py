from pathlib import Path

from app.history import get_analysis, list_analyses, save_analysis


def payload():
    return {"tipo_documento": "teste"}, {"resumo_executivo": "ok", "prioridade_sugerida": "baixa"}


def test_history_isolated_by_owner(tmp_path: Path):
    database = tmp_path / "history.db"
    base, assisted = payload()

    first = save_analysis("one.txt", "local", base, assisted, database, owner_id="alice")
    second = save_analysis("two.txt", "local", base, assisted, database, owner_id="bob")

    assert [item["id"] for item in list_analyses(database_path=database, owner_id="alice")] == [first["id"]]
    assert [item["id"] for item in list_analyses(database_path=database, owner_id="bob")] == [second["id"]]
    assert get_analysis(second["id"], database, owner_id="alice") is None
