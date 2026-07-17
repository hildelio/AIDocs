# Startup XYZ Platform

## Architecture

This repository contains the foundational platform assets for the Startup XYZ cloud environment, including the bootstrap layer, live environments, reusable Terraform modules, and CI/CD workflows.

## Getting Started

1. Review the governance rules in [AGENTS.md](AGENTS.md).
2. Initialize the dev environment from [live/dev](live/dev).
3. Run the local quality gate with `make doctor`.

## Directory Layout

- [bootstrap](bootstrap) - isolated bootstrap resources for Terraform state.
- [live](live) - environment entrypoints such as dev and prod.
- [modules](modules) - reusable Terraform modules.
- [scripts](scripts) - operational and governance helpers.
- [docs](docs) - architecture canon, ADRs, contracts, and diagrams.

## Make Commands

- `make architecture-check`
- `make fmt`
- `make validate`
- `make doctor`

## CI/CD

GitHub Actions workflows are defined under [.github/workflows](.github/workflows) to validate Terraform changes on pull requests and pushes.

## Module Contracts

The module contracts live in [docs/contracts](docs/contracts) and describe interfaces, dependencies, and acceptance criteria.

## Roadmap

- v0.1.0 - bootstrap, IAM module, and CI/CD scaffolding.
- v0.2.0 - expand module catalog and environment promotion.
