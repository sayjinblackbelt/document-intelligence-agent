"""Regras configuráveis para análise documental demonstrativa."""

DOCUMENT_TYPES = {
    "memorial": ["memorial", "objeto", "escopo"],
    "relatorio": ["relatório", "relatorio", "conclusão", "conclusao"],
    "especificacao": ["especificação", "especificacao", "requisito", "requisitos"],
}

KEYWORDS = {
    "requisitos": ["requisito", "requisitos", "deverá", "deverao", "necessário", "necessario"],
    "pendencias": ["pendente", "pendência", "pendencia", "aguardando", "a definir"],
    "riscos": ["risco", "risco alto", "incidente", "falha", "vazamento", "não conformidade", "nao conformidade"],
}


def classify_document(text: str) -> str:
    normalized = text.lower()
    scores = {
        name: sum(keyword in normalized for keyword in keywords)
        for name, keywords in DOCUMENT_TYPES.items()
    }
    best_type, best_score = max(scores.items(), key=lambda item: item[1])
    return best_type if best_score > 0 else "outro"


def find_keywords(text: str, dictionary: dict[str, list[str]]) -> dict[str, list[str]]:
    normalized = text.lower()
    found = {}
    for category, keywords in dictionary.items():
        found[category] = [keyword for keyword in keywords if keyword in normalized]
    return found
