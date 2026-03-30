# PostgreSQL Managed Service Runbook

## Backup and restore

- Daily full backup plus 15-minute WAL archiving.
- Retention: 30 days in hot storage, 90 days in cold storage.
- Quarterly restore drill to non-production namespace.

## Upgrade strategy

- Patch upgrades: monthly in stage, then prod after 7-day soak.
- Major upgrades: blue/green migration with logical replication and rollback window.

## Capacity triggers

- CPU above 75% for 30 minutes: scale up instance resources.
- Storage above 80%: expand PVC and review table/index growth.
- Replication lag above 30 seconds: investigate IO, locks, and query pressure.

## Operational checks

- Confirm backups succeeded in last 24 hours.
- Confirm replication healthy and lag under threshold.
- Confirm pgbouncer/connection pools under saturation limits.
