# Contrato do Módulo Lambda

## Objetivo

Provisionar uma função AWS Lambda com role de execução IAM fornecida pelo módulo IAM. Nesta fase inicial, o módulo não implementa lógica de negócio — apenas estrutura a função com um artefato de código placeholder que permita validação e plan sem erros.

## Inputs

| Nome | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `function_name` | `string` | sim | Nome da função Lambda. |
| `runtime` | `string` | sim | Runtime da função (ex: `python3.12`). |
| `handler` | `string` | sim | Handler de entrada da função (ex: `index.handler`). |
| `filename` | `string` | sim | Caminho local para o arquivo `.zip` com o código da função. |
| `iam_role_arn` | `string` | sim | ARN da role de execução. Deve ser obtido exclusivamente via output do módulo IAM (`module.iam.lambda_execution_role_arn`). ARNs hardcoded são proibidos. |
| `tags` | `map(string)` | sim | Tags obrigatórias da plataforma: `project`, `environment`, `owner`, `cost_center`, `managed_by`. |

## Outputs

| Nome | Tipo | Descrição |
|---|---|---|
| `function_arn` | `string` | ARN da função Lambda criada. |
| `function_name` | `string` | Nome da função Lambda criada. |
| `invoke_arn` | `string` | ARN de invocação da função (usado pelo API Gateway). |

## Dependências

- **Módulo IAM**: A role de execução Lambda (`lambda_execution_role_arn`) deve ser consumida via output do módulo IAM. Nenhum ARN pode ser hardcoded.
- **Provider AWS**: Declarado exclusivamente em `live/*/providers.tf`.

## Consumidores

- `live/dev/main.tf`
- `live/prod/main.tf` (futuro)
- Módulo API Gateway (futuro, via output `invoke_arn`)

## Recursos AWS

- `aws_lambda_function`: Função Lambda principal.

## Restrições

- Este módulo **não deve** declarar `provider`, `backend` ou `terraform.required_providers`.
- O ARN da role de execução deve ser recebido como variável — nunca hardcoded.
- Nesta fase, nenhuma lógica de negócio deve ser implementada. O artefato de código (`filename`) é um placeholder vazio.

## Critérios de Aceite

- `terraform validate` executa sem erros no diretório `live/dev/`.
- `terraform plan` executa sem erros no diretório `live/dev/`.
- O output `function_arn` está disponível após apply.
- Nenhum ARN está hardcoded no módulo ou no ambiente.
- As tags obrigatórias estão presentes em todos os recursos do módulo.
