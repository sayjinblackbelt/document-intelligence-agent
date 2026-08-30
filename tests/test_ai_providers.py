import pytest

from app.ai_providers import LocalAIProvider, OpenAIProvider, get_ai_provider


def test_local_provider_returns_structured_analysis():
    result = LocalAIProvider().analyze(
        "REQUISITOS: registrar documentos. PENDÊNCIA: revisar. RISCO: atraso."
    )

    assert result["provider"] == "local"
    assert result["modo"] == "local-demonstrativo"
    assert result["prioridade_sugerida"] == "alta"
    assert result["revisao_humana_recomendada"] is True


def test_provider_factory_returns_local_provider():
    provider = get_ai_provider("local")

    assert isinstance(provider, LocalAIProvider)


def test_provider_factory_rejects_unknown_provider():
    with pytest.raises(ValueError, match="Provedor não configurado"):
        get_ai_provider("unknown")


def test_openai_provider_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        OpenAIProvider()


def test_openai_provider_sends_request_and_normalizes_response(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "choices": [
                    {"message": {"content": "Resumo gerado pelo modelo."}}
                ]
            }

    def fake_post(url, headers, json, timeout):
        assert url == OpenAIProvider.endpoint
        assert headers["Authorization"] == "Bearer test-key"
        assert json["model"] == "test-model"
        assert timeout == 30.0
        return FakeResponse()

    monkeypatch.setattr("app.ai_providers.httpx.post", fake_post)

    provider = OpenAIProvider(api_key="test-key", model="test-model")
    result = provider.analyze("Documento de teste.")

    assert result["provider"] == "openai"
    assert result["modo"] == "llm"
    assert result["model"] == "test-model"
    assert result["resumo_executivo"] == "Resumo gerado pelo modelo."
    assert result["revisao_humana_recomendada"] is True
