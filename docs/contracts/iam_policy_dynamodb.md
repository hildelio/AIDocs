# Contrato do Módulo iam_policy_dynamodb

## Objetivo

Encapsular a concessão de acesso CRUD (GetItem, PutItem, UpdateItem, DeleteItem, Query, Scan) a uma tabela DynamoDB para uma role IAM existente, sem alterar os módulos `iam` ou `dynamodb` originais. Implementa o padrão de Integração Desacoplada.

## Inputs

| Nome | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `role_name` | `string` | sim | Nome da role IAM que receberá a policy. Deve vir de `module.iam.lambda_execution_role_name`. |
| `table_arn` | `string` | sim | ARN da tabela DynamoDB alvo. Deve vir de `module.dynamodb.table_arn`. |
| `tags` | `map(string)` | sim | Tags obrigatórias da plataforma: `project`, `environment`, `owner`, `cost_center`, `managed_by`. |

## Outputs

| Nome | Tipo | Descrição |
|---|---|---|
| `policy_arn` | `string` | ARN da policy IAM criada. |

## Recursos AWS

| Recurso | Descrição |
|---|---|
| `aws_iam_policy` | Policy com permissões CRUD restritas ao ARN da tabela DynamoDB. |
| `aws_iam_role_policy_attachment` | Vincula a policy à role informada. |

## Dependências

- **Módulo IAM**: `role_name` via `module.iam.lambda_execution_role_name`.
- **Módulo DynamoDB**: `table_arn` via `module.dynamodb.table_arn`.
- **Provider AWS**: Declarado exclusivamente em `live/*/providers.tf`.

## Consumidores

- `live/dev/main.tf`
- `live/prod/main.tf` (futuro)

## Restrições

- Este módulo **não deve** declarar `provider`, `backend` ou `terraform.required_providers`.
- Nenhum ARN ou nome de recurso pode ser hardcoded.
- O `Resource` da policy deve ser restrito ao ARN exato da tabela — sem wildcards.
- Fora de escopo: permissões de stream, DAX, backup ou acesso cross-account.

## Critérios de Aceite

- `terraform validate` e `terraform plan` executam sem erros em `live/dev/`.
- A policy usa `Resource = [var.table_arn]` — sem wildcards.
- O módulo `iam` permanece inalterado.
- O módulo `dynamodb` permanece inalterado.
