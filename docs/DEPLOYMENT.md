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
