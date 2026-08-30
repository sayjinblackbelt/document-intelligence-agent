# API — Document Intelligence Agent

## Run

```bash
pip install -r requirements.txt
uvicorn app.api:app --reload
```

Interactive documentation:

- `/docs`
- `/redoc`

## Endpoints

### GET /health
Checks service availability.

### POST /analyze/text
Analyzes text sent as JSON.

### POST /analyze/file
Uploads and analyzes `.txt`, text-extractable `.pdf`, or `.docx`.

### POST /analyze/ai
Runs deterministic analysis plus the selected provider.

Example:

```json
{
  "filename": "document.txt",
  "content": "REQUIREMENTS: register documents. RISK: delay.",
  "provider": "local",
  "language": "en"
}
```

Supported languages: `pt`, `en`, `es`.

### POST /analyze/ai/file
Uploads TXT/PDF/DOCX, extracts text, runs assisted analysis, and persists history.

Query parameters:

- `provider=local|openai|ollama`
- `language=pt|en|es`

### GET /history
Lists persisted analyses.

Optional filters:

- `limit`
- `provider`
- `priority`
- `filename`

### GET /history/{id}
Returns one persisted analysis.

### GET /history/{id}/export
Exports a saved analysis.

Supported formats:

- `json`
- `md`
- `pdf`

Example:

```
/history/12/export?format=pdf
```

## Current limits

This is a demonstration MVP. Scanned PDFs require OCR, and authentication, access control, retention policies, and sensitive-data controls should be implemented before production use.
