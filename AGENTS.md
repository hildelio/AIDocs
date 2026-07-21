# AGENTS.md

## 1. Objetivo

Este documento define a constituição arquitetural e de governança do projeto de infraestrutura em Terraform para a plataforma cloud. Ele estabelece as regras obrigatórias que devem orientar todas as futuras implementações, garantindo consistência técnica, segurança, reuso e facilidade de manutenção.

## 2. Escopo

Este documento é exclusivamente de governança e arquitetura. Não define recursos AWS concretos, nem implementa infraestrutura. Sua função é servir como referência obrigatória para futuras alterações e implementações.

## 3. Regras de Arquitetura

### 3.1 Estrutura de Diretórios Canônica

- Objetivo: Garantir organização e separação clara entre bootstrap, ambientes (`live`) e módulos reutilizáveis.
- Regra: A estrutura de diretórios deve seguir o `docs/architecture/ARCHITECTURE_CANON.md`. O código Terraform reside em diretórios específicos na raiz do projeto.
- Motivação: Manter uma estrutura previsível evita a dispersão de código, facilita a governança e reduz a inconsistência entre ambientes.
- Exemplos:
  - `bootstrap/`: Contém a infraestrutura para o state backend do Terraform.
  - `live/dev/` e `live/prod/`: Pontos de entrada que consomem módulos para compor os ambientes.
  - `modules/`: Contém todos os módulos Terraform reutilizáveis.

### 3.2 Bootstrap Isolado

- Objetivo: Provisionar o Remote State de forma independente e controlada.
- Regra: O diretório `bootstrap/` é autônomo, não consome outros módulos e contém a definição dos recursos (S3, DynamoDB) para o backend do Terraform.
- Motivação: O bootstrap é executado uma única vez para criar a fundação do state. Isolá-lo previne corrupção do state e alterações acidentais.
- Exemplos:
  - O `bootstrap/` é responsável exclusivamente pela criação do bucket S3 e da tabela DynamoDB para o Terraform State.

### 3.3 Ambientes (`live`)

- Objetivo: Estruturar ambientes de forma consistente, previsível e isolada.
- Regra: Os ambientes são definidos nos diretórios `live/`, com subpastas para `dev/` e `prod/`.
- Motivação: Ambientes distintos precisam de isolamento lógico e operacional. A estrutura `live/` permite a composição explícita de módulos por ambiente (ver `ADR-001`).
- Exemplos:
  - Cada diretório de ambiente (ex: `live/dev/`) contém os arquivos `main.tf`, `providers.tf`, `backend.tf`, etc., para orquestrar o consumo dos módulos.

### 3.4 Módulos Orientados a Recursos

- Objetivo: Promover reuso, coesão e baixo acoplamento.
- Regra: Módulos residem em `modules/` e são nomeados pelo recurso ou capacidade que representam (ex: `iam`, `s3`, `lambda`).
- Motivação: Módulos especializados tornam o código mais intuitivo, simplificam a manutenção e são facilmente reutilizáveis em diferentes ambientes.
- Exemplos:
  - O módulo `lambda` deve conter a lógica para provisionar uma função Lambda e suas configurações associadas.
  - O módulo `iam` deve ser granular e focado em papéis e políticas específicas.

### 3.5 Módulos IAM Granulares

- Objetivo: Aplicar o princípio de menor privilégio.
- Regra: O módulo IAM deve ser granular, com políticas específicas por caso de uso para reduzir o excesso de permissões.
- Motivação: Módulos IAM amplos aumentam a superfície de ataque e dificultam a auditoria.
- Exemplos:
  - Um módulo IAM para execução de Lambda deve receber apenas as permissões mínimas necessárias.

### 3.6 Controle de Versão

- Objetivo: Garantir reprodutibilidade e compatibilidade.
- Regra: É obrigatório o uso de `versions.tf` em `bootstrap/` e em cada ambiente (`live/*`).
- Motivação: Definir versões de providers e do Terraform evita que atualizações inesperadas quebrem a compatibilidade.
- Exemplos:
  - O diretório `live/dev/` deve ter um `versions.tf` para garantir consistência com os módulos utilizados.

### 3.7 Tags Obrigatórias

- Objetivo: Garantir governança, rastreabilidade e custeio.
- Regra: Todos os módulos devem receber uma variável `map(string)` chamada `tags` e propagá-la para os recursos. As tags obrigatórias são: `project`, `environment`, `owner`, `cost_center` e `managed_by`.
- Motivação: Tags padronizadas são essenciais para auditoria, gestão de custos e automação.
- Exemplos:
  - `tags = { project = "startup-xyz", environment = "dev", owner = "platform-team", cost_center = "engineering", managed_by = "terraform" }`

### 3.8 Inputs e Outputs

- Objetivo: Evitar hardcoding e promover encapsulamento.
- Regra: Valores não devem ser "hardcodados". A interface de um módulo com o resto do sistema deve ser feita exclusivamente via `variables.tf` (entradas) e `outputs.tf` (saídas).
- Motivação: Interfaces bem definidas tornam o código mais seguro, reutilizável e fácil de manter.
- Exemplos:
  - Um ARN de um recurso não deve ser "hardcodado" dentro de um módulo; ele deve ser recebido como uma variável.

### 3.9 Providers

- Objetivo: Centralizar a definição de providers nos ambientes.
- Regra: Módulos (`modules/`) não devem conter blocos `provider`. Eles são declarados apenas nos pontos de entrada (`bootstrap/` e `live/*`).
- Motivação: Separar a declaração de providers dos módulos reutilizáveis reduz o acoplamento e facilita a gestão da configuração (ex: múltiplas regiões ou contas).
- Exemplos:
  - O provider AWS deve ser definido em `live/dev/providers.tf`.
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
- É ESTRITAMENTE PROIBIDO executar comandos que alterem a raiz do repositório (como `git init`), criar branches, alterar remotes ou realizar commits sem a autorização explícita do operador.
- Toda alteração em arquivos dentro de `.github/workflows/` exige apresentação do diff e justificativa. Você não pode substituir Actions ou alterar estratégias de CI/CD automaticamente para tentar corrigir falhas.
- Alterações nos arquivos `providers.tf`, `versions.tf`, `backend.tf` e `terraform/bootstrap/main.tf` exigem a exibição obrigatória do diff no chat e aprovação explícita do Tech Lead antes de prosseguir.
- É PROIBIDO declarar `provider`, `backend` ou `terraform.required_providers` dentro de qualquer diretório `modules/`.
- Apenas módulos públicos, reutilizáveis ou consumidos por outros módulos exigem contrato prévio em `docs/contracts/` contendo: Objetivo, Inputs, Outputs, Dependências, Consumidores, Recursos AWS e Critérios de Aceite. Módulos internos, experimentais ou de escopo limitado a um único ambiente podem ser implementados sem contrato prévio, desde que documentados em ADR.
- Módulos IAM iniciais devem criar APENAS Roles e Trust Policies. Resource Policies (para S3, Lambda, etc.) só devem ser criadas após ou junto com a existência dos respectivos recursos para evitar permissões especulativas.
