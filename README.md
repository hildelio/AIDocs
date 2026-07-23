# Startup XYZ Platform — MVP de Ingestão e OCR Serverless

[![Terraform](https://img.shields.io/badge/IaC-Terraform-7B42BC?logo=terraform)](live/dev)
[![Python](https://img.shields.io/badge/Runtime-Python%203.12-3776AB?logo=python)](application/src)
[![AWS](https://img.shields.io/badge/Cloud-AWS%20Serverless-FF9900?logo=amazonaws)](https://aws.amazon.com)
[![Arquitetura](https://img.shields.io/badge/Padrão-Event--Driven%20Serverless-232F3E)](docs/architecture)

---

## Visão Geral & Objetivos

Este repositório implementa o **MVP de uma plataforma de ingestão e extração de dados** construída como estudo de caso para defesa de TCC. O projeto demonstra a aplicação de princípios de **Platform Engineering, Site Reliability Engineering (SRE) e Cloud Architecture** para construir um pipeline serverless de ponta a ponta.

**O problema resolvido:** Um cliente precisa enviar documentos (faturas, recibos) e ter o texto extraído automaticamente por IA, de forma assíncrona, auditável e resiliente — sem que a API sincrona sofra timeout durante o processamento pesado.

**Objetivos técnicos demonstrados:**
- Arquitetura orientada a eventos (*event-driven*) com baixo acoplamento
- Separação de responsabilidades em camadas (Handler → Service → Repository)
- Infraestrutura como Código (IaC) com Terraform modular e reutilizável
- Máquina de estados determinística e auditável no DynamoDB
- Tratamento de falhas resiliente com estados explícitos de erro

---

## Arquitetura Física

![Arquitetura Serverless Final — Startup XYZ](arquitetura/arquitetura_serverless_startup_xyz_final.png)

### Fluxo de Dados (Passo a Passo)

| # | Etapa | Descrição |
|---|-------|-----------|
| 1 | **Requisição Síncrona** | O cliente faz `POST /upload` para o API Gateway com `user_id` e `filename` |
| 2 | **Lambda Ingestão** | Gera um `document_id` (UUID), salva metadados no DynamoDB (status `PENDING_UPLOAD`) e retorna uma Pre-signed URL do S3 |
| 3 | **Upload Direto** | O cliente faz `PUT` direto para o S3 usando a URL assinada (**bypass total do Lambda**) |
| 4 | **Trigger Assíncrono** | O S3 emite um evento `s3:ObjectCreated` que aciona a Lambda OCR automaticamente |
| 5 | **Pipeline OCR** | A Lambda OCR atualiza o status para `PROCESSING`, chama o Amazon Textract e salva o texto extraído no DynamoDB com status `PROCESSED` |
| 6 | **Observabilidade** | Ambas as Lambdas emitem logs estruturados para o CloudWatch. Erros externos são capturados e persistidos com status `FAILED_EXTERNAL_DEPENDENCY` |

---

## Decisões Arquiteturais (ADRs)

As decisões de design estão documentadas em [`docs/adr/`](docs/adr/).

| ADR | Decisão | Motivação |
|-----|---------|-----------|
| [ADR-001](docs/adr/ADR-001-live-directory.md) | Separação de ambientes em `live/dev` e `live/prod` | Isolamento operacional e estado independente por ambiente |
| [ADR-002](docs/adr/ADR-002-module-contracts.md) | Contratos de módulo explícitos | Evitar acoplamento implícito e facilitar reutilização |
| [ADR-003](docs/adr/ADR-003-module-dependency-graph.md) | Grafo de dependências de módulos | Tornar explícitas as dependências entre módulos Terraform |
| [ADR-004](docs/adr/ADR-004-pre-signed-url.md) | Acesso ao S3 via Pre-signed URLs | Segurança sem exposição pública; evita timeout e custos de API Gateway com payloads pesados |
| [ADR-005](docs/adr/ADR-005-estrategia-evolucao-plataforma-ia.md) | Roadmap de evolução da plataforma de IA em 4 fases | Desacoplamento para que equipes de Infra, Engenharia e Data Science evoluam independentemente |

### Por que duas Lambdas?

A separação em **Lambda Ingestão** e **Lambda OCR** é uma decisão deliberada de desacoplamento:

- **Lambda Ingestão** é síncrona e deve responder em milissegundos (gera URL, escreve metadados). Configurada com timeout padrão de 3s.
- **Lambda OCR** é assíncrona e pode demorar até 30s (Textract é um serviço de IA externo). Configurada com `timeout = 30` e `memory_size = 256MB`.
- O isolamento garante que uma falha no pipeline OCR **jamais afeta** a disponibilidade da API de ingestão.

---

## Máquina de Estados (O Diferencial)

O documento no DynamoDB funciona como a **fonte de verdade** do processamento assíncrono. A máquina de estados garante observabilidade total em qualquer momento:

```
                        ┌──────────────────────────┐
                        │         REQUESTED         │  ← Lambda Ingestão: UUID gerado
                        └─────────────┬────────────┘
                                      │
                        ┌─────────────▼────────────┐
                        │      PENDING_UPLOAD        │  ← Metadados salvos no DynamoDB
                        └─────────────┬────────────┘
                                      │  S3 Event Notification
                        ┌─────────────▼────────────┐
                        │         PROCESSING         │  ← Lambda OCR acordada
                        └─────────────┬────────────┘
                                      │
               ┌──────────────────────┴────────────────────┐
               │                                           │
  ┌────────────▼────────────┐             ┌────────────────▼──────────────┐
  │         PROCESSED        │             │    FAILED_EXTERNAL_DEPENDENCY  │
  │  extracted_text salvo   │             │   (ex: SubscriptionRequired)   │
  └─────────────────────────┘             └────────────────────────────────┘
```

O estado `FAILED_EXTERNAL_DEPENDENCY` é capturado via `ClientError` do Boto3 e gravado no DynamoDB antes de encerrar a execução — **garantindo que o pipeline nunca fique em estado indefinido** e o **Poison Pill** (S3 retry infinito) não ocorra.

---

## Engenharia de Plataforma (IaC Modular)

```
edn/
├── bootstrap/          # Bootstrap isolado: S3 + DynamoDB para Terraform State
├── live/
│   └── dev/            # Entrypoint do ambiente dev (orquestra módulos)
│       ├── main.tf     # Composição: lambda, s3, dynamodb, api_gateway, iam, ocr_pipeline
│       ├── backend.tf  # State remoto (S3 + DynamoDB locking)
│       └── versions.tf # Versões travadas do provider AWS
└── modules/
    ├── lambda/          # Módulo genérico de Lambda (timeout, memory_size, env vars)
    ├── s3/              # Bucket privado: versioning, SSE-S3, lifecycle, bloqueio público
    ├── dynamodb/        # Tabela PAY_PER_REQUEST com billing e tags obrigatórias
    ├── iam/             # Role de execução Lambda com AWSLambdaBasicExecutionRole
    ├── iam_policy_dynamodb/  # Política CRUD mínima no DynamoDB (menor privilégio)
    ├── iam_policy_s3/        # Política PutObject no S3 (menor privilégio)
    ├── api_gateway/     # HTTP API Gateway com integração Lambda proxy
    └── ocr_pipeline/    # Módulo composto: Lambda OCR + IAM + S3 Trigger
```

**Princípios aplicados:**
- **Menor Privilégio (IAM):** Cada Lambda tem apenas as permissões mínimas necessárias
- **Zero Hardcoding:** Todos os valores são injetados via `variables.tf`. ARNs e nomes são resolvidos via `outputs.tf`
- **Módulos sem Provider:** Providers são declarados apenas nos pontos de entrada (`live/`, `bootstrap/`)
- **Tags Obrigatórias:** `project`, `environment`, `owner`, `cost_center`, `managed_by` propagadas para todos os recursos
- **source_code_hash:** O Terraform detecta automaticamente mudanças no `artifact.zip` via hash SHA256

---

## Observabilidade & Troubleshooting

### CloudWatch Logs

Ambas as Lambdas emitem logs para grupos dedicados:
- `/aws/lambda/startup-xyz-dev-ingestion` — Logs da ingestão
- `/aws/lambda/startup-xyz-dev-ocr` — Logs do pipeline OCR (incluindo latência do Textract)

**Comando de diagnóstico:**
```bash
aws logs tail /aws/lambda/startup-xyz-dev-ocr --region sa-east-1 --since 30m
```

### Tratamento do `SubscriptionRequiredException`

Durante o desenvolvimento foi identificado que o Amazon Textract requer ativação explícita na conta AWS em algumas regiões (`sa-east-1` não suporta o endpoint padrão do Textract). O pipeline trata este cenário especificamente:

```python
except ClientError as e:
    logger.exception(f"AWS ClientError: {e}")
    status_to_save = "FAILED"
    if "SubscriptionRequiredException" in str(e):
        status_to_save = "FAILED_EXTERNAL_DEPENDENCY"
    self.dynamodb_repository.update_document(document_id, {"status": status_to_save})
```

Esta abordagem garante que o pipeline é **idempotente e auditável** mesmo em cenários de falha de infraestrutura externa.

---

## Camada de Aplicação (Python 3.12)

```
application/
├── src/
│   ├── handlers/
│   │   ├── upload_handler.py   # Handler HTTP: recebe evento API Gateway, retorna URL
│   │   └── ocr_handler.py      # Handler S3: recebe evento ObjectCreated, aciona OCR
│   ├── services/
│   │   ├── ingestion_service.py # Orquestra geração de UUID, URL e persistência
│   │   └── ocr_service.py       # Orquestra Textract + máquina de estados
│   ├── repositories/
│   │   ├── s3_repository.py         # PutObject + generate_presigned_url
│   │   ├── dynamodb_repository.py   # PutItem + UpdateItem + GetItem por s3_key
│   │   └── textract_repository.py   # detect_document_text com log de latência
│   └── config.py                # Fail-fast: variáveis de ambiente obrigatórias
├── scripts/
│   └── simulate_client_e2e.py  # Script de validação E2E completo
└── requirements.txt
```

**Padrões de qualidade implementados:**
- **Fail-Fast:** `config.py` levanta `RuntimeError` imediatamente se variáveis de ambiente estiverem ausentes
- **Preservação de Traceback:** Todos os blocos `except` usam `logger.exception()` e `raise` puro
- **Cold Start Optimization:** Repositórios e Services inicializados no escopo global do Handler
- **Type Hints:** Todos os métodos anotados com `dict[str, Any]`, `str`, etc.

---

## Instruções de Execução

### Pré-requisitos
- AWS CLI configurado com credenciais válidas
- Terraform >= 1.0
- Python 3.12+
- Graphviz (para gerar diagramas)

### Deploy

```bash
# 1. Build do artifact
make build-app

# 2. Deploy da infraestrutura
make plan    # Verifica mudanças
make apply   # Aplica o plano

# 3. Validação E2E
python application/scripts/simulate_client_e2e.py https://<api-id>.execute-api.sa-east-1.amazonaws.com/
```

### Verificação de Qualidade

```bash
make fmt              # Formata HCL
make validate         # Valida Terraform
make architecture-check  # Valida estrutura de diretórios
```

### Geração do Diagrama de Arquitetura

```bash
cd arquitetura
python arquitetura_serverless_startup_xyz_final.py
```

### Destruição do Ambiente

```bash
make destroy
```

> **Nota:** O bucket S3 deve ser esvaziado antes de `terraform destroy`. Em caso de falha, use o script AWS CLI de purgação de versões.

---

## Estrutura de Commits

O projeto segue [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — Nova funcionalidade
- `chore:` — Manutenção de infraestrutura e tooling
- `fix:` — Correção de bug
- `docs:` — Documentação

---

## Roadmap e Trabalhos Futuros

- **v0.1.0** ✅ — Bootstrap, IAM, CI/CD scaffolding
- **v0.2.0** ✅ — Lambda Ingestão, S3, DynamoDB, API Gateway
- **v0.3.0** ✅ — Pipeline OCR assíncrono (Lambda OCR + Textract + S3 Event)
- **v0.4.0** ✅ — Máquina de estados determinística e tratamento de erros externos
- **v0.5.0** 🔮 — Dead Letter Queue (SQS DLQ) para retry automático de falhas
- **v0.6.0** 🔮 — Ambiente `prod` com separação completa de state e roles
- **v0.7.0** 🔮 — Integração com Amazon Bedrock para sumarização de documentos extraídos
