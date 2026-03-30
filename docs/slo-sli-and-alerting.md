# Platform SLO, SLI, and Alerting

## Objectives

Define measurable reliability targets and operational signals for managed platform services.

## Global platform SLOs

- Kubernetes platform availability: 99.95% monthly
- Stateful platform services (PostgreSQL, Elasticsearch): 99.9% monthly
- Istio ingress success rate: 99.9% monthly

## SLIs and alert thresholds

### Kubernetes workloads

- SLI: Deployment available replicas / desired replicas
- Alert: available replicas below desired for 10 minutes (critical)
- SLI: Pod restart rate
- Alert: restart rate exceeds 5 restarts per pod in 15 minutes (warning)

### PostgreSQL

- SLI: Primary availability
- Alert: primary down for 2 minutes (critical)
- SLI: replication lag
- Alert: lag above 30 seconds for 10 minutes (warning)
- SLI: storage utilization
- Alert: above 80% (warning), above 90% (critical)

### Elasticsearch

- SLI: cluster health
- Alert: yellow for 15 minutes (warning), red for 5 minutes (critical)
- SLI: JVM memory pressure
- Alert: above 75% for 10 minutes (warning), above 85% for 5 minutes (critical)

### Istio

- SLI: ingress 5xx rate
- Alert: above 2% for 5 minutes (critical)
- SLI: p95 latency
- Alert: above service-specific threshold for 10 minutes (warning)

## Incident response integration

- P1 alerts page primary on-call immediately.
- P2 alerts route to team on-call and slack channel.
- Every SLO burn event must create an incident review item.
