"""Motor de análise documental."""

from pathlib import Path

from .extractors import SUPPORTED_EXTENSIONS, extract_text
from .rules import KEYWORDS, classify_document, find_keywords


def analyze_text_content(text: str, filename: str = "documento") -> dict:
    found = find_keywords(text, KEYWORDS)
    classification = classify_document(text)

    populated_categories = sum(bool(items) for items in found.values())
    score = round(populated_categories / len(KEYWORDS) * 100)

    return {
        "arquivo": filename,
        "tipo_documento": classification,
        "palavras_chave": found,
        "score_completude": score,
        "caracteres": len(text),
        "linhas": len(text.splitlines()),
    }


def analyze_document(path: Path) -> dict:
    text = extract_text(path)
    return analyze_text_content(text, path.name)


def analyze_directory(directory: Path) -> list[dict]:
    documents = sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    return [analyze_document(path) for path in documents]
