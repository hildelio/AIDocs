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

# Terraform files are only allowed inside live/<environment>/ subdirectories
# (e.g., live/dev/, live/prod/) as defined by ADR-001 and ARCHITECTURE_CANON.md.
# provider.tf, backend.tf and versions.tf are REQUIRED inside those subdirectories.
# Guard: reject any .tf files placed directly at the live/ root (depth 1 only).
if find "$repo_root/live" -maxdepth 1 -type f -name '*.tf' 2>/dev/null | grep -q .; then
  fail "Found .tf files at live/ root — Terraform files must be inside live/<environment>/ subdirectories (e.g., live/dev/, live/prod/)"
fi

echo "[architecture-check] Architecture check passed"
