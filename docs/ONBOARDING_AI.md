# Onboarding para Agentes de IA

Versão: 1.0
Data: 2026-07-16

## 1. Visão do Projeto

Este repositório contém os ativos da plataforma para o ambiente de nuvem da Startup XYZ, gerenciados via Terraform. O objetivo é garantir uma infraestrutura consistente, segura, reutilizável e de fácil manutenção, seguindo as melhores práticas de Engenharia de Plataforma e IaC.

## 2. Estrutura Oficial (Canônica)

A estrutura de diretórios é a fonte da verdade para a organização do código. Qualquer desvio deve ser tratado como uma violação de arquitetura. A estrutura canônica é definida em `docs/architecture/ARCHITECTURE_CANON.md`.

- `bootstrap/`: Código Terraform para criar o backend de state (S3/DynamoDB). É executado uma única vez e raramente modificado.
- `live/`: Pontos de entrada para cada ambiente (`dev`, `prod`). É aqui que os módulos são consumidos e orquestrados para formar um ambiente completo.
- `modules/`: Catálogo de módulos Terraform reutilizáveis e orientados a recursos (ex: `iam`, `s3`).
- `scripts/`: Scripts de automação e governança (ex: `architecture-check.sh`).
- `docs/`: Documentação do projeto.
  - `architecture/`: A arquitetura canônica.
  - `adr/`: Decisões de arquitetura que registram mudanças e suas justificativas.
  - `contracts/`: Contratos de interface para cada módulo, definindo inputs/outputs.
- `Makefile`: Comandos para automação de tarefas comuns (lint, validate, etc.).

## 3. Ordem Obrigatória de Leitura dos Documentos

Para entender completamente o projeto, siga esta ordem de leitura:

1.  **`docs/architecture/ARCHITECTURE_CANON.md`**: Entender a estrutura de diretórios oficial.
2.  **`docs/adr/*.md`**: Ler todas as Decisões de Arquitetura para compreender as evoluções do projeto.
3.  **`AGENTS.md`**: Revisar as regras constitucionais de governança. **Atenção:** ADRs podem sobrepor regras deste arquivo.
4.  **`README.md`**: Visão geral do projeto e comandos úteis.
5.  **`docs/contracts/*.md`**: Antes de usar ou alterar um módulo, leia seu contrato.
6.  **`.github/workflows/*.yml`**: Para entender o processo de Integração Contínua.

## 4. Regras Inegociáveis de Governança

Extraídas de `AGENTS.md` e `ARCHITECTURE_CANON.md`.

- **Resolução de Conflitos**: Em caso de divergência entre documentos, a hierarquia de precedência é: `docs/adr/` > `docs/architecture/ARCHITECTURE_CANON.md` > `AGENTS.md`. Qualquer divergência encontrada **deve ser reportada**.
- **Isolamento de Módulos**: Módulos em `modules/` **NUNCA** devem conter `provider`, `backend` ou `versions.tf`.
- **Independência do Bootstrap**: O diretório `bootstrap/` é autônomo, não consome módulos e não depende de remote state.
- **Contratos de Módulo**: Nenhum módulo pode ser criado ou alterado sem um contrato correspondente e atualizado em `docs/contracts/`.
- **Revisão de Arquivos Core**: Alterações em `providers.tf`, `backend.tf`, `bootstrap/main.tf` ou nos workflows de CI/CD (`.github/workflows/`) exigem a exibição do `diff` e aprovação humana explícita.
- **Tags Obrigatórias**: Todos os recursos devem ser marcados com as tags: `project`, `environment`, `owner`, `cost_center`, e `managed_by`.
- **Menor Privilégio**: Módulos IAM devem ser granulares e criar apenas as permissões estritamente necessárias.

## 5. Fluxos de Trabalho (Terraform, Git e CI/CD)

### Terraform
- **State Remoto**: O state é armazenado em um backend S3, configurado por ambiente nos arquivos `live/<env>/backend.<env>.hcl`.
- **Composição**: Ambientes (`live/*`) compõem e consomem os módulos reutilizáveis de `modules/`.
- **Validação Local**: Use os comandos do `Makefile` para garantir a qualidade antes de submeter. O comando `make doctor` executa todas as checagens de uma vez.

### Git
- A branch principal é a `main`.
- Todas as alterações devem ser propostas via Pull Requests.

### CI/CD
- **GitHub Actions** são usadas para validação contínua.
- **`terraform-check.yml`**: Executado em todos os pushes e PRs. Realiza checagens de arquitetura, formatação (`fmt`), inicialização (`init`), validação (`validate`) e segurança (`tflint`, `tfsec`).
- **`terraform-ci.yml`**: Além das checagens acima, executa o `terraform plan` em PRs para a `main` e pushes na `main`.

## 6. O que o Agente NUNCA pode fazer

- Executar `git init`, `git commit`, `git push`, alterar branches ou remotes sem instrução explícita.
- **Inventar estruturas de diretórios** ou mover arquivos para contornar erros de validação. A causa raiz do erro deve ser diagnosticada.
- Declarar `provider`, `backend` ou `terraform.required_providers` dentro do diretório `modules/`.
- Criar um módulo sem que seu contrato (`docs/contracts/`) exista previamente.
- Modificar arquivos de CI/CD, state, providers ou bootstrap sem o processo de revisão explícito (apresentar `diff` e pedir aprovação).

## 7. Checklist Pré-Alteração de Código

- [ ] Li e entendi o `docs/contracts/` do(s) módulo(s) que irei alterar?
- [ ] Minha alteração é compatível com a `docs/architecture/ARCHITECTURE_CANON.md`?
- [ ] Verifiquei se existe uma `ADR` em `docs/adr/` que impacta minha alteração?
- [ ] Minha alteração viola alguma regra do `AGENTS.md`? Se sim, a violação é intencional, documentada em uma ADR e reportada?
- [ ] Executei `make doctor` localmente e todos os testes passaram?
- [ ] Se estou criando um novo módulo, já criei e aprovei o contrato em `docs/contracts/` primeiro?
- [ ] Se a mudança afeta um arquivo core (CI/CD, state, providers, bootstrap), estou pronto para apresentar o `diff` para aprovação?
