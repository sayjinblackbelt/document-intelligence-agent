"""Contrato e validação para respostas estruturadas da camada de IA."""

import json
from typing import Any


PRIORITIES = {"baixa", "média", "alta"}


STRUCTURED_ANALYSIS_INSTRUCTIONS = """
Retorne exclusivamente um objeto JSON válido, sem Markdown e sem texto fora do JSON,
com exatamente esta estrutura:

{
  "resumo_executivo": "string",
  "requisitos": ["string"],
  "pendencias": ["string"],
  "riscos": ["string"],
  "prioridade_sugerida": "baixa | média | alta"
}

Use listas vazias quando não houver informação suficiente. Não invente informações.
""".strip()


def parse_structured_analysis(content: str) -> dict[str, Any]:
    """Converte e valida a resposta JSON produzida por um provider de LLM."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError(
            "O provider retornou uma resposta que não segue o contrato JSON estruturado."
        ) from error

    if not isinstance(data, dict):
        raise ValueError("A resposta estruturada do provider deve ser um objeto JSON.")

    summary = data.get("resumo_executivo", "")
    requirements = data.get("requisitos", [])
    pending = data.get("pendencias", [])
    risks = data.get("riscos", [])
    priority = data.get("prioridade_sugerida", "baixa")

    if not isinstance(summary, str):
        raise ValueError("'resumo_executivo' deve ser uma string.")

    for field, value in {
        "requisitos": requirements,
        "pendencias": pending,
        "riscos": risks,
    }.items():
        if not isinstance(value, list) or not all(
            isinstance(item, str) for item in value
        ):
            raise ValueError(f"'{field}' deve ser uma lista de strings.")

    if priority not in PRIORITIES:
        raise ValueError(
            "'prioridade_sugerida' deve ser uma destas opções: "
            + ", ".join(sorted(PRIORITIES))
            + "."
        )

    return {
        "resumo_executivo": summary.strip(),
        "requisitos": requirements,
        "pendencias": pending,
        "riscos": risks,
        "prioridade_sugerida": priority,
    }
