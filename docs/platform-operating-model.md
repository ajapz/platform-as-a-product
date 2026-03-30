# Platform Operating Model

## Mission

Enable product teams to ship and run secure, scalable, and resilient services by providing managed platform capabilities with clear SLOs and paved roads.

## Managed service catalog

- Kubernetes cluster baseline
- PostgreSQL deployment standards
- Elasticsearch deployment standards
- Istio service mesh baseline
- Terraform modules for platform controls

## Reliability targets

- Control plane availability target: 99.95%
- Stateful platform services availability target: 99.9%
- Platform incident response:
  - P1: acknowledge in 15 minutes
  - P2: acknowledge in 30 minutes

## Security guardrails

- RBAC with separate personas:
  - Platform admin
  - Namespace deployer
  - Read-only observer
- Network policy baseline:
  - Default deny ingress and egress
  - Explicit allow for kube-dns
  - Namespace-level allow-list patterns
- Secrets and credentials:
  - No static credentials in repository
  - Integrate external secret manager in runtime

## Scalability and availability patterns

- Minimum 2 replicas for stateless workloads in production namespaces.
- PodDisruptionBudgets for all critical workloads.
- Topology spread and anti-affinity to avoid single-node concentration.
- Horizontal Pod Autoscaler for traffic-sensitive services.
- Persistent volume sizing and class standards for stateful services.

## Terraform operating practice

- One environment folder per environment (`dev`, `stage`, `prod`).
- Shared module for baseline namespace controls and quotas.
- Pull requests require:
  - `terraform fmt -check`
  - `terraform validate`
  - Plan output review

## Continuous improvement loop

- Weekly platform review: incidents, capacity, policy exceptions.
- Monthly service template refresh based on team adoption feedback.
- Quarterly reliability game day and failure drills.
