# Document Intelligence Agent

[🇧🇷 Português](README.md) | 🇺🇸 English | [🇪🇸 Español](README.es.md)

> Structured document analysis with deterministic rules, assisted AI, persistent history, exports, and a multilingual web interface.

## Features

- TXT, text-extractable PDF, scanned PDF via OCR, and DOCX;
- deterministic classification, completeness score, requirements, pending items, and risks;
- Local, OpenAI, and Ollama providers;
- validated structured JSON contract;
- SQLite analysis history with search and filters;
- JSON, Markdown, and PDF exports;
- web interface in Portuguese, English, and Spanish;
- FastAPI, tests, Docker, and GitHub Actions CI;\n- JWT/API-key authentication, persistent users, and user-owned history;\n- dashboard metrics, batch analysis, document comparison, and structured audit events.

## Quick start

```bash
git clone https://github.com/sayjinblackbelt/document-intelligence-agent.git
cd document-intelligence-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.api:app --reload
```

Open:

- Web: `http://127.0.0.1:8000/`
- API docs: `http://127.0.0.1:8000/docs`

## Assisted analysis

Select `local`, `openai`, or `ollama` and use `pt`, `en`, or `es` through the web interface or API.

Uploaded assisted analyses are persisted in SQLite and can be reopened, filtered, and exported.

## API

Main endpoints:

- `GET /health`
- `POST /analyze/text`
- `POST /analyze/file`
- `POST /analyze/ai`
- `POST /analyze/ai/file`
- `GET /history`
- `GET /history/{id}`
- `GET /history/{id}/export?format=json|md|pdf`

See [API documentation](docs/API.md).

## Design principle

Automation supports analysis; human responsibility remains essential for technical validation and decisions.

## Production note

This repository is a portfolio/demo project. Production use should add authentication, authorization, data retention, audit controls, and safeguards for sensitive documents.

## Author

**Filipe Gimenes de Morais**
