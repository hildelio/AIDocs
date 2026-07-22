# Contrato do Módulo DynamoDB

## Objetivo

Provisionar uma tabela AWS DynamoDB para persistência de dados da plataforma, com billing mode PAY_PER_REQUEST (on-demand) e proteção contra deleção acidental.

## Inputs

| Nome | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `table_name` | `string` | sim | Nome da tabela DynamoDB. |
| `hash_key` | `string` | sim | Nome do atributo usado como partition key (hash key). |
| `hash_key_type` | `string` | não | Tipo do hash key: `S` (String), `N` (Number) ou `B` (Binary). Default: `S`. |
| `tags` | `map(string)` | sim | Tags obrigatórias da plataforma: `project`, `environment`, `owner`, `cost_center`, `managed_by`. |

## Outputs

| Nome | Tipo | Descrição |
|---|---|---|
| `table_name` | `string` | Nome da tabela DynamoDB criada. |
| `table_arn` | `string` | ARN da tabela DynamoDB criada. |

## Recursos AWS

| Recurso | Descrição |
|---|---|
| `aws_dynamodb_table` | Tabela DynamoDB com billing PAY_PER_REQUEST. |

## Dependências

- **Provider AWS**: Declarado exclusivamente em `live/*/providers.tf`.
- Sem dependência de outros módulos da plataforma nesta fase.

## Consumidores

- `live/dev/main.tf`
- `live/prod/main.tf` (futuro)
- Módulo Lambda (futuro — para acesso via policy IAM com ARN via output `table_arn`)

## Restrições

- Este módulo **não deve** declarar `provider`, `backend` ou `terraform.required_providers`.
- Nenhum ARN ou nome de tabela pode ser hardcoded nos consumidores; usar os outputs deste módulo.
- Fora de escopo nesta fase: índices secundários (GSI/LSI), streams, TTL, réplicas globais, criptografia KMS customizada.

## Critérios de Aceite

- `terraform validate` e `terraform plan` executam sem erros em `live/dev/`.
- Os outputs `table_name` e `table_arn` estão disponíveis após apply.
- Billing mode é `PAY_PER_REQUEST`.
- Tags obrigatórias presentes no recurso.
