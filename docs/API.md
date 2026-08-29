# API — Document Intelligence Agent

## Executar

```bash
pip install -r requirements.txt
uvicorn app.api:app --reload
```

A documentação interativa estará disponível em:

- `/docs`
- `/redoc`

## Endpoints

### GET /health

Verifica o funcionamento do serviço.

### POST /analyze/text

Analisa conteúdo enviado como JSON.

Exemplo:

```json
{
  "filename": "documento.txt",
  "content": "O requisito deverá ser validado. Existe uma pendência."
}
```

### POST /analyze/file

Recebe um arquivo `.txt` UTF-8.

## Limites atuais

Esta versão é um MVP demonstrativo:

- aceita texto e arquivos TXT;
- utiliza regras determinísticas;
- não substitui revisão humana;
- PDF, DOCX e IA serão adicionados em fases futuras.
