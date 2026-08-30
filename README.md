# Document Intelligence Agent

🇧🇷 Português | [🇺🇸 English](README.en.md) | [🇪🇸 Español](README.es.md)

[![CI](https://github.com/sayjinblackbelt/document-intelligence-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/sayjinblackbelt/document-intelligence-agent/actions/workflows/ci.yml)

> Análise estruturada de documentos com regras determinísticas, IA assistida, histórico persistente, exportação e interface multilíngue.

## Recursos

- 📄 TXT, PDF com texto e PDFs escaneados via OCR, e DOCX;
- 🔎 requisitos, pendências e riscos;
- 🏷️ classificação e score de completude;
- 🤖 providers Local, OpenAI e Ollama;
- 📋 contrato JSON estruturado validado;
- 🗃️ histórico SQLite com busca e filtros;
- 📤 exportação em JSON, Markdown e PDF;
- 🌐 interface em Português, English e Español;
- 🧪 testes automatizados;
- 🔄 CI com GitHub Actions;
- 🐳 Docker e healthcheck;
- 🔐 API Key opcional e JWT para usuários persistentes;
- 👥 isolamento do histórico por usuário.

## Início rápido

```bash
git clone https://github.com/sayjinblackbelt/document-intelligence-agent.git
cd document-intelligence-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.api:app --reload
```

No Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Abra:

- Interface: `http://127.0.0.1:8000/`
- Healthcheck: `http://127.0.0.1:8000/health`
- API: `http://127.0.0.1:8000/docs`

## Fluxo

```text
TXT / PDF / DOCX
        ↓
Extração de texto
        ↓
Análise determinística
        ↓
IA: Local / OpenAI / Ollama
        ↓
JSON estruturado
        ↓
SQLite
        ↓
Histórico, filtros e exportação
```

## Análise assistida

A interface permite selecionar:

- provider: `local`, `openai` ou `ollama`;
- idioma: `pt`, `en` ou `es`.

O resultado é salvo automaticamente no histórico.

## API

Principais endpoints:

- `GET /health`
- `POST /analyze/text`
- `POST /analyze/file`
- `POST /analyze/ai`
- `POST /analyze/ai/file`
- `GET /history`
- `GET /history/{id}`
- `GET /history/{id}/export?format=json|md|pdf`

Consulte [docs/API.md](docs/API.md).

## Testes

```bash
pytest -q
```

## Docker

```bash
docker build -t document-intelligence-agent .
docker run -p 8000:8000 document-intelligence-agent
```

## Autenticação

Para ambiente local, o projeto pode operar sem autenticação. Em deploy protegido, configure `JWT_SECRET` e use `POST /auth/login` para obter um Bearer token. O histórico é filtrado pelo usuário autenticado.

## OCR

PDFs sem texto extraível usam OCR como fallback. No Docker, Tesseract e Poppler são instalados automaticamente.

## Segurança

Este projeto é demonstrativo. Antes de uso em produção, recomenda-se implementar autenticação, autorização, retenção, auditoria e controles para documentos e dados sensíveis.

## Autor

**Filipe Gimenes de Morais**
