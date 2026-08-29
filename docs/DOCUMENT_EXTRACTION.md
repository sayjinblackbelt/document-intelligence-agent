# Extração de Documentos

## Formatos suportados

| Formato | Biblioteca |
|---|---|
| TXT | Biblioteca padrão |
| PDF | pypdf |
| DOCX | python-docx |

## Fluxo

```text
Arquivo
  ↓
Identificação da extensão
  ↓
Extrator específico
  ↓
Texto normalizado
  ↓
Motor de análise
```

## Limitações

PDFs digitalizados como imagem podem não possuir texto extraível. OCR não faz parte deste MVP.

A extração é apenas uma etapa técnica; resultados analíticos continuam sujeitos à revisão humana.
