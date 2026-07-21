$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot

if (Test-Path (Join-Path $repoRoot 'terraform/environments')) {
    Write-Error 'Found forbidden directory: terraform/environments'
}

if (Test-Path (Join-Path $repoRoot 'terraform/modules')) {
    Write-Error 'Found forbidden directory: terraform/modules'
}

$forbiddenFiles = Get-ChildItem -Path (Join-Path $repoRoot 'modules') -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -in @('provider.tf','backend.tf','versions.tf') }

if ($forbiddenFiles) {
    Write-Error 'Found forbidden Terraform files inside modules/'
}

# Terraform files are only allowed inside live/<environment>/ subdirectories
# (e.g., live/dev/, live/prod/) as defined by ADR-001 and ARCHITECTURE_CANON.md.
# provider.tf, backend.tf and versions.tf are REQUIRED inside those subdirectories.
# Guard: reject any .tf files placed directly at the live/ root (depth 1 only).
$liveRootTfFiles = Get-ChildItem -Path (Join-Path $repoRoot 'live') -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -eq '.tf' }

if ($liveRootTfFiles) {
    Write-Error 'Found .tf files at live/ root — Terraform files must be inside live/<environment>/ subdirectories (e.g., live/dev/, live/prod/)'
}

Write-Host '[architecture-check] Architecture check passed'
