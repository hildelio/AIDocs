#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

fail() {
  echo "[architecture-check] $1" >&2
  exit 1
}

if [ -d "$repo_root/terraform/environments" ]; then
  fail "Found forbidden directory: terraform/environments"
fi

if [ -d "$repo_root/terraform/modules" ]; then
  fail "Found forbidden directory: terraform/modules"
fi

if find "$repo_root/modules" -type f \( -name 'provider.tf' -o -name 'backend.tf' -o -name 'versions.tf' \) 2>/dev/null | grep -q .; then
  fail "Found forbidden Terraform files inside modules/"
fi

if find "$repo_root/live" -type f \( -name 'provider.tf' -o -name 'backend.tf' -o -name 'versions.tf' \) 2>/dev/null | grep -q .; then
  fail "Found forbidden Terraform files inside live/"
fi

echo "[architecture-check] Architecture check passed"
