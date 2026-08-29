# Document Intelligence Agent

> MVP demonstrativo para análise estruturada de documentos com Python, regras determinísticas e saída em JSON.

## Objetivo

Demonstrar como processos de análise documental podem ser parcialmente automatizados, reduzindo tarefas repetitivas e produzindo informações estruturadas para apoio à decisão.

## MVP atual

O agente:

- lê documentos de texto;
- identifica metadados básicos;
- procura requisitos, pendências e riscos por regras configuráveis;
- classifica o tipo de documento;
- calcula um score de completude;
- gera um relatório JSON.

## Arquitetura

```text
Documento
   ↓
Leitura
   ↓
Extração de metadados
   ↓
Regras de análise
   ├── requisitos
   ├── pendências
   └── riscos
   ↓
Score
   ↓
Relatório JSON
```

## Estrutura

```text
document-intelligence-agent/
├── app/
│   ├── analyzer.py
│   ├── rules.py
│   └── report.py
├── sample_data/
│   ├── document_01.txt
│   ├── document_02.txt
│   └── document_03.txt
├── output/
│   └── .gitkeep
├── tests/
│   └── test_analyzer.py
├── docs/
│   └── ARCHITECTURE.md
├── main.py
├── requirements.txt
└── README.md
```

## Execução

```bash
python main.py
```

O relatório será salvo em `output/analysis_report.json`.

## Princípio de projeto

A primeira versão é determinística. Isso permite resultados reproduzíveis, testes objetivos e rastreabilidade. A integração com IA poderá ser adicionada posteriormente sem substituir a camada de validação.

## Roadmap

1. MVP local;
2. testes automatizados;
3. FastAPI;
4. upload de documentos;
5. persistência;
6. integração com LLM;
7. interface web;
8. comparação entre versões.

## Confidencialidade

Todos os documentos de demonstração são fictícios. Nenhum conteúdo corporativo ou proprietário é utilizado.

## Tecnologias

Python · JSON · pytest (testes) · FastAPI (roadmap)
