"""Geração de relatórios para análises documentais."""

import json
from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def save_report(results: list[dict], destination: Path) -> None:
    total = len(results)
    average_score = (
        sum(item["score_completude"] for item in results) / total
        if total
        else 0
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


def analysis_markdown(record: dict[str, Any]) -> str:
    assisted = record.get("analise_assistida", {})
    base = record.get("analise_base", {})

    def section(title: str, values: list[str]) -> str:
        lines = "\n".join(f"- {value}" for value in values) or "- Nenhum item identificado."
        return f"## {title}\n\n{lines}\n"

    return "\n".join(
        [
            "# Document Intelligence Agent — Analysis Report",
            "",
            f"**File:** {record.get('filename', '—')}",
            f"**Analysis ID:** {record.get('id', '—')}",
            f"**Created at:** {record.get('created_at', '—')}",
            f"**Provider:** {record.get('provider', '—')}",
            f"**Suggested priority:** {assisted.get('prioridade_sugerida', '—')}",
            "",
            "## Executive summary",
            "",
            assisted.get("resumo_executivo", "No summary available."),
            "",
            section("Requirements", assisted.get("requisitos", [])),
            section("Pending items", assisted.get("pendencias", [])),
            section("Risks", assisted.get("riscos", [])),
            "## Base analysis",
            "",
            f"- Document type: {base.get('tipo_documento', '—')}",
            f"- Completeness score: {base.get('score_completude', '—')}",
            "",
            "> Human review is recommended before technical or business decisions.",
            "",
        ]
    )


def analysis_json(record: dict[str, Any]) -> str:
    return json.dumps(record, ensure_ascii=False, indent=2)


def analysis_pdf(record: dict[str, Any]) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    for line in analysis_markdown(record).splitlines():
        if not line:
            story.append(Spacer(1, 8))
        elif line.startswith("# "):
            story.append(Paragraph(line[2:], styles["Title"]))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], styles["Heading2"]))
        elif line.startswith("- "):
            story.append(Paragraph("• " + line[2:], styles["BodyText"]))
        elif line.startswith("> "):
            story.append(Paragraph(line[2:], styles["Italic"]))
        else:
            story.append(Paragraph(line.replace("&", "&amp;"), styles["BodyText"]))

    document.build(story)
    return buffer.getvalue()
