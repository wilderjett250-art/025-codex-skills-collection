---
name: backend-patterns
description: Implement Node.js, Express or Next.js server-side validation, service boundaries, transactions, caching and background work. 后端业务逻辑、接口校验、事务与幂等。Use framework-specific Skills for other stacks.
metadata:
  origin: ECC
---
# Backend implementation
Trace the affected route through authorization, validation, business operation and persistence. Preserve API compatibility and the project's framework.
- Authorize the operation on the actual resource; validate input at trust boundaries and avoid leaking internal or secret fields in responses/logs.
- Define transaction ownership and idempotency before adding retries or multi-write operations. Protect concurrent legitimate updates.
- Inspect query shape and indexes before caching; define invalidation and consistency if a cache is warranted.
- For a slow endpoint, measure the request path and query count/plan before changing it. Check avoidable round trips, N+1 queries, unbounded reads, connection lifetimes and blocking work. Bound pagination, concurrency and timeouts without dropping required authorization, validation or consistency. Compare with the same workload; do not promise throughput from code inspection.
- Jobs need retry boundaries, deduplication and observable failure. Do not turn small synchronous operations into background systems without a reason.
- Verify business invariants with isolated data and meaningful integration checks. Production write tests require the existing authorization/backup gate.
Read [pattern examples](references/pattern-examples.md) only for a relevant implementation pattern; it is a legacy reference, not a requirement to adopt its sample stack.
Use api-design for a new public contract and architecture-decisions for broader system tradeoffs. Do not load their full instructions for an ordinary endpoint fix.
