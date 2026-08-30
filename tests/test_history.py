from pathlib import Path

from app.history import get_analysis, list_analyses, save_analysis


def sample_base():
    return {
        "arquivo": "projeto.txt",
        "tipo_documento": "especificacao",
        "palavras_chave": {},
        "score_completude": 100,
        "caracteres": 42,
        "linhas": 1,
    }


def sample_assisted():
    return {
        "provider": "local",
        "resumo_executivo": "Resumo.",
        "requisitos": [],
        "pendencias": [],
        "riscos": [],
        "prioridade_sugerida": "baixa",
        "revisao_humana_recomendada": True,
    }


def test_save_and_get_analysis(tmp_path: Path):
    database = tmp_path / "history.db"

    saved = save_analysis(
        "projeto.txt",
        "local",
        sample_base(),
        sample_assisted(),
        database,
    )

    loaded = get_analysis(saved["id"], database)

    assert loaded is not None
    assert loaded["filename"] == "projeto.txt"
    assert loaded["provider"] == "local"
    assert loaded["analise_base"]["score_completude"] == 100


def test_list_analyses_returns_newest_first(tmp_path: Path):
    database = tmp_path / "history.db"

    first = save_analysis(
        "primeiro.txt", "local", sample_base(), sample_assisted(), database
    )
    second = save_analysis(
        "segundo.txt", "local", sample_base(), sample_assisted(), database
    )

    records = list_analyses(limit=10, database_path=database)

    assert len(records) == 2
    assert records[0]["id"] == second["id"]
    assert records[1]["id"] == first["id"]


def test_list_analyses_limits_results(tmp_path: Path):
    database = tmp_path / "history.db"

    for index in range(3):
        save_analysis(
            f"documento-{index}.txt",
            "local",
            sample_base(),
            sample_assisted(),
            database,
        )

    records = list_analyses(limit=2, database_path=database)

    assert len(records) == 2
