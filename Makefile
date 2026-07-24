.PHONY: architecture-check fmt validate plan apply destroy init lint sec doctor

ENV ?= dev
TERRAFORM_DIR := live/$(ENV)

build-app:
	powershell -NoProfile -ExecutionPolicy Bypass -Command "if (Test-Path 'artifact.zip') { Remove-Item 'artifact.zip' }; Compress-Archive -Path 'application/src', 'application/requirements.txt' -DestinationPath 'artifact.zip'"

architecture-check:
	powershell -NoProfile -ExecutionPolicy Bypass -File scripts/architecture-check.ps1

fmt:
	terraform fmt -recursive bootstrap $(TERRAFORM_DIR) modules

validate:
	powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-Location '$(TERRAFORM_DIR)'; terraform validate"

plan:
	powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-Location '$(TERRAFORM_DIR)'; terraform plan -out=tfplan"

apply:
	powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-Location '$(TERRAFORM_DIR)'; terraform apply tfplan"

destroy:
	powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-Location '$(TERRAFORM_DIR)'; terraform destroy -auto-approve"

init:
	powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-Location '$(TERRAFORM_DIR)'; terraform init '-backend-config=backend.$(ENV).hcl'"

lint:
	terraform fmt -check -recursive bootstrap $(TERRAFORM_DIR) modules

sec:
	@powershell -NoProfile -Command "if (Get-Command tfsec -ErrorAction SilentlyContinue) { tfsec $(TERRAFORM_DIR) } else { Write-Host 'tfsec not installed' }"

doctor: architecture-check
	terraform version
	aws --version
	aws sts get-caller-identity
	$(MAKE) fmt
	$(MAKE) validate
	$(MAKE) lint
	$(MAKE) sec
