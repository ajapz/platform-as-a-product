$ErrorActionPreference = "Stop"

param(
    [switch]$SkipKyvernoInstall
)

function Invoke-ApplyDirectory {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    if (-not (Test-Path -Path $Path)) {
        throw "Required path not found: $Path"
    }

    Write-Host "Applying $Label from $Path ..."
    kubectl apply -f $Path
}

if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
    throw "kubectl is required but not found in PATH."
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

Invoke-ApplyDirectory -Path (Join-Path $repoRoot "kubernetes/namespaces") -Label "namespaces"
Invoke-ApplyDirectory -Path (Join-Path $repoRoot "kubernetes/rbac") -Label "RBAC policies"

if (-not $SkipKyvernoInstall) {
    Write-Host "Installing or upgrading Kyverno ..."
    kubectl apply -f https://github.com/kyverno/kyverno/releases/download/v1.12.5/install.yaml
}

Invoke-ApplyDirectory -Path (Join-Path $repoRoot "policies/kyverno") -Label "Kyverno cluster policies"
Invoke-ApplyDirectory -Path (Join-Path $repoRoot "kubernetes/network-policies") -Label "network policies"

Write-Host "Bootstrap complete."
Write-Host "Applied order: namespaces -> RBAC -> Kyverno install -> Kyverno policies -> network policies"
