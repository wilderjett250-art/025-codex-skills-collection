# Large Project Control Documents

Use only the documents that are missing or needed for the current project. Preserve an existing canonical equivalent rather than creating parallel planning systems.

| Document | Owns | Must stay out |
|---|---|---|
| `AGENTS.md` | durable local constraints and module rules | daily status, copied specialist manuals |
| `PROJECT_PROFILE.md` | category, capabilities, risk, required acceptance | architecture and task diary |
| `PROJECT_MAP.md` | module boundaries, interfaces, ownership, external dependencies | changing task status and logs |
| `WORK_QUEUE.md` | package order, dependencies, state, current owner | implementation details duplicated from packages |
| `decisions/ADR-*.md` | a decision, alternatives, consequence, evidence | routine task notes |
| `work-packages/WP-*.md` | one agent-ready task contract and completion evidence | whole-project history |
| `HANDOFF.md` | verified current project state, remaining risks, next safe action | speculative plans presented as facts |

## Compactness targets

- Keep `PROJECT_PROFILE.md` to routing and acceptance metadata.
- Keep `PROJECT_MAP.md` to modules, interfaces, and links; it should be readable before an implementation task without source dumps.
- Keep `WORK_QUEUE.md` to active, blocked, and next packages. Move completed detail to the package and handoff.
- Create an ADR only when a future agent would otherwise reopen a consequential decision.
- Archive or summarize completed package detail after its facts have been incorporated into `HANDOFF.md`.

## Minimal project map

```markdown
# Project Map

## Modules

| Module | Paths | Responsibility | Interface / dependency | Validation owner |
|---|---|---|---|---|

## External systems

| System | Purpose | Boundary | Verification route |
|---|---|---|---|

## Active architectural constraints

-
```

## Minimal work queue

```markdown
# Work Queue

| Package | Status | Depends on | Owner | Acceptance evidence |
|---|---|---|---|---|

## Current package

-

## Blocked

-
```

Use a factual state flow: `draft` → `ready` → `in-progress` → `in-review` → `verified`, with `blocked` or `superseded` as explicit exits. Do not mark a package `verified` when only source code changed.
