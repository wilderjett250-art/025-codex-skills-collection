---
name: architecture-decisions
description: Choose or review application architecture, technical completeness, module/data boundaries and ADRs against real constraints. 架构评审、技术选型、模块耦合、过度设计、长期维护。Not project coordination or visual styling.
---
# Architecture decisions
Inspect the confirmed repository's current stack, deployment, data ownership and relevant constraints before suggesting replacements.
1. Identify the decision being made and its actual drivers: core journey, scale evidence, consistency, latency, availability, team capacity, budget, migration and operations. Mark estimates and unknowns.
2. Compare the current/simple option with one or two plausible alternatives. Give benefits, costs, failure modes and conditions that would change the recommendation. Avoid speculative microservices, queues or distributed databases.
3. Trace one representative request through client, API, service and persistence. Specify ownership, authentication/authorization boundaries, transaction or idempotency boundaries, retries and observable failure handling where relevant.
   Examine a failed request too: resource/timeout bounds, degraded behavior, observability and recovery. In a maintainability review, follow recent change hotspots and domain concepts; explain where coupling causes scattered edits or prevents meaningful tests. More layers or services do not prove a better architecture.
4. For a migration, account for compatibility, existing records, rollout, rollback and concurrency. A diagram alone is not a recoverable migration plan.
5. Write the smallest useful ADR in the project's existing decision location: context, options, selected option with reason, consequences, validation evidence, revisit trigger. Preserve user-chosen stacks and frameworks.
Validate the decision with an actual dependency/config/schema inspection or bounded spike when justified. Do not claim load capacity or runtime correctness from a document.
Use api-design only for detailed interface contracts and the actual framework owner for implementation. Component composition belongs to react-engineering; product value belongs to product-discovery.
