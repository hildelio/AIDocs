# AGENTS.md

## 1. Objetivo

Este documento define a constituição arquitetural e de governança do projeto de infraestrutura em Terraform para a plataforma cloud. Ele estabelece as regras obrigatórias que devem orientar todas as futuras implementações, garantindo consistência técnica, segurança, reuso e facilidade de manutenção.

## 2. Escopo

Este documento é exclusivamente de governança e arquitetura. Não define recursos AWS concretos, nem implementa infraestrutura. Sua função é servir como referência obrigatória para futuras alterações e implementações.

## 3. Regras de Arquitetura

### 3.1 Estrutura de Diretórios

- Objetivo: Garantir organização e separação clara entre bootstrap, ambientes e módulos reutilizáveis.
- Regra: Todo o código Terraform deve residir dentro da pasta raiz chamada terraform/.
- Motivação: Centralizar a implementação em um único ponto evita dispersão de código, facilita a leitura e reduz risco de inconsistência entre ambientes.
- Exemplos:
  - Código Terraform deve estar em terraform/bootstrap/ para infraestrutura de bootstrap.
  - Ambientes devem ficar em terraform/environments/staging/ e terraform/environments/production/.
  - Módulos reutilizáveis devem ficar em terraform/modules/.

### 3.2 Bootstrap Isolado

- Objetivo: Provisionar o Remote State de forma independente e controlada.
- Regra: O diretório terraform/bootstrap/ será independente e conterá os arquivos obrigatórios main.tf, providers.tf, variables.tf, outputs.tf e versions.tf para provisionar o Remote State com S3 e DynamoDB.
- Motivação: O bootstrap deve ser executado uma única vez para criar os recursos básicos de estado remoto e não deve ser alterado após a execução inicial, reduzindo risco de inconsistência e corrupção do estado.
- Exemplos:
  - O bootstrap deve ser responsável somente pela criação do bucket S3 e da tabela DynamoDB do Terraform State.
  - Após a execução inicial, qualquer alteração futura no bootstrap deve ser tratada como uma revisão explícita.

### 3.3 Ambientes

- Objetivo: Estruturar ambientes de forma consistente, previsível e isolada.
- Regra: Os ambientes devem ficar em terraform/environments/ com subpastas staging/ e production/.
- Motivação: Ambientes distintos precisam de isolamento lógico e operacional, além de permitir evolução independente entre homologação e produção.
- Exemplos:
  - Cada ambiente deve possuir os arquivos main.tf, providers.tf, backend.tf, variables.tf, outputs.tf, terraform.tfvars e locals.tf.
  - O arquivo locals.tf deve definir a variável environment com o valor correspondente ao ambiente.

### 3.4 Módulos Orientados a Recursos

- Objetivo: Promover reuso, coesão e baixo acoplamento.
- Regra: Os módulos devem ficar em terraform/modules/ e ser nomeados pelo recurso AWS que representam, por exemplo: api-gateway, lambda, s3, iam.
- Motivação: Módulos orientados a recursos tornam o código mais intuitivo, simplificam manutenção e permitem reutilização em diferentes ambientes.
- Exemplos:
  - Um módulo para API Gateway deve conter lógica específica para esse recurso.
  - Um módulo para IAM deve ser granular e especializado.

### 3.5 Módulos IAM Granulares

- Objetivo: Aplicar princípio de menor privilégio e reduzir risco de excesso de permissões.
- Regra: O módulo IAM deve ser granular, com responsabilidade bem definida e políticas específicas por uso.
- Motivação: Módulos IAM amplos aumentam a superfície de ataque e dificultam auditoria e manutenção.
- Exemplos:
  - Um módulo IAM para execução de Lambda deve receber apenas as permissões mínimas necessárias.
  - Políticas devem ser separadas por responsabilidade sempre que possível.

### 3.6 Controle de Versão

- Objetivo: Garantir reprodutibilidade e compatibilidade entre ambientes.
- Regra: É obrigatório o arquivo versions.tf em todos os módulos e ambientes.
- Motivação: Definir versões de providers e Terraform evita incompatibilidades e melhora previsibilidade da execução.
- Exemplos:
  - Um módulo de S3 deve incluir versions.tf com as versões mínimas ou fixas de Terraform e providers.
  - O ambiente staging deve incluir versions.tf para garantir consistência com os módulos utilizados.

### 3.7 Tags Obrigatórias

- Objetivo: Garantir governança, rastreabilidade e custeio.
- Regra: Todos os módulos devem receber uma variável map(string) chamada tags com os campos obrigatórios: project, environment, owner, cost_center e managed_by.
- Motivação: Tags padronizadas facilitam auditoria, cobrança, gestão de custos e políticas de governança.
- Exemplos:
  - Exemplo de estrutura: tags = { project = "startup-xyz", environment = "staging", owner = "platform-team", cost_center = "engineering", managed_by = "terraform" }.

### 3.8 Inputs e Outputs

- Objetivo: Evitar hardcoding e promover encapsulamento.
- Regra: Todos os valores devem passar por variáveis. Recursos nunca devem ser expostos diretamente; a interface de módulos deve ocorrer via outputs.tf.
- Motivação: Inputs e outputs bem definidos tornam o código mais seguro, reutilizável e simples de evoluir.
- Exemplos:
  - Não é permitido hardcodear nomes, ARNs ou IDs diretamente no módulo.
  - Cada módulo deve expor apenas as informações relevantes por meio de outputs.

### 3.9 Providers

- Objetivo: Centralizar definição de providers em ambientes e evitar acoplamento indevido.
- Regra: Módulos não possuem provider. Providers ficam apenas nas pastas de environments.
- Motivação: Separar a declaração de providers dos módulos reduz acoplamento e facilita evolução da infraestrutura.
- Exemplos:
  - O provider AWS deve ser definido em terraform/environments/staging/providers.tf e terraform/environments/production/providers.tf.
  - Módulos reutilizáveis devem apenas consumir o provider fornecido pelo ambiente.

## 4. Restrições Obrigatórias

- Não alterar arquivos existentes.
- Não criar estrutura de pastas do Terraform ou código HCL (.tf).
- Não criar README.md ou documentação adicional fora do AGENTS.md.

## 5. Regras de Implementação Futura

### 5.1 Princípios Gerais

- Objetivo: Garantir que futuras implementações sigam um padrão consistente.
- Regra: Qualquer alteração futura deve respeitar este AGENTS.md e não pode contradizê-lo.
- Motivação: O documento serve como constituição técnica do projeto.
- Exemplos:
  - Se uma futura implementação criar um módulo fora de terraform/modules/, ela deve ser reavaliada.
  - Se uma futura implementação introduzir hardcoding em vez de variável, deve ser recusada.

### 5.2 Critério de Interrupção

- Objetivo: Evitar decisões técnicas inconsistentes.
- Regra: Em caso de ambiguidade, conflito ou falta de informação técnica, a execução deve ser interrompida e uma lista objetiva de dúvidas deve ser apresentada.
- Motivação: Suposições prematuras podem comprometer segurança, governança e manutenção da plataforma.
- Exemplos:
  - Se uma futura solicitação não definir o ambiente ou o tipo de recurso, a execução deve parar para esclarecimento.

## 6. Padrões de Qualidade Esperados

- Código deve ser simples, modular e de baixo acoplamento.
- Código deve favorecer reuso, observabilidade, segurança e facilidade de evolução.
- A implementação futura deve considerar boas práticas de Terraform e princípios do AWS Well-Architected Framework.

## Processo de Revisão Arquitetural

- Antes de criar, mover ou excluir diretórios, compare a alteração com o `docs/architecture/ARCHITECTURE_CANON.md`. Em caso de divergência, interrompa a execução.
- O agente está ESTRITAMENTE PROIBIDO de criar novos diretórios, mover arquivos ou alterar a arquitetura para tentar corrigir erros de validação do Terraform. O agente deve sempre diagnosticar a causa raiz primeiro e solicitar aprovação humana caso a solução envolva mudanças estruturais.
- Alterações nos arquivos `providers.tf`, `versions.tf`, `backend.tf` e `terraform/bootstrap/main.tf` exigem a exibição obrigatória do diff no chat e aprovação explícita do Tech Lead antes de prosseguir.
- É PROIBIDO declarar `provider`, `backend` ou `terraform.required_providers` dentro de qualquer diretório `modules/`.
- Nenhum módulo poderá ser criado sem que exista previamente um documento de contrato em `docs/contracts/` contendo: Objetivo, Inputs, Outputs, Dependências, Consumidores, Recursos AWS e Critérios de Aceite.
- Módulos IAM iniciais devem criar APENAS Roles e Trust Policies. Resource Policies (para S3, Lambda, etc.) só devem ser criadas após ou junto com a existência dos respectivos recursos para evitar permissões especulativas.
