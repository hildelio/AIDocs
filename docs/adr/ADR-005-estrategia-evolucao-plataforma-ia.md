# ADR-005: Estratégia de Evolução da Plataforma de IA

## Status
Aceito

## Contexto
O projeto baseia-se em uma arquitetura serverless orientada a eventos. Com o objetivo de agregar inteligência e processamento avançado de dados sem comprometer a estabilidade e a performance do sistema principal (API síncrona), é necessário formalizar a jornada de evolução da plataforma de IA.

## Decisão
A evolução arquitetural para integração de Inteligência Artificial seguirá um roadmap de 4 fases claras, garantindo o desacoplamento entre a ingestão de dados, o processamento pesado e o consumo por modelos de ML.

### Estratégia em 4 Fases

#### Fase 1: Ingestão (Atual)
- **Componentes:** API Gateway -> Lambda -> S3.
- **Funcionamento:** O cliente utiliza rotas de API para obter Pre-signed URLs e faz o upload direto de binários para o S3.
- **FinOps:** O S3 possui uma `lifecycle_rule` configurada para transferir dados inativos para a classe GLACIER após 365 dias, reduzindo custos de armazenamento a longo prazo.

#### Fase 2: Processamento Assíncrono (Event-driven)
- **Componentes:** S3 Event Notifications -> Lambda -> Amazon Textract.
- **Funcionamento:** Assim que um arquivo (ex: PDF ou imagem) chega no S3, um evento `s3:ObjectCreated:*` aciona automaticamente uma Lambda especializada. A Lambda envia o documento para o Amazon Textract para extração de texto (OCR) ou estruturação de dados.
- **Vantagem:** O fluxo assíncrono impede que o cliente sofra timeout (API Gateway limite de 30s) enquanto o processamento pesado ocorre em background.

#### Fase 3: Indexação e Metadados
- **Componentes:** Saída do Textract -> DynamoDB.
- **Funcionamento:** O resultado extraído pela inteligência de documentos (Fase 2) é processado, enriquecido e salvo em uma tabela DynamoDB configurada como `PAY_PER_REQUEST`.
- **Vantagem:** Permite buscas eficientes, indexação rápida e consultas transacionais por parte da aplicação, mantendo um repositório centralizado dos metadados extraídos.

#### Fase 4: Consumo e Treinamento (Integração IA)
- **Componentes:** DynamoDB/S3 -> Modelos de ML (Amazon Bedrock, SageMaker, etc.).
- **Funcionamento:** A camada de dados consolidados (S3 para binários brutos, DynamoDB para metadados/texto extraído) torna-se a fonte da verdade para o consumo por serviços avançados de IA. Exemplos de evolução incluem aplicações RAG com Amazon Bedrock ou treinamento supervisionado utilizando SageMaker, ou outras plataformas de ML conforme evolução do produto.
- **Vantagem:** A fundação de dados estará preparada, limpa e estruturada, permitindo plugar serviços de IA sob demanda conforme a evolução do produto sem necessidade de refatorar a infraestrutura de ingestão.

## Consequências
- A plataforma assegura escalabilidade e resiliência desde o dia 1.
- O desacoplamento evita gargalos e permite que equipes de Infraestrutura, Engenharia de Software e Data Science trabalhem de forma independente em diferentes partes do pipeline.
