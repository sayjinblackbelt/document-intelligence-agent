# Document Intelligence Agent

[🇧🇷 Português](README.md) | 🇺🇸 English | [🇪🇸 Español](README.es.md)

> Demonstration MVP for structured document analysis using Python, deterministic rules, assisted AI, and JSON output.

## 🎯 Objective

Demonstrate how document-analysis processes can be partially automated, reducing repetitive work and producing structured information to support human decision-making.

## ✅ Current capabilities

The agent can:

- read text documents;
- extract basic metadata;
- support **TXT, text-extractable PDF, and DOCX**;
- identify requirements, pending items, and risks through configurable rules;
- classify document types;
- calculate a completeness score;
- generate structured JSON reports;
- expose analysis through a FastAPI REST API;
- provide a demonstration web interface;
- use an optional assisted-AI layer without replacing deterministic validation.

## 🏗️ Architecture

```text
TXT / PDF / DOCX
        ↓
Text extraction
        ↓
Normalization
        ↓
Deterministic rules
        ↓
Optional assisted AI
        ↓
Structured result
        ↓
Human review
```

## 📂 Structure

```text
document-intelligence-agent/
├── app/
│   ├── analyzer.py
│   ├── rules.py
│   └── report.py
├── sample_data/
├── output/
├── tests/
├── docs/
├── main.py
├── requirements.txt
└── README.md
```

## 🚀 Running locally

```bash
python main.py
```

The report is saved to:

```text
output/analysis_report.json
```

## 🌐 REST API

Install dependencies and start the application:

```bash
pip install -r requirements.txt
uvicorn app.api:app --reload
```

Initial endpoints:

- `GET /health`
- `POST /analyze/text`
- `POST /analyze/file`
- `POST /analyze/ai`

FastAPI provides interactive documentation at:

```text
/docs
```

See also:

- [API documentation](docs/API.md)
- [Roadmap](docs/ROADMAP.md)

## 🧠 Design principle

The first analysis layer is deterministic. This provides reproducibility, objective testing, and traceability.

AI is an optional assistive layer and does not replace validation or human review.

> **Automation supports analysis; human responsibility remains essential for technical validation and decisions.**

## 🖥️ Web interface

The application includes a demonstration web interface served by FastAPI.

After starting the application:

```bash
uvicorn app.api:app --reload
```

Open:

```text
http://127.0.0.1:8000/
```

The interface supports:

- TXT, PDF, and DOCX upload;
- analysis execution;
- document classification;
- completeness score;
- requirements;
- pending items;
- risks;
- full JSON visualization.

## 📈 Evolution

```text
Python MVP ✓
      ↓
REST API ✓
      ↓
TXT / PDF / DOCX ✓
      ↓
Assisted AI ✓
      ↓
Web Interface ✓
      ↓
OCR for scanned PDFs
      ↓
Version comparison
      ↓
Advanced persistence and security
```

## 🐳 Deployment

The project is prepared for container execution with Docker:

```bash
docker build -t document-intelligence-agent .
docker run -p 8000:8000 document-intelligence-agent
```

A `render.yaml` configuration is also included for demonstration deployments on compatible platforms.

See [Deployment documentation](docs/DEPLOYMENT.md).

## 🔒 Confidentiality

All demonstration documents are fictional.

A public MVP should use only fictional or non-confidential documents until appropriate controls for security, privacy, and data retention are implemented.

## 🛠️ Technologies

**Python · FastAPI · JSON · pytest · Docker · HTML/CSS/JavaScript**

## 👨‍💻 Author

**Filipe Gimenes de Morais**
