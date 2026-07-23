# Startup XYZ Platform — MVP de Ingestão e OCR Serverless

[![Terraform](https://img.shields.io/badge/IaC-Terraform-7B42BC?logo=terraform)](live/dev)
[![Python](https://img.shields.io/badge/Runtime-Python%203.12-3776AB?logo=python)](application/src)
[![AWS](https://img.shields.io/badge/Cloud-AWS%20Serverless-FF9900?logo=amazonaws)](https://aws.amazon.com)

---

## Visão Geral

Este repositório implementa o **MVP de uma plataforma de ingestão e extração de dados** como estudo de caso de TCC. O projeto demonstra a aplicação prática de **Platform Engineering, SRE e Cloud Architecture** para construir um pipeline serverless auditável de ponta a ponta.

**O problema resolvido:** Um cliente envia documentos (faturas, recibos) e o texto é extraído automaticamente por IA — de forma assíncrona e resiliente — sem que a API síncrona sofra timeout durante o processamento pesado.

---

## Arquitetura

![Arquitetura Serverless Final — Startup XYZ](arquitetura/arquitetura_serverless_startup_xyz_final.png)

O diagrama mostra três camadas lógicas:
- **① Entrada:** API Gateway → Lambda Ingestão (síncrona, resposta em ms)
- **② Processamento:** S3 Event → Lambda OCR → Amazon Textract (assíncrono, até 30s)
- **③ Estado/Observabilidade:** DynamoDB (máquina de estados) + CloudWatch Logs

---

## Decisões Arquiteturais (ADRs)

| ADR | Decisão | Por quê |
|-----|---------|---------|
| [ADR-001](docs/adr/ADR-001-live-directory.md) | `live/dev` e `live/prod` como entrypoints | Isolamento operacional com state independente por ambiente |
| [ADR-002](docs/adr/ADR-002-module-contracts.md) | Contratos de interface para módulos | Evitar acoplamento implícito; forçar interfaces explícitas antes da implementação |
| [ADR-003](docs/adr/ADR-003-module-dependency-graph.md) | Grafo de dependência: IAM → S3 → Lambda → API GW | Ordem de provisionamento previsível; evita permissões especulativas |
| [ADR-004](docs/adr/ADR-004-pre-signed-url.md) | Acesso ao S3 via Pre-signed URLs | Bucket privado sem exposição pública; evita timeout e custo de payload no API Gateway |
| [ADR-005](docs/adr/ADR-005-estrategia-evolucao-plataforma-ia.md) | Roadmap de IA em 4 fases | Desacoplamento para que Infra, Engenharia e Data Science evoluam independentemente |

### Por que duas Lambdas separadas?

| | Lambda Ingestão | Lambda OCR |
|---|---|---|
| **Natureza** | Síncrona | Assíncrona (event-driven) |
| **Timeout** | 3s | 30s |
| **Memória** | 128 MB | 256 MB |
| **Responsabilidade** | Gera UUID, Pre-signed URL, salva `PENDING_UPLOAD` | Chama Textract, salva texto e estado final |
| **Isolamento** | Falha do OCR nunca impacta a API de ingestão | ✅ |

---

## Máquina de Estados

O DynamoDB é a **fonte de verdade** do ciclo de vida de cada documento:

```
PENDING_UPLOAD  →  PROCESSING  →  PROCESSED
                                ↘  FAILED_EXTERNAL_DEPENDENCY
```

| Status | Quem define | Condição |
|--------|------------|----------|
| `PENDING_UPLOAD` | Lambda Ingestão | Registro criado; aguardando upload do cliente |
| `PROCESSING` | Lambda OCR | S3 Event recebido; Textract em andamento |
| `PROCESSED` | Lambda OCR | Texto extraído com sucesso |
| `FAILED_EXTERNAL_DEPENDENCY` | Lambda OCR | `ClientError: SubscriptionRequiredException` capturado |

O estado `FAILED_EXTERNAL_DEPENDENCY` garante que o pipeline **nunca fique suspenso indefinidamente** e bloqueia o retry infinito do S3 (*Poison Pill*) sem necessidade de DLQ.

---

## Engenharia de Plataforma (IaC Modular)

```
edn/
├── bootstrap/          # Bootstrap isolado: estado remoto (S3 + DynamoDB locking)
├── live/dev/           # Entrypoint do ambiente dev — orquestra módulos
└── modules/
    ├── lambda/              # Genérico: timeout, memory_size, env vars, source_code_hash
    ├── s3/                  # Bucket privado: versioning, SSE-S3, lifecycle, public access block
    ├── dynamodb/            # PAY_PER_REQUEST com tags obrigatórias
    ├── iam/                 # Role de execução + AWSLambdaBasicExecutionRole
    ├── iam_policy_dynamodb/ # CRUD mínimo (menor privilégio)
    ├── iam_policy_s3/       # PutObject mínimo (menor privilégio)
    ├── api_gateway/         # HTTP API Gateway com integração Lambda proxy
    └── ocr_pipeline/        # Módulo composto: Lambda OCR + IAM + S3 Trigger
```

**Princípios aplicados:** Zero hardcoding · Menor privilégio IAM · Módulos sem `provider` · Tags obrigatórias · `source_code_hash` para deploy automático por diff de artefato.

---

## Observabilidade

- **CloudWatch:** `/aws/lambda/startup-xyz-dev-ingestion` e `/aws/lambda/startup-xyz-dev-ocr`
- **Log de latência do Textract:** `logger.info(f"Textract call completed in {elapsed:.2f}s")`
- **Diagnóstico rápido:**
  ```bash
  aws logs tail /aws/lambda/startup-xyz-dev-ocr --region sa-east-1 --since 30m
  ```

---

## Estrutura da Aplicação

```
application/
├── src/
│   ├── config.py                  # Fail-fast: RuntimeError se env var ausente
│   ├── handlers/                  # Interface HTTP/S3 Event — sem regras de negócio
│   ├── services/                  # Orquestração: ingestion_service, ocr_service
│   └── repositories/             # Adaptadores AWS: S3, DynamoDB, Textract
└── scripts/simulate_client_e2e.py # Prova E2E: API → S3 PUT → Polling DynamoDB
```

---

## Execução

```bash
# Build e deploy
make build-app
make plan && make apply

# Validação E2E
python application/scripts/simulate_client_e2e.py https://<api-id>.execute-api.sa-east-1.amazonaws.com/

# Qualidade
make fmt && make validate && make architecture-check

# Gerar diagrama
cd arquitetura && python arquitetura_serverless_startup_xyz_final.py
```

---

## Roadmap

| Versão | Status | Entrega |
|--------|--------|---------|
| v0.1.0 | ✅ | Bootstrap, IAM, CI/CD scaffolding |
| v0.2.0 | ✅ | Lambda Ingestão, S3, DynamoDB, API Gateway |
| v0.3.0 | ✅ | Pipeline OCR assíncrono (Lambda OCR + Textract + S3 Event) |
| v0.4.0 | ✅ | Máquina de estados e tratamento de erros externos |
| v0.5.0 | 🔮 | Dead Letter Queue (SQS DLQ) para retry automático |
| v0.6.0 | 🔮 | Ambiente `prod` com state e roles separados |
| v0.7.0 | 🔮 | Integração com Amazon Bedrock (sumarização RAG) |
