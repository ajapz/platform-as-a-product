# Platform Bootstrap Scripts

## Bootstrap policy bundles

Run from repository root:

- `pwsh ./scripts/bootstrap-policies.ps1`

Options:

- `-SkipKyvernoInstall` to skip Kyverno installation/upgrade and only apply local policies.

Execution order:

1. `kubernetes/namespaces`
2. `kubernetes/rbac`
3. Kyverno install/upgrade (unless skipped)
4. `policies/kyverno`
5. `kubernetes/network-policies`
