# ADR-001: Estrutura de diretórios live/dev e live/prod

- Status: Aceito
- Data: 2026-07-16

## Contexto

A plataforma precisa de uma estrutura de consumo de módulos que seja previsível, reutilizável e alinhada ao modelo de ambientes de execução. A abordagem anterior baseada em `environments/` torna a composição mais rígida e dificulta a evolução incremental de cada ambiente.

## Decisão

Usar a estrutura `live/dev` e `live/prod` como pontos de entrada para composição e consumo dos módulos, em vez de `environments/`.

## Consequências

- A organização de ambientes passa a ser mais explícita e alinhada com o padrão de deployment.
- Os módulos ficam isolados e reutilizáveis, com composição feita nos diretórios `live/`.
- A governança fica mais clara, pois cada ambiente possui um ponto de entrada bem definido.
