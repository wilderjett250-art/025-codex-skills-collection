---
name: large-project-ops
description: Run a confirmed special-large project with compact control documents and ready-to-execute work packages so each agent receives only its scope, dependencies, permissions, and acceptance evidence. Use for multi-service, hardware, ML, production-critical, legacy, or cross-team work; do not split ordinary repositories by default.
---

# Large Project Operations

Use this Skill after a project is classified as `special-large`, or when the user explicitly asks for agent-ready decomposition. Keep one canonical project boundary unless a module has its own build, release, ownership, data, and rollback boundary.

## Operating model

Do not solve context limits by cloning, copying, or physically splitting a repository into artificial mini-projects. Instead, keep a compact project control plane and create small **work packages** for agents.

```text
confirmed project root
├── AGENTS.md                 durable local constraints
├── PROJECT_PROFILE.md        category, capabilities, risks, acceptance
├── PROJECT_MAP.md            stable module and interface map
├── WORK_QUEUE.md             active package order and dependency state
├── HANDOFF.md                verified current state and phase continuity
├── decisions/                only decisions that constrain future work
└── work-packages/            one bounded task per agent or phase
    └── WP-<id>-<slug>.md
```

Read [references/control-documents.md](references/control-documents.md) when creating or auditing this control plane. Read [references/work-package-schema.md](references/work-package-schema.md) when preparing an agent-ready task.

## Minimal operating flow

1. Confirm root, owner, delivery boundary, and `special-large` evidence. Read existing instructions and handoff before creating a parallel control system.
2. Record a read-only baseline in the handoff. Create only the missing control documents required for the current phase: map for stable boundaries, queue for active order, decision for a durable tradeoff, and a package for an assigned outcome.
3. Make a package `ready` only when it has one acceptance boundary, a read set, a write set, dependencies, allowed mutations, approval gates, and focused evidence. Keep unresolved inputs as `draft` or `blocked`, not hidden inside a task; ask one decisive question at a time when an answer would change that contract.
4. Give an agent only the root/module instructions, relevant profile and handoff section, one map section, one ready package, linked decision, and one primary Skill. Add one supporting Skill only when it changes execution or acceptance.
5. Parallelize only when packages have no shared writes, mutable external state, ordered dependency, or conflicting acceptance environment. Otherwise express the dependency in the queue.
6. On completion, mark the package with evidence, update the queue and handoff, then discard prior exploration instead of passing an ever-growing conversation onward.

## Physical module boundaries

Create a separate repository, worktree, service, or independently deployed module only when it has a real boundary: separate build/test/release lifecycle, isolated data ownership, separately versioned interface, independent rollback, or an owner boundary. A long conversation, a large directory, or token pressure alone is not a reason to split code.

## Context rules

- Read the active package and its direct dependencies, not the entire queue, decision history, repository, manual, or knowledge-base result set.
- Keep one active package per agent task. It may contain dependent edits, but must end in one coherent acceptance decision.
- Link to source, decisions, and evidence instead of copying them. `HANDOFF.md` records current facts; packages record task contracts; neither replaces live verification.
