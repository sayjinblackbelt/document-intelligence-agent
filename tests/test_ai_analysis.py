from app.ai_analysis import analyze_with_ai


def test_local_ai_analysis():
    result = analyze_with_ai(
        "O requisito deverá ser validado. Existe uma pendência e um risco operacional."
    )

    assert result["modo"] == "local-demonstrativo"
    assert result["revisao_humana_recomendada"] is True
    assert result["prioridade_sugerida"] in {"baixa", "média", "alta"}
