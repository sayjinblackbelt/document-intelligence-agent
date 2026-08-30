# Arquitetura — Document Intelligence Agent

## Objetivo

Separar entrada, extração, regras, análise e apresentação para que o MVP possa evoluir sem acoplamento excessivo.

## Diagrama

![Arquitetura atual do Document Intelligence Agent](images/architecture.svg)

O diagrama acima representa a implementação atual. A camada de IA externa **não está implementada**: o MVP possui apenas o provider `local`, usado como demonstração e ponto de extensão para futuros adaptadores.

## Fluxo principal

```text
INTERFACE WEB / API REST
        ↓
FastAPI
        ↓
TXT / PDF / DOCX
        ↓
extractors.py
        ↓
analyzer.py
        ↓
rules.py
        ↓
resultado estruturado
        ↓
JSON / interface web
        ↓
revisão humana
```

A rota `/analyze/ai` adiciona uma camada opcional:

```text
texto
  ↓
análise base
  ↓
ai_analysis.py
  ↓
provider local demonstrativo
  ↓
resumo + prioridade sugerida
  ↓
revisão humana recomendada
```

## Componentes e responsabilidades

### `api.py`

Expõe a API FastAPI, recebe texto e arquivos, serve a interface web e orquestra as rotas:

- `GET /health`;
- `POST /analyze/text`;
- `POST /analyze/file`;
- `POST /analyze/ai`.

### `extractors.py`

Extrai texto dos formatos suportados:

- TXT;
- PDF via `pypdf`;
- DOCX via `python-docx`.

### `analyzer.py`

Centraliza a análise documental:

- análise de texto;
- análise de arquivo;
- análise de diretórios;
- cálculo do score de completude;
- composição do resultado estruturado.

### `rules.py`

Mantém regras explícitas e configuráveis para:

- classificação inicial do documento;
- identificação de requisitos;
- identificação de pendências;
- identificação de riscos.

### `ai_analysis.py`

Implementa a camada opcional de IA assistida do MVP.

Atualmente:

- funciona com `provider="local"`;
- não realiza chamadas externas;
- gera resumo executivo a partir das regras locais;
- sugere prioridade;
- marca a revisão humana como recomendada.

## Princípios

- resultados rastreáveis;
- regras explícitas;
- separação de responsabilidades;
- camada de IA desacoplada;
- evolução progressiva para provedores externos;
- revisão humana para interpretação e decisão técnica.
