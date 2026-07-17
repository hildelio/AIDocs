# ADR-002: Contratos de interface para módulos

- Status: Aceito
- Data: 2026-07-16

## Contexto

Implementar módulos de infraestrutura sem um contrato formal entre entradas e saídas aumenta o risco de acoplamento, reuso inadequado e inconsistência operacional. O código pode funcionar localmente, mas se tornar difícil de evoluir e auditar.

## Decisão

Todo módulo deve ser precedido por um documento de contrato em `docs/contracts/` que defina objetivo, inputs, outputs, dependências, consumidores, recursos AWS e critérios de aceite.

## Consequências

- A implementação dos módulos passa a ser guiada por interfaces claras.
- Reuso e manutenção ficam mais seguros.
- A arquitetura se torna auditar e governável desde a fase de design.
