# Architecture Canon

Version: 1.0.0
Last Updated: 2026-07-16
Owner: Platform Team

## Official Tree

```text
bootstrap/
live/dev/
live/prod/
modules/iam/
modules/s3/
modules/lambda/
scripts/
docs/
Makefile
```

## Ownership

- bootstrap, modules, and scripts belong to Platform.
- live belongs to Application.

## Immutable Rules

- Modules MUST NOT contain provider, backend, or versions.tf files.
- The bootstrap directory is independent, never consumes modules, never depends on remote state, and is changed only through ADRs.
- Terraform code must remain under the canonical structure above.
- **Lifecycle Separation (Infra vs. App):** Infrastructure code (Terraform) and Application code (e.g., Python scripts for Lambdas, zip artifacts) MUST maintain independent evolution, testing, and deployment lifecycles to prevent tight coupling. App artifacts should be injected into infrastructure modules (e.g., via `live/`), never hardcoded within the module definition. Infrastructure modules MUST NOT contain business logic or application source code.
