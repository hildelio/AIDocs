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

Write-Host '[architecture-check] Architecture check passed'
