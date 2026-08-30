"""Adaptadores para provedores de análise assistida por IA."""

import os
from abc import ABC, abstractmethod

import httpx

from .rules import KEYWORDS, find_keywords


class AIProvider(ABC):
    """Contrato comum para provedores de análise assistida."""

    name: str

    @abstractmethod
    def analyze(self, text: str) -> dict:
        """Retorna uma análise estruturada do texto."""


class LocalAIProvider(AIProvider):
    """Fallback determinístico sem dependências externas."""

    name = "local"

    def analyze(self, text: str) -> dict:
        keywords = find_keywords(text, KEYWORDS)
        requirements = keywords.get("requisitos", [])
        pending = keywords.get("pendencias", [])
        risks = keywords.get("riscos", [])

        summary_parts = []
        if requirements:
            summary_parts.append(
                f"Foram identificados {len(requirements)} indício(s) relacionado(s) a requisitos."
            )
        if pending:
            summary_parts.append(
                f"Foram identificados {len(pending)} indício(s) relacionado(s) a pendências."
            )
        if risks:
            summary_parts.append(
                f"Foram identificados {len(risks)} indício(s) relacionado(s) a riscos."
            )

        summary = " ".join(summary_parts) or (
            "Não foram identificados indícios suficientes pelas regras locais "
            "para gerar um resumo analítico."
        )

        priority = "baixa"
        if risks or pending:
            priority = "alta" if risks and pending else "média"

        return {
            "modo": "local-demonstrativo",
            "provider": self.name,
            "resumo_executivo": summary,
            "requisitos_contextuais": requirements,
            "pendencias_contextuais": pending,
            "riscos_contextuais": risks,
            "prioridade_sugerida": priority,
            "revisao_humana_recomendada": True,
        }


class OpenAIProvider(AIProvider):
    """Adaptador opcional para a API Chat Completions da OpenAI."""

    name = "openai"
    endpoint = "https://api.openai.com/v1/chat/completions"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.timeout = timeout

        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY não configurada. Defina a variável de ambiente "
                "para usar o provider 'openai'."
            )

    def analyze(self, text: str) -> dict:
        payload = {
            "model": self.model,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente de análise documental. "
                        "Produza uma resposta objetiva em português, destacando "
                        "requisitos, pendências, riscos e uma prioridade sugerida. "
                        "Não invente informações ausentes no documento."
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
            raise ValueError(
                f"Falha ao consultar o provider OpenAI: {error}"
            ) from error

        data = response.json()
        try:
            summary = data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, AttributeError) as error:
            raise ValueError(
                "Resposta inesperada recebida do provider OpenAI."
            ) from error

        return {
            "modo": "llm",
            "provider": self.name,
            "model": self.model,
            "resumo_executivo": summary,
            "revisao_humana_recomendada": True,
        }


def get_ai_provider(provider: str = "local") -> AIProvider:
    """Resolve um provider configurado pelo nome."""

    providers = {
        "local": LocalAIProvider,
        "openai": OpenAIProvider,
    }

    provider_class = providers.get(provider.lower())
    if not provider_class:
        available = ", ".join(sorted(providers))
        raise ValueError(
            f"Provedor não configurado: '{provider}'. "
            f"Disponíveis: {available}."
        )

    return provider_class()
