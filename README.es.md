# Agente de Inteligencia Documental

[🇧🇷 Português](README.md) | [🇺🇸 English](README.en.md) | 🇪🇸 Español

> MVP demostrativo para análisis estructurado de documentos mediante Python, reglas determinísticas, IA asistida y salida en JSON.

## 🎯 Objetivo

Demostrar cómo los procesos de análisis documental pueden automatizarse parcialmente, reduciendo tareas repetitivas y generando información estructurada para apoyar la toma de decisiones humanas.

## ✅ Capacidades actuales

El agente puede:

- leer documentos de texto;
- extraer metadatos básicos;
- admitir **TXT, PDF con texto extraíble y DOCX**;
- identificar requisitos, pendientes y riesgos mediante reglas configurables;
- clasificar tipos de documentos;
- calcular un índice de completitud;
- generar informes estructurados en JSON;
- exponer el análisis mediante una API REST con FastAPI;
- ofrecer una interfaz web demostrativa;
- utilizar una capa opcional de IA asistida sin sustituir la validación determinística.

## 🏗️ Arquitectura

```text
TXT / PDF / DOCX
        ↓
Extracción de texto
        ↓
Normalización
        ↓
Reglas determinísticas
        ↓
IA asistida opcional
        ↓
Resultado estructurado
        ↓
Revisión humana
```

## 🚀 Ejecución local

```bash
python main.py
```

## 🌐 API REST

```bash
pip install -r requirements.txt
uvicorn app.api:app --reload
```

Endpoints iniciales:

- `GET /health`
- `POST /analyze/text`
- `POST /analyze/file`
- `POST /analyze/ai`

La documentación interactiva está disponible en `/docs`.

## 🧠 Principio de diseño

La primera capa de análisis es determinística, proporcionando reproducibilidad, pruebas objetivas y trazabilidad.

La IA es una capa asistiva y no sustituye la validación ni la revisión humana.

## 🖥️ Interfaz web

La aplicación incluye una interfaz web demostrativa que permite:

- cargar TXT, PDF y DOCX;
- ejecutar análisis;
- visualizar clasificación;
- consultar el índice de completitud;
- revisar requisitos, pendientes y riesgos;
- visualizar el JSON completo.

## 📈 Evolución

```text
MVP Python ✓
      ↓
API REST ✓
      ↓
TXT / PDF / DOCX ✓
      ↓
IA asistida ✓
      ↓
Interfaz Web ✓
      ↓
OCR para PDF escaneado
      ↓
Comparación entre versiones
      ↓
Persistencia y seguridad avanzada
```

## 🐳 Despliegue

El proyecto está preparado para ejecutarse en contenedores con Docker.

También incluye una configuración `render.yaml` para despliegues demostrativos en plataformas compatibles.

## 🔒 Confidencialidad

Todos los documentos de demostración son ficticios.

Una versión pública del MVP debe utilizar únicamente documentos ficticios o no confidenciales hasta implementar controles adecuados de seguridad, privacidad y retención de datos.

## 🛠️ Tecnologías

**Python · FastAPI · JSON · pytest · Docker · HTML/CSS/JavaScript**

## 👨‍💻 Autor

**Filipe Gimenes de Morais**
