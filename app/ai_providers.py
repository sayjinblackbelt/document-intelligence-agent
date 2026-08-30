"""Adapters for assisted document-analysis providers."""

import os
from abc import ABC, abstractmethod

import httpx

from .ai_schema import STRUCTURED_ANALYSIS_INSTRUCTIONS, parse_structured_analysis
from .rules import KEYWORDS, find_keywords


class AIProvider(ABC):
    name: str

    @abstractmethod
    def analyze(self, text: str, language: str = "pt") -> dict:
        """Return a structured analysis."""


class LocalAIProvider(AIProvider):
    name = "local"

    def analyze(self, text: str, language: str = "pt") -> dict:
        keywords = find_keywords(text, KEYWORDS)
        requirements = keywords.get("requisitos", [])
        pending = keywords.get("pendencias", [])
        risks = keywords.get("riscos", [])

        language = language if language in {"pt", "en", "es"} else "pt"
        messages = {
            "pt": {
                "prefix": "Foram identificados",
                "requirements": "requisito(s)",
                "pending": "pendência(s)",
                "risks": "risco(s)",
                "empty": "Não foram identificados indícios suficientes pelas regras locais para gerar um resumo analítico.",
            },
            "en": {
                "prefix": "The analysis identified",
                "requirements": "requirement(s)",
                "pending": "pending item(s)",
                "risks": "risk(s)",
                "empty": "The local rules did not identify enough indicators to generate an analytical summary.",
            },
            "es": {
                "prefix": "El análisis identificó",
                "requirements": "requisito(s)",
                "pending": "pendiente(s)",
                "risks": "riesgo(s)",
                "empty": "Las reglas locales no identificaron suficientes indicios para generar un resumen analítico.",
            },
        }[language]

        summary_parts = []
        if requirements:
            summary_parts.append(
                f"{messages['prefix']} {len(requirements)} {messages['requirements']}."
            )
        if pending:
            summary_parts.append(
                f"{messages['prefix']} {len(pending)} {messages['pending']}."
            )
        if risks:
            summary_parts.append(
                f"{messages['prefix']} {len(risks)} {messages['risks']}."
            )
        summary = " ".join(summary_parts) or messages["empty"]

        priority = "baixa"
        if risks or pending:
            priority = "alta" if risks and pending else "média"

        return {
            "modo": "local-demonstrativo",
            "provider": self.name,
            "resumo_executivo": summary,
            "requisitos": requirements,
            "pendencias": pending,
            "riscos": risks,
            "prioridade_sugerida": priority,
            "revisao_humana_recomendada": True,
        }


class OpenAIProvider(AIProvider):
    name = "openai"
    endpoint = "https://api.openai.com/v1/chat/completions"

    def __init__(self, api_key=None, model=None, timeout: float = 30.0) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.timeout = timeout
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY não configurada para o provider 'openai'.")

    def analyze(self, text: str, language: str = "pt") -> dict:
        language_name = {"pt": "Portuguese", "en": "English", "es": "Spanish"}.get(language, "Portuguese")
        payload = {
            "model": self.model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a document analysis assistant. Write summary and list values in "
                        + language_name
                        + ". Keep JSON keys and priority values exactly as specified. "
                        + STRUCTURED_ANALYSIS_INSTRUCTIONS
                    ),
                },
                {"role": "user", "content": text},
            ],
        }
        try:
            response = httpx.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise ValueError(f"Falha ao consultar o provider OpenAI: {error}") from error

        data = response.json()
        try:
            analysis = parse_structured_analysis(data["choices"][0]["message"]["content"])
        except (KeyError, IndexError, AttributeError) as error:
            raise ValueError("Resposta inesperada recebida do provider OpenAI.") from error

        return {
            "modo": "llm",
            "provider": self.name,
            "model": self.model,
            **analysis,
            "revisao_humana_recomendada": True,
        }


class OllamaProvider(AIProvider):
    name = "ollama"

    def __init__(self, base_url=None, model=None, timeout: float = 60.0) -> None:
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2")
        self.timeout = timeout

    def analyze(self, text: str, language: str = "pt") -> dict:
        language_name = {"pt": "Portuguese", "en": "English", "es": "Spanish"}.get(language, "Portuguese")
        payload = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a document analysis assistant. Write summary and list values in "
                        + language_name
                        + ". Keep JSON keys and priority values exactly as specified. "
                        + STRUCTURED_ANALYSIS_INSTRUCTIONS
                    ),
                },
                {"role": "user", "content": text},
            ],
        }
        try:
            response = httpx.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise ValueError(
                f"Falha ao consultar o Ollama em {self.base_url}: {error}"
            ) from error

        data = response.json()
        try:
            analysis = parse_structured_analysis(data["message"]["content"])
        except (KeyError, AttributeError) as error:
            raise ValueError("Resposta inesperada recebida do provider Ollama.") from error

        return {
            "modo": "llm-local",
            "provider": self.name,
            "model": self.model,
            **analysis,
            "revisao_humana_recomendada": True,
        }


def get_ai_provider(provider: str = "local") -> AIProvider:
    providers = {
        "local": LocalAIProvider,
        "openai": OpenAIProvider,
        "ollama": OllamaProvider,
    }
    provider_class = providers.get(provider.lower())
    if not provider_class:
        available = ", ".join(sorted(providers))
        raise ValueError(
            f"Provedor não configurado: '{provider}'. Disponíveis: {available}."
        )
    return provider_class()
