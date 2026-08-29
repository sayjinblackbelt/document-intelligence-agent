# Arquitetura — Document Intelligence Agent

## Objetivo

Separar leitura, regras, análise e apresentação para que o MVP possa evoluir sem acoplamento excessivo.

## Camadas

```text
sample_data/
    ↓
app/analyzer.py
    ↓
app/rules.py
    ↓
app/report.py
    ↓
output/analysis_report.json
```

## Responsabilidades

### `rules.py`
Contém palavras-chave e regras de classificação.

### `analyzer.py`
Lê documentos e aplica as regras.

### `report.py`
Transforma os resultados em relatório JSON.

### `main.py`
Orquestra a execução do MVP.

## Evolução

A arquitetura foi desenhada para permitir a substituição ou complementação das regras por um serviço de IA.

```text
Documento
   ↓
Extração
   ↓
Regras determinísticas
   ↓
LLM / IA (futuro)
   ↓
Validação
   ↓
JSON / API
   ↓
Interface
```

## Princípios

- dados fictícios;
- resultados rastreáveis;
- regras explícitas;
- revisão humana;
- separação de responsabilidades.
