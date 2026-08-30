"""Comparação entre análises documentais."""

from typing import Any


def compare_analyses(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    left_base = left.get("analise_base", {})
    right_base = right.get("analise_base", {})
    left_ai = left.get("analise_assistida", {})
    right_ai = right.get("analise_assistida", {})

    return {
        "left": {"id": left["id"], "filename": left["filename"]},
        "right": {"id": right["id"], "filename": right["filename"]},
        "completeness": {
            "left": left_base.get("score_completude"),
            "right": right_base.get("score_completude"),
            "difference": (left_base.get("score_completude") or 0) - (right_base.get("score_completude") or 0),
        },
        "document_type": {
            "left": left_base.get("tipo_documento"),
            "right": right_base.get("tipo_documento"),
        },
        "priority": {
            "left": left_ai.get("prioridade_sugerida"),
            "right": right_ai.get("prioridade_sugerida"),
        },
        "requirements": {
            "common": sorted(set(left_ai.get("requisitos", [])) & set(right_ai.get("requisitos", []))),
            "left_only": sorted(set(left_ai.get("requisitos", [])) - set(right_ai.get("requisitos", []))),
            "right_only": sorted(set(right_ai.get("requisitos", [])) - set(left_ai.get("requisitos", []))),
        },
    }
