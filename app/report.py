"""Geração de relatório JSON."""

import json
from pathlib import Path


def save_report(results: list[dict], destination: Path) -> None:
    total = len(results)
    average_score = (
        sum(item["score_completude"] for item in results) / total
        if total else 0
    )

    report = {
        "projeto": "Document Intelligence Agent",
        "finalidade": "Demonstração com dados fictícios",
        "documentos_analisados": total,
        "score_medio_completude": round(average_score, 1),
        "resultados": results,
    }

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
