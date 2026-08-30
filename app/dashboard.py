"""Agregações para o dashboard de análises."""

from collections import Counter
from typing import Any


def dashboard_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    providers = Counter(record.get("provider", "unknown") for record in records)
    priorities = Counter(
        record.get("analise_assistida", {}).get("prioridade_sugerida", "unknown")
        for record in records
    )
    document_types = Counter(
        record.get("analise_base", {}).get("tipo_documento", "unknown")
        for record in records
    )
    scores = [
        record.get("analise_base", {}).get("score_completude")
        for record in records
        if isinstance(record.get("analise_base", {}).get("score_completude"), (int, float))
    ]
    return {
        "total_analyses": total,
        "average_completeness": round(sum(scores) / len(scores), 1) if scores else 0,
        "providers": dict(providers),
        "priorities": dict(priorities),
        "document_types": dict(document_types),
    }
