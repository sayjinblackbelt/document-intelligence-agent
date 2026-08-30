# Deploy

## Docker

```bash
docker build -t document-intelligence-agent .
docker run -p 8000:8000 -e DATABASE_PATH=/app/data/analyses.db document-intelligence-agent
```

Abra `http://localhost:8000`.

## Variáveis

Consulte `.env.example`:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`
- `DATABASE_PATH`

## Produção

Antes de receber documentos reais, implemente autenticação, autorização, rate limiting, HTTPS, retenção, backups, auditoria e controles adequados para dados sensíveis.

## Autenticação

Defina `DOCUMENT_AGENT_API_KEY` no ambiente de produção. Quando configurada, os endpoints de análise assistida e histórico exigem o header `X-API-Key`. O projeto mantém modo aberto apenas para demonstração local.
