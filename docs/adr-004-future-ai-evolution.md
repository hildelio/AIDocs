# ADR-004: Fluxo Orientado a Eventos (S3 -> Lambda -> IA)

## Status
Proposto

## Contexto
Temos o requisito futuro de extrair dados de faturas ou documentos PDF/Imagens processando-os com IA (ex: Amazon Textract). O processamento desses documentos pode ser demorado, impossibilitando a execução síncrona dentro da janela de timeout do API Gateway (máximo 30 segundos).

## Decisão
Implementaremos um fluxo arquitetural Assíncrono Orientado a Eventos (Event-Driven) acoplado nativamente na AWS. A cadeia de invocação será orientada pelos eventos do bucket S3.

## Fluxo Arquitetural
1. **Upload:** O usuário final faz o upload da fatura para o bucket `app-data` (utilizando uma Pre-signed URL, conforme [ADR-003](adr-003-pre-signed-url.md)).
2. **Notificação de Evento:** O S3 é configurado com *Event Notifications* para disparar um evento `s3:ObjectCreated:*` quando um novo arquivo `.pdf` ou imagem cair na pasta/prefixo `inbox/`.
3. **Invocação Assíncrona:** O evento invoca automaticamente uma Lambda especializada (ex: `document-processor-lambda`).
4. **Processamento (Textract):** A Lambda chama o serviço Amazon Textract, passando o objeto S3 como referência, para realizar o OCR ou extração de dados estruturados.
5. **Persistência e Notificação:** O resultado do Textract é processado e salvo na tabela DynamoDB. O frontend, se necessário, pode ser notificado (via WebSocket/IoT Core) ou fazer polling do status via API.

## Consequências

### Positivas
- **Desacoplamento:** O cliente não fica bloqueado aguardando o processamento assíncrono.
- **Escalabilidade Nativa:** O S3 e a Lambda gerenciam os picos de uploads sem sobrecarregar gargalos síncronos. Se ocorrerem milhares de uploads ao mesmo tempo, as instâncias Lambda escalam de acordo.
- **Resiliência:** A integração S3 -> Lambda suporta tentativas (retries) automáticas em caso de falha temporária.

### Negativas / Mitigações
- Necessita de gerenciamento adequado de infraestrutura (Terraform) para criar o recurso `aws_s3_bucket_notification` com permissões adequadas em `aws_lambda_permission`.
- A complexidade do frontend aumenta (precisa lidar com estado assíncrono - "processando", "concluído", em vez de resposta imediata).
