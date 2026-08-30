"""Geração de relatórios para análises documentais."""

import json
from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from xml.sax.saxutils import escape

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


def analysis_markdown(record: dict[str, Any], language: str = "en") -> str:
    language = language if language in {"pt", "en", "es"} else "en"
    labels = {
        "pt": {
            "report": "Relatório de Análise", "file": "Arquivo", "id": "ID da análise",
            "created": "Criado em", "provider": "Provider", "priority": "Prioridade sugerida",
            "summary": "Resumo executivo", "requirements": "Requisitos", "pending": "Pendências",
            "risks": "Riscos", "base": "Análise base", "type": "Tipo do documento",
            "score": "Score de completude", "none": "Nenhum item identificado.",
            "review": "A revisão humana é recomendada antes de decisões técnicas ou de negócio.",
        },
        "en": {
            "report": "Analysis Report", "file": "File", "id": "Analysis ID",
            "created": "Created at", "provider": "Provider", "priority": "Suggested priority",
            "summary": "Executive summary", "requirements": "Requirements", "pending": "Pending items",
            "risks": "Risks", "base": "Base analysis", "type": "Document type",
            "score": "Completeness score", "none": "No items identified.",
            "review": "Human review is recommended before technical or business decisions.",
        },
        "es": {
            "report": "Informe de Análisis", "file": "Archivo", "id": "ID del análisis",
            "created": "Creado en", "provider": "Proveedor", "priority": "Prioridad sugerida",
            "summary": "Resumen ejecutivo", "requirements": "Requisitos", "pending": "Pendientes",
            "risks": "Riesgos", "base": "Análisis base", "type": "Tipo de documento",
            "score": "Puntuación de completitud", "none": "No se identificaron elementos.",
            "review": "Se recomienda revisión humana antes de decisiones técnicas o de negocio.",
        },
    }[language]
    assisted = record.get("analise_assistida", {})
    base = record.get("analise_base", {})

    def section(title: str, values: list[str]) -> str:
        lines = "\n".join(f"- {value}" for value in values) or f"- {labels['none']}"
        return f"## {title}\n\n{lines}\n"

    return "\n".join(
        [
            f"# Document Intelligence Agent — {labels['report']}",
            "",
            f"**{labels['file']}:** {record.get('filename', '—')}",
            f"**{labels['id']}:** {record.get('id', '—')}",
            f"**{labels['created']}:** {record.get('created_at', '—')}",
            f"**{labels['provider']}:** {record.get('provider', '—')}",
            f"**{labels['priority']}:** {assisted.get('prioridade_sugerida', '—')}",
            "",
            f"## {labels['summary']}",
            "",
            assisted.get("resumo_executivo", "No summary available."),
            "",
            section(labels["requirements"], assisted.get("requisitos", [])),
            section(labels["pending"], assisted.get("pendencias", [])),
            section(labels["risks"], assisted.get("riscos", [])),
            f"## {labels['base']}",
            "",
            f"- {labels['type']}: {base.get('tipo_documento', '—')}",
            f"- {labels['score']}: {base.get('score_completude', '—')}",
            "",
            f"> {labels['review']}",
            "",
        ]
    )


def analysis_json(record: dict[str, Any]) -> str:
    return json.dumps(record, ensure_ascii=False, indent=2)


def analysis_pdf(record: dict[str, Any], language: str = "en") -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    for line in analysis_markdown(record, language=language).splitlines():
        if not line:
            story.append(Spacer(1, 8))
        elif line.startswith("# "):
            story.append(Paragraph(escape(line[2:]), styles["Title"]))
        elif line.startswith("## "):
            story.append(Paragraph(escape(line[3:]), styles["Heading2"]))
        elif line.startswith("- "):
            story.append(Paragraph("• " + escape(line[2:]), styles["BodyText"]))
        elif line.startswith("> "):
            story.append(Paragraph(escape(line[2:]), styles["Italic"]))
        else:
            story.append(Paragraph(escape(line), styles["BodyText"]))

    document.build(story)
    return buffer.getvalue()
