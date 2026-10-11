---
name: large-project-ops
description: Coordinate large or legacy projects through dependency-aware milestones, bounded agent work packages and integration acceptance. 大项目、跨端协作、里程碑、任务拆分。Use for real cross-system complexity, not every feature.
---

# Large Project Operations

Use only after special-large evidence exists or when the user explicitly asks for agent-ready decomposition. Keep one real project boundary; token pressure alone is not a reason to split code or repositories.

1. Confirm root, owner, delivery boundary, current instructions, and handoff.
2. Create only the missing control records for this phase: profile, map, queue, durable decision, or one work package. Preserve an existing canonical equivalent.
   Order packages by dependencies and the riskiest unresolved assumption. Prefer an early executable vertical slice across client, service and data over completing each layer in isolation. Track the integration owner, contract/version and rollback boundary at shared seams.
3. Make a package ready only when it has one outcome, read/write sets, dependencies, allowed mutations, approval gates, and acceptance evidence. Leave unresolved material inputs `draft` or `blocked`.
4. Give an agent its active package, direct dependencies, relevant project records, one owner Skill, and only the capability modules that change its work. Multiple modules are allowed when individually justified.
5. Parallelize only with no shared writes, ordered external mutation, or conflicting acceptance environment. On completion, record evidence in the package, queue, and handoff.
   Parallel agents are optional. Each gets a bounded context packet, not the full project history. Verify the combined result in its acceptance environment; component checks alone do not close the milestone. Resume from current state rather than recreating the plan after compaction.

Read only the active package and direct dependencies, not the whole repository or planning history. Create a separate module only for a separate build, release, ownership, data, interface, or rollback boundary.

Read [references/control-documents.md](references/control-documents.md) for control records and [references/work-package-schema.md](references/work-package-schema.md) for a task contract.
