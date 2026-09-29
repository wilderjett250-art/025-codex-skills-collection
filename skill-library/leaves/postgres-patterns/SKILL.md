---
name: postgres-patterns
description: Design and diagnose PostgreSQL queries, indexes, schemas, connection pools, locking and row-level security. PostgreSQL慢查询、索引、连接池、锁、行级权限。Not MySQL or automatic database changes.
metadata:
  origin: ECC adapted with pinned Supabase references
---
# PostgreSQL decisions
Inspect PostgreSQL version, actual schema, representative query and application access path. Identify whether the issue is query planning, connections, locks or authorization before changing anything.
Select individual rules beneath references/curation-20260908/supabase-postgres-best-practices/references/: query-, conn-, schema-, lock-, security-, data-, monitor-, advanced-. List filenames to choose the relevant rule; do not preload the compiled AGENTS.md or all categories.
Choose ID types, decimal precision, index order and connection limits from workload and constraints. No universal ban on UUIDs; no blanket ALTER SYSTEM or role changes. Supabase auth.uid() examples require Supabase; adapt to the actual identity system.
Start with read-only plans/statistics. EXPLAIN ANALYZE executes the query, including writes and functions, so use only an authorized isolated scope where execution is safe. Apply the established recovery gate to migrations and data changes.
Compare plans and actual outcomes after authorized changes; an added index is not proof of faster queries. Validate tenant isolation using appropriate distinct test identities.
