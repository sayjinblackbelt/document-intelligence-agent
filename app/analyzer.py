"""Motor de análise documental do MVP."""

from pathlib import Path

from .rules import KEYWORDS, classify_document, find_keywords


def analyze_document(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    found = find_keywords(text, KEYWORDS)
    classification = classify_document(text)

    populated_categories = sum(bool(items) for items in found.values())
    score = round(populated_categories / len(KEYWORDS) * 100)

    return {
        "arquivo": path.name,
        "tipo_documento": classification,
        "palavras_chave": found,
        "score_completude": score,
        "caracteres": len(text),
        "linhas": len(text.splitlines()),
    }


def analyze_directory(directory: Path) -> list[dict]:
    documents = sorted(directory.glob("*.txt"))
    return [analyze_document(path) for path in documents]
