"""Processamento em lote para documentos enviados à API."""

from pathlib import Path
from typing import Any

from .ai_analysis import analyze_with_ai
from .analyzer import analyze_text_content
from .extractors import extract_text
from .history import save_analysis


def analyze_paths(
    files: list[tuple[Path, str]],
    provider: str,
    language: str,
    owner_id: str,
) -> dict[str, Any]:
    results = []
    errors = []
    for path, filename in files:
        try:
            text = extract_text(path)
            if not text.strip():
                raise ValueError("Nenhum texto útil encontrado.")
            base = analyze_text_content(text, filename)
            assisted = analyze_with_ai(text, provider, language)
            results.append(
                save_analysis(filename, provider, base, assisted, owner_id=owner_id)
            )
        except Exception as error:
            errors.append({"filename": filename, "error": str(error)})
    return {
        "processed": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors,
    }
