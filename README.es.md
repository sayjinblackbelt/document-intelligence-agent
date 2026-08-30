# Agente de Inteligencia Documental

[🇧🇷 Português](README.md) | [🇺🇸 English](README.en.md) | 🇪🇸 Español

> Análisis documental estructurado con reglas determinísticas, IA asistida, historial persistente, exportaciones e interfaz web multilingüe.

## Funciones

- TXT, PDF con texto extraíble, PDF escaneado mediante OCR y DOCX;
- clasificación determinística, índice de completitud, requisitos, pendientes y riesgos;
- proveedores Local, OpenAI y Ollama;
- contrato JSON estructurado validado;
- historial SQLite con búsqueda y filtros;
- exportación JSON, Markdown y PDF;
- interfaz en portugués, inglés y español;
- FastAPI, pruebas, Docker y CI con GitHub Actions;\n- autenticación JWT/API Key, usuarios persistentes e historial aislado por usuario;\n- métricas de dashboard, análisis por lotes, comparación documental y eventos de auditoría estructurados.

## Inicio rápido

```bash
git clone https://github.com/sayjinblackbelt/document-intelligence-agent.git
cd document-intelligence-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.api:app --reload
```

Abra:

- Web: `http://127.0.0.1:8000/`
- Documentación API: `http://127.0.0.1:8000/docs`

## Análisis asistido

Seleccione `local`, `openai` u `ollama` y use `pt`, `en` o `es` desde la interfaz o la API.

Los análisis asistidos se guardan en SQLite y pueden consultarse, filtrarse y exportarse.

## API

- `GET /health`
- `POST /analyze/text`
- `POST /analyze/file`
- `POST /analyze/ai`
- `POST /analyze/ai/file`
- `GET /history`
- `GET /history/{id}`
- `GET /history/{id}/export?format=json|md|pdf`

Consulte la [documentación de la API](docs/API.md).

## Principio de diseño

La automatización apoya el análisis; la responsabilidad humana sigue siendo esencial para las validaciones y decisiones técnicas.

## Autor

**Filipe Gimenes de Morais**
