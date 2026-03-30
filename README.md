# Platform-as-a-Product

Opinionated managed-platform baseline for teams running reliable services on Kubernetes with Terraform, security guardrails, and automation.

## What this repo provides

- Terraform baseline to standardize namespaces and resource controls across `dev`, `stage`, and `prod`.
- Kubernetes guardrails for RBAC and Network Policies.
- Kyverno and Conftest policy-as-code guardrails for admission and CI.
- High-availability defaults for PostgreSQL, Elasticsearch, and Istio.
- Python automation to validate manifests, enforce HA checks, and generate baseline policy.
- CI workflow with Terraform lint/security, Kubernetes schema checks, policy checks, and scheduled drift plan artifacts.

## Repository layout

- `terraform/` Infrastructure as code for platform baseline.
- `kubernetes/` Cluster-native policies and workload standards.
- `services/` HA value presets for common platform dependencies.
- `automation/python/` Platform automation CLI and tests.
- `docs/` Platform operating model and adoption guidance.
- `policies/` Policy-as-code for cluster admission and CI validation.

## Quick start

1. Review and customize `terraform/environments/dev/terraform.tfvars`, `terraform/environments/stage/terraform.tfvars`, and `terraform/environments/prod/terraform.tfvars`.
2. Apply Terraform baseline:
   - `cd terraform/environments/<env>`
   - `terraform init`
   - `terraform plan`
   - `terraform apply`
3. Apply Kubernetes baseline manifests:
   - `kubectl apply -f kubernetes/namespaces/`
   - `kubectl apply -f kubernetes/rbac/`
   - `kubectl apply -f kubernetes/network-policies/`
4. Validate manifests and policy with Python automation:
   - `cd automation/python`
   - `python -m pip install -e .[dev]`
   - `platformctl validate-manifests ../../kubernetes`
   - `platformctl check-ha ../../kubernetes/workloads`

## Phase 2 automation

- Generate namespace-wide network policy bundles:
   - `platformctl generate-netpol-bundle --namespaces-file ../../kubernetes/namespaces/platform-namespaces.yaml --output-dir ../../kubernetes/network-policies`
- Canonical generated bundle (tracked in git):
   - `kubernetes/network-policies/generated/*.yaml`
   - refresh with: `platformctl generate-netpol-bundle --namespaces-file ../../kubernetes/namespaces/platform-namespaces.yaml --output-dir ../../kubernetes/network-policies/generated`
- Bootstrap policy bundles in apply order:
   - `pwsh ./scripts/bootstrap-policies.ps1`
   - `pwsh ./scripts/bootstrap-policies.ps1 -SkipKyvernoInstall`

## CI configuration for Terraform plan

Set these repository secrets for full CI plan support:

- `KUBECONFIG_B64`: base64-encoded kubeconfig for the target cluster contexts.
- `TF_BACKEND_CONFIG_B64`: optional base64-encoded backend config (`backend.hcl` format). If omitted, CI runs `terraform init -backend=false` and still validates configuration.

## Reliability docs and service runbooks

- SLO/SLI and alerting blueprint: `docs/slo-sli-and-alerting.md`
- PostgreSQL runbook: `services/postgresql/RUNBOOK.md`
- Elasticsearch runbook: `services/elasticsearch/RUNBOOK.md`
- Istio runbook: `services/istio/RUNBOOK.md`

## Platform principles

- Default-secure: least privilege and deny-by-default network posture.
- Reliability-first: anti-affinity, disruption budgets, autoscaling, and capacity controls.
- Golden paths: paved road templates teams can adopt quickly.
- Automated governance: policy checks and drift detection in CI/CD.

See `docs/platform-operating-model.md` for operational details.
