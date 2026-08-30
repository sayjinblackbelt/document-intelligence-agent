"""Camada opcional de análise assistida por IA."""

from .ai_providers import get_ai_provider


def local_ai_assist(text: str) -> dict:
    """Compatibilidade com o modo local existente."""
    return get_ai_provider("local").analyze(text)


def analyze_with_ai(text: str, provider: str = "local") -> dict:
    """Executa a análise usando o adaptador do provider selecionado."""
    return get_ai_provider(provider).analyze(text)
