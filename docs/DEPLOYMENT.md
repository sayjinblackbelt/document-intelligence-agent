# Deploy

## Docker

Construção:

```bash
docker build -t document-intelligence-agent .
```

Execução:

```bash
docker run -p 8000:8000 document-intelligence-agent
```

Abra:

```text
http://localhost:8000
```

## Plataforma de hospedagem

O projeto inclui `render.yaml` como configuração demonstrativa para plataformas compatíveis com deploy baseado em repositório.

Antes de publicar, revise:

- limites do plano;
- variáveis de ambiente;
- política de privacidade;
- limites de upload;
- logs e observabilidade.

## Segurança

O MVP não deve receber documentos confidenciais em ambiente público sem controles adicionais de autenticação, armazenamento, retenção e proteção de dados.
