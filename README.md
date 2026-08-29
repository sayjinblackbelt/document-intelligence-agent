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


## API REST

A versão atual também disponibiliza uma API FastAPI.

```bash
pip install -r requirements.txt
uvicorn app.api:app --reload
```

Endpoints iniciais:

- `GET /health`
- `POST /analyze/text`
- `POST /analyze/file`

A documentação interativa é fornecida automaticamente pelo FastAPI em `/docs`.

Veja também:

- [Documentação da API](docs/API.md)
- [Roadmap](docs/ROADMAP.md)

## Evolução do projeto

```text
MVP Python ✓
      ↓
API REST ✓
      ↓
PDF / DOCX
      ↓
IA assistida
      ↓
Interface Web
```


## Suporte a documentos

O agente agora suporta:

- **TXT**
- **PDF com texto extraível**
- **DOCX**

A extração ocorre antes da análise, permitindo que o mesmo motor de regras trabalhe sobre o texto normalizado.

```text
TXT / PDF / DOCX
        ↓
Extração de texto
        ↓
Normalização
        ↓
Motor de análise
        ↓
JSON
```

> PDFs digitalizados como imagem ainda exigiriam uma futura camada de OCR.


## IA assistida

A Fase 4 introduz uma camada de análise assistida desacoplada do motor principal.

```text
Documento
   ↓
Extração
   ↓
Regras determinísticas
   ↓
IA assistida opcional
   ↓
Resultado estruturado
   ↓
Revisão humana
```

O modo atual `local` funciona sem chave de API e demonstra a arquitetura de integração. Um endpoint externo pode ser conectado futuramente por meio de adaptadores, sem alterar o motor principal.

Endpoint:

- `POST /analyze/ai`

A IA do projeto é assistiva: resultados não substituem revisão técnica ou decisão humana.


## Interface Web

A aplicação agora possui uma interface web demonstrativa servida pelo próprio FastAPI.

Após iniciar:

```bash
uvicorn app.api:app --reload
```

Abra:

```text
http://127.0.0.1:8000/
```

A interface permite:

- upload de TXT, PDF ou DOCX;
- execução da análise;
- visualização de classificação;
- score de completude;
- requisitos;
- pendências;
- riscos;
- JSON completo.

## Fluxo completo

```text
USUÁRIO
  ↓
INTERFACE WEB
  ↓
FASTAPI
  ↓
EXTRAÇÃO DOCUMENTAL
  ↓
REGRAS
  ↓
IA ASSISTIDA
  ↓
RESULTADO
  ↓
REVISÃO HUMANA
```


## Deploy

O projeto está preparado para execução em container com Docker.

```bash
docker build -t document-intelligence-agent .
docker run -p 8000:8000 document-intelligence-agent
```

Também foi incluída uma configuração `render.yaml` para facilitar deploy demonstrativo em plataformas compatíveis.

Consulte [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

> **Importante:** uma versão pública do MVP deve utilizar apenas documentos fictícios ou não confidenciais até que sejam implementados controles adequados de segurança e retenção de dados.
