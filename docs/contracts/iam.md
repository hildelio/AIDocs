# Contrato do Módulo IAM

## Objetivo

Fornecer um módulo reutilizável para criar roles e policies com princípio de menor privilégio para integrações da plataforma, especialmente Lambda e API Gateway.

## Inputs

- `project` (string): identificador do projeto.
- `environment` (string): ambiente de implantação (`dev`, `prod`, etc.).
- `owner` (string): equipe responsável.
- `cost_center` (string): centro de custo.
- `lambda_execution_role_name` (string, opcional): nome da role para execução da Lambda.
- `apigateway_execution_role_name` (string, opcional): nome da role para integração do API Gateway.
- `tags` (map(string)): tags obrigatórias da plataforma.

## Outputs

- `lambda_execution_role_arn` (string): ARN da role de execução da Lambda.
- `lambda_execution_role_name` (string): nome da role de execução da Lambda.
- `apigateway_execution_role_arn` (string): ARN da role de execução do API Gateway.
- `apigateway_execution_role_name` (string): nome da role de execução do API Gateway.

## Resources

- Por enquanto, este módulo deve criar apenas `aws_iam_role` e `aws_iam_role_policy_attachment`.
- Trust Policies devem ser definidas junto às roles para permitir a integração com Lambda e API Gateway.

## Dependencies

- Provider AWS.
- Tags padronizadas do projeto.
- Recursos alvo ainda não criados, como S3 e Lambda, devem ser referenciados apenas quando já existirem.

## Consumers

- Módulo Lambda.
- Módulo API Gateway.
- Futuras integrações com serviços AWS que exijam IAM role.

## Security

- As policies devem seguir o princípio de menor privilégio.
- Nenhuma policy de resource deve ser criada sem o recurso alvo já existir ou sem contexto explícito.
- Roles devem receber apenas os trust relationships necessários.

## Constraints

- Este módulo não deve criar policies de recursos para S3, Lambda ou outros serviços nesta fase inicial.
- O módulo deve ser limitado à identidade e trust relationships mínimas necessárias.
- Os outputs devem retornar ARNs e nomes reais após o apply.

## Critérios de Aceite

- As roles devem ser nomeadas com base no ambiente e no projeto.
- Os outputs devem retornar ARNs e nomes reais após o apply.
- Nenhuma política deve ser criada com permissões amplas sem justificativa explícita.
