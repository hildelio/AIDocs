# ADR-003: Grafo de dependência dos módulos iniciais

- Status: Aceito
- Data: 2026-07-16

## Contexto

A plataforma precisa de uma ordem de composição clara para reduzir acoplamento e facilitar a validação incremental. Um fluxo bem definido ajuda a evitar decisões de permissão prematuras e garante que cada camada seja provisionada de forma previsível.

## Decisão

Definir o fluxo de dependência inicial como: IAM -> S3 -> Lambda -> API Gateway.

## Consequências

- O módulo IAM é a base para identidade e trust relationships.
- O módulo S3 depende da identidade definida pelo IAM para políticas mínimas.
- O módulo Lambda depende de IAM e S3 para execução e armazenamento.
- O módulo API Gateway depende de Lambda para orquestração de entrada e saída.
