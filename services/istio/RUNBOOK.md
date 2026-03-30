# Istio Managed Service Runbook

## Backup and restore

- Version-controlled IstioOperator/Helm values plus gateway manifests.
- Restore by reapplying versioned control plane and gateway resources.

## Upgrade strategy

- Canary control plane revision in stage then prod.
- Migrate workloads by namespace label revision update.
- Rollback using prior control plane revision and gateway image.

## Capacity triggers

- Istiod CPU above 70% for 15 minutes: increase replicas/resources.
- Ingress gateway p95 latency above threshold: autoscale and investigate backend saturation.

## Operational checks

- All istiod pods healthy and revision labels expected.
- Ingress gateways have desired replicas and no crash loops.
- mTLS policy state consistent with platform policy.
