# Arquitetura de IA Assistida

## Objetivo

Adicionar capacidades de IA sem tornar o projeto dependente de um provedor externo.

## Arquitetura

```text
Documento
   ↓
Extração
   ↓
Regras determinísticas
   ↓
Camada de IA
   ├── Local demonstrativa
   └── Adaptador externo futuro
   ↓
Resultado estruturado
   ↓
Revisão humana
```

## Implementação atual

O modo `local` é determinístico e utiliza sinais identificados pelas regras para gerar:

- resumo executivo demonstrativo;
- requisitos contextuais;
- pendências contextuais;
- riscos contextuais;
- prioridade sugerida.

## Evolução futura

A camada pode receber adaptadores para diferentes provedores de LLM. Credenciais não devem ser incluídas no código ou versionadas.

## Princípio

IA assistida não substitui validação técnica ou revisão humana.
