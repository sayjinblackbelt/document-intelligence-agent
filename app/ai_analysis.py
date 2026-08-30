"""Optional assisted AI analysis layer."""

from .ai_providers import get_ai_provider


def local_ai_assist(text: str, language: str = "pt") -> dict:
    return get_ai_provider("local").analyze(text, language=language)


def analyze_with_ai(
    text: str,
    provider: str = "local",
    language: str = "pt",
) -> dict:
    return get_ai_provider(provider).analyze(text, language=language)
