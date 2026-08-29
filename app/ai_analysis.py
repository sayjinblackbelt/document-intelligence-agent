"""Camada opcional de análise assistida por IA.

O MVP não depende de um provedor externo. A interface foi desenhada para
permitir futura integração com um LLM, mantendo uma implementação local
determinística como fallback.
"""

from .rules import KEYWORDS, find_keywords


def local_ai_assist(text: str) -> dict:
    """Gera uma análise assistida demonstrativa sem chamada externa."""
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
        "Não foram identificados indícios suficientes pelas regras locais para gerar um resumo analítico."
    )

    priority = "baixa"
    if risks or pending:
        priority = "alta" if risks and pending else "média"

    return {
        "modo": "local-demonstrativo",
        "resumo_executivo": summary,
        "requisitos_contextuais": requirements,
        "pendencias_contextuais": pending,
        "riscos_contextuais": risks,
        "prioridade_sugerida": priority,
        "revisao_humana_recomendada": True,
    }


def analyze_with_ai(text: str, provider: str = "local") -> dict:
    """Ponto único para futura integração com provedores de IA."""
    if provider == "local":
        return local_ai_assist(text)

    raise ValueError(
        "Provedor não configurado. Use 'local' no MVP ou implemente um adaptador externo."
    )
