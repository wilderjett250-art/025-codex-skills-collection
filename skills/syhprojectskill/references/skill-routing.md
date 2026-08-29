# Skill Routing Matrix

This matrix is a routing aid, not a preload list. Use the project category to change execution and acceptance depth, then route every atomic capability to one owner with one canonical domain path.

## Always available as project context

Read only when present and in scope:

- project-root `AGENTS.md`;
- `PROJECT_PROFILE.md`;
- the relevant section of `HANDOFF.md`;
- the current task prompt and explicit user constraints.

These files are not substitutes for specialist Skills. They define the project boundary, current state, and acceptance contract.

## Coursework / assignment

| Current task signal | Primary route | Optional supporting route |
|---|---|---|
| implement or repair code | language/framework Skill or `coding-standards` | `tdd-workflow` when tests are part of the requirement |
| create or inspect a report/document | `documents` or `office-quality-gate` | `pdf` only when PDF handling is required |
| inspect an unfamiliar codebase | `agent-architecture-audit` | `code-tour` when a navigable tour is requested |

Do not load deployment, production-audit, cloud, or browser Skills unless the assignment explicitly requires them.

## Small commercial project

| Current task signal | Primary route | Optional supporting route |
|---|---|---|
| API or backend change | relevant backend/framework Skill | `api-design`, database Skill, or `security-awareness` only when the change touches them |
| deployment or release | `deployment-patterns` | `production-audit` or provider Skill only for the named target |
| account, browser, or customer-console action | `external-browser` when its MCP tools are registered; otherwise the configured browser-specific route | `security-awareness` when credentials, permissions, or suspicious content are involved |
| data/schema change | relevant database Skill | `database-migrations` when a migration is actually in scope |

Do not load all provider, database, and security Skills for a routine code edit.

## Special large project

| Current task signal | Primary route | Optional supporting route |
|---|---|---|
| project decomposition, work-package planning, or agent-ready MD control | `large-project-ops` | `work-handoff` for phase continuity; `agent-harness-construction` when the agent/tool/context system is being changed |
| architecture or boundary change | `agent-architecture-audit` | `large-project-ops` when the change must be split into agent-ready packages |
| long-running AI workflow or tool routing | `agent-harness-construction` | `agent-evaluation` for measurable regression checks; `large-project-ops` or `work-handoff` only when phase continuity is required |
| live deployment, operations, or acceptance | `production-audit` or `deployment-patterns` | provider, database, security, or `work-handoff` Skill only as required |
| ML training or shared GPU service | `mle-workflow` | `production-audit` when web-facing services are affected |
| hardware, device, or multi-system route | the relevant device/platform Skill | `work-handoff` and `production-audit` when external state is involved |
| documentation or release evidence | `office-quality-gate` or `work-handoff` | `pdf`, `documents`, or project-specific delivery Skill as needed |

Special-large does not mean every specialist is loaded. It means the baseline, checkpoint, evidence, and rollback requirements are stricter.

## Loading and stopping rules

1. Choose the category and build `project type + phase + surface/platform + risk` from current evidence.
2. Run the full-prompt lookup in `skill-library-router` before selecting custom Skills.
3. For each returned work unit, load its one owner Skill body. A compound task can have multiple owners only because it has multiple atomic work units.
4. Load a supporting, access, or control Skill only if the route identifies a real dependency, execution method, or claim boundary.
5. Stop loading after the tools, constraints, and acceptance checks are known. Never load a domain or family as a bundle.
6. After a phase completes, write a compact handoff update and discard stale phase-specific context where the host supports compaction.
7. If two Skills prescribe different tools or routes, do not combine them silently; select one route, explain the conflict, and ask for direction when it changes scope or risk.
