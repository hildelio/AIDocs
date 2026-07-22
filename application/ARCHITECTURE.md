# Application Architecture

## Visão Geral
A camada de aplicação (funções AWS Lambda) deste projeto segue um padrão arquitetural em **3 Camadas (3-Tier Architecture)** para garantir a separação de responsabilidades, testabilidade e manutenibilidade do código.

## Estrutura de Camadas

A arquitetura está dividida nas seguintes responsabilidades estritas:

### 1. Handler (Entrypoint)
- **Localização:** `src/handlers/`
- **Responsabilidade:** Atuar exclusivamente como a porta de entrada para eventos da AWS (ex: requisições do API Gateway, eventos do S3, SQS).
- **Regras:**
  - Deve receber o `event` e `context`.
  - Extrair e desserializar os parâmetros necessários (body, path parameters, headers).
  - Invocar a camada de **Service**.
  - Formatar a resposta HTTP (status code, JSON body) caso a origem exija (ex: API Gateway).
  - **Proibido:** Conter regras de negócio, queries a banco de dados ou chamadas diretas a APIs externas.

### 2. Service (Regra de Negócio)
- **Localização:** `src/services/`
- **Responsabilidade:** Orquestrar o fluxo principal da aplicação e executar as regras de negócio.
- **Regras:**
  - Concentrar a lógica "core" da aplicação (ex: validação de dados complexa, decisão de fluxos, cálculos).
  - Chamar os módulos da camada de **Repository/Infrastructure** quando precisar ler ou gravar dados, ou interagir com outros serviços.
  - O Service não deve saber detalhes técnicos de *como* o dado é gravado (SQL, NoSQL, APIs).
  - Altamente testável via testes unitários isolados (mocking da camada inferior).

### 3. Infrastructure / Repository
- **Localização:** `src/repositories/`
- **Responsabilidade:** Isolar a comunicação com serviços externos, APIs de terceiros e persistência de dados.
- **Regras:**
  - Encapusular o uso da biblioteca `boto3`.
  - Implementar o acesso ao DynamoDB (queries, puts, scans).
  - Implementar interações com o S3 (geração de Pre-signed URLs, uploads/downloads locais).
  - Lidar com exceções específicas de infraestrutura (ex: `ClientError` do boto3) e expor erros padronizados para a camada de Service.

## Fluxo de Dados

`[Event Source (ex: API Gateway)] --> Handler --> Service --> Repository --> [AWS Services (S3/DynamoDB)]`
