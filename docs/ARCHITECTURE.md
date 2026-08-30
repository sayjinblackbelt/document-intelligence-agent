# Arquitetura — Document Intelligence Agent

## Visão geral

Web UI / REST API → FastAPI → validação de upload → extração TXT/PDF/DOCX → análise determinística → Local/OpenAI/Ollama → JSON validado → SQLite → histórico, filtros e exportação.

## Camadas

- **API (`api.py`)**: valida entrada, orquestra fluxos e serve a interface.
- **Extraction (`extractors.py`)**: TXT, PDF com texto e DOCX.
- **Analysis (`analyzer.py`, `rules.py`)**: classificação e indicadores explícitos.
- **AI (`ai_analysis.py`, `ai_providers.py`, `ai_schema.py`)**: providers desacoplados e contrato JSON validado.
- **Persistence (`history.py`)**: SQLite e filtros.
- **Reporting (`report.py`)**: JSON, Markdown e PDF.
- **Web (`static/`)**: interface responsiva em PT/EN/ES.

## Princípios

- separação de responsabilidades;
- regras rastreáveis;
- validação de contrato;
- limites explícitos de entrada;
- revisão humana para decisões;
- evolução incremental para produção.

## Limitações atuais

PDFs escaneados ainda precisam de OCR. O SQLite é adequado ao MVP; produção multiusuário deve considerar banco gerenciado, autenticação e auditoria.
