# Elasticsearch Managed Service Runbook

## Backup and restore

- Snapshot policy every 6 hours to object storage.
- Retention: 14 days quick restore, 60 days archive.
- Monthly restore verification in stage cluster.

## Upgrade strategy

- Rolling minor upgrades with shard allocation awareness.
- Major upgrades use parallel cluster migration and index reindex strategy.

## Capacity triggers

- JVM pressure above 75% sustained: scale data nodes or tune shard allocation.
- Disk usage above 75%: add storage capacity and rebalance shards.
- Search latency p95 above SLO: evaluate hot shards and query profiles.

## Operational checks

- Cluster health is green.
- No unassigned shards.
- Snapshot completion within expected window.
