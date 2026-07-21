# Contrato do Módulo API Gateway

## Objetivo

Provisionar um API Gateway HTTP API (v2) como proxy reverso de uma função AWS Lambda, expondo-a para a internet pública. O módulo cria também a `aws_lambda_permission` necessária para autorizar a invocação da Lambda pelo Gateway.

## Inputs

| Nome | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `name` | `string` | sim | Nome do API Gateway. |
| `lambda_invoke_arn` | `string` | sim | ARN de invocação da Lambda. Deve ser obtido exclusivamente via `module.lambda.invoke_arn`. ARNs hardcoded são proibidos. |
| `lambda_function_name` | `string` | sim | Nome da função Lambda. Deve ser obtido exclusivamente via `module.lambda.function_name`. |
| `tags` | `map(string)` | sim | Tags obrigatórias da plataforma: `project`, `environment`, `owner`, `cost_center`, `managed_by`. |

## Outputs

| Nome | Tipo | Descrição |
|---|---|---|
| `api_endpoint` | `string` | URL pública do API Gateway (endpoint de invocação). |
| `api_id` | `string` | ID do API Gateway criado. |

## Recursos AWS

| Recurso | Descrição |
|---|---|
| `aws_apigatewayv2_api` | HTTP API v2 (protocol_type = HTTP). |
| `aws_apigatewayv2_integration` | Integração do tipo `AWS_PROXY` com a Lambda. |
| `aws_apigatewayv2_route` | Rota `$default` apontando para a integração. |
| `aws_apigatewayv2_stage` | Stage `$default` com `auto_deploy = true`. |
| `aws_lambda_permission` | Permissão para o API Gateway invocar a Lambda, restrita ao ARN do próprio Gateway. |

## Dependências

- **Módulo Lambda**: `lambda_invoke_arn` e `lambda_function_name` devem vir exclusivamente dos outputs do módulo Lambda.
- **Provider AWS**: Declarado exclusivamente em `live/*/providers.tf`.
- Sem acesso a recursos externos via `data` sources.

## Consumidores

- `live/dev/main.tf`
- `live/prod/main.tf` (futuro)

## Restrições

- Este módulo **não deve** declarar `provider`, `backend` ou `terraform.required_providers`.
- Nenhum ARN, ID ou URL pode ser hardcoded.
- Fora de escopo: autenticação (JWT/Cognito), domínio customizado, CORS avançado, WAF, logs de acesso ou CloudWatch.
- A `aws_lambda_permission` deve ser restrita ao ARN do `aws_apigatewayv2_api` criado pelo próprio módulo — nunca um wildcard genérico.

## Critérios de Aceite

- `terraform validate` e `terraform plan` executam sem erros em `live/dev/`.
- O output `api_endpoint` está disponível após apply.
- Nenhum ARN, ID ou URL está hardcoded no módulo ou no ambiente.
- As tags obrigatórias estão presentes em todos os recursos que suportam tags.
- A `aws_lambda_permission` usa `source_arn` restrito ao ARN do Gateway criado.
