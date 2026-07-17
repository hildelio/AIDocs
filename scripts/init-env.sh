#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Uso: $0 <dev|prod>" >&2
  exit 1
fi

ENV="$1"

if ! command -v aws >/dev/null 2>&1; then
  echo "AWS CLI não encontrado no PATH." >&2
  exit 1
fi

echo "Validando identidade AWS..."
aws sts get-caller-identity

echo "Configurando contexto de execução..."
export AWS_REGION="us-east-1"
export AWS_DEFAULT_REGION="us-east-1"
export TF_VAR_environment="$ENV"
export TF_VAR_project="startup-xyz"
export TF_VAR_owner="platform-team"
export TF_VAR_cost_center="engineering"

echo "Contexto preparado:"
echo "- Ambiente: $ENV"
echo "- AWS_REGION: $AWS_REGION"
echo "- AWS_DEFAULT_REGION: $AWS_DEFAULT_REGION"
echo "- TF_VAR_environment: $TF_VAR_environment"
echo "- TF_VAR_project: $TF_VAR_project"
echo "- TF_VAR_owner: $TF_VAR_owner"
echo "- TF_VAR_cost_center: $TF_VAR_cost_center"
echo ""
echo "Próximo passo:"
echo "  cd live/$ENV"
echo "  terraform init"
