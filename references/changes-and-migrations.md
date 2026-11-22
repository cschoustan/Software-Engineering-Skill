# API and Data Changes

For changes to public interfaces or persisted data, consider both old consumers using new deployments and new consumers using old deployments.

## Contract inventory

Record affected producers, consumers, schemas, routes, status codes, error shape, nullability, authorization, serialization, ordering, pagination, retry behavior, and version constraints where relevant.

## Phased migration

1. **Expand:** introduce compatible fields, endpoints, indexes, or schema structures without requiring all consumers to upgrade simultaneously.
2. **Migrate:** backfill or dual-read/write only when necessary. Use bounded batches, checkpoints, idempotent updates, and integrity comparisons. Include failure/timeout handling.
3. **Contract:** remove obsolete paths only after old clients, jobs, and persisted records no longer depend on them.

Do not assume that reverting the application reverses a database migration. Define separate restore, compensation, or repair procedures.

## Checks

- Test mixed-version compatibility as the deployment topology requires.
- Exercise unknown/missing fields, duplicates, retries, malformed inputs, denied access, and partial failures.
- Verify row counts, key invariants, constraints, indexes, and performance after backfill.
- State the rollback point and the action required if a migration is interrupted.
- Require explicit approval for destructive or irreversible operations.

Use [migration plan](../templates/migration-plan.md).
