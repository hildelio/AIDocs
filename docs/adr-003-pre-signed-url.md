# ADR-003: Acesso Seguro ao S3 via Pre-signed URLs

## Status
Aceito

## Contexto
O aplicativo cliente precisa fazer upload e download de arquivos (ex: faturas, recibos, imagens) diretamente do navegador ou aplicativo móvel. No entanto, o bucket S3 não deve ser exposto publicamente para evitar vazamentos de dados, e passar binários pesados através do API Gateway + Lambda é ineficiente em termos de custos (FinOps) e performance, além de esbarrar nos limites de payload (10MB no API Gateway, 6MB na Lambda).

## Decisão
A plataforma adotará o padrão de **Pre-signed URLs** (URLs pré-assinadas) para todas as operações diretas no S3 a partir de clientes externos.

## Como funciona
1. **Solicitação:** O cliente autenticado solicita uma URL ao backend (via API Gateway -> Lambda).
2. **Assinatura:** A Lambda, usando a role IAM `lambda_exec_role` com permissões adequadas no bucket `app-data`, gera uma Pre-signed URL (GET para download, PUT para upload) com validade curta (ex: 5 a 15 minutos).
3. **Acesso Direto:** O cliente usa essa URL para fazer o upload ou download diretamente de/para o S3, fazendo bypass no API Gateway/Lambda para a transferência do arquivo em si.

## Consequências

### Positivas
- **Segurança Aprimorada:** O bucket S3 permanece totalmente privado (bloqueio público mantido). O acesso só ocorre via credenciais temporárias amarradas a um objeto específico.
- **Eficiência e Custos (FinOps):** Evitamos custos de transferência de dados através do API Gateway e tempo de execução na Lambda. O tráfego pesado vai direto para o S3.
- **Performance:** Menos latência, já que pulamos intermediários na transferência do binário. Não há risco de timeout na Lambda durante uploads lentos.

### Negativas / Mitigações
- Requer uma etapa extra de negociação (pedir URL antes do upload/download) na lógica do frontend.
- O controle de expiração é baseado no tempo gerado na assinatura, portanto, a URL não pode ser revogada antes desse prazo; como mitigação, usaremos prazos de expiração curtos.
