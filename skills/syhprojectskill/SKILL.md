---
name: syhprojectskill
description: Classify a confirmed project as coursework, commercial-small, special-large, or unknown, then select the smallest project context, validation depth, and specialist route that fit the current task without exposing secrets.
---

# SYH Project Routing

This is a router, not a project record or a technical playbook. It selects the working mode; `AGENTS.md` owns durable local rules, `HANDOFF.md` owns current verified state, and specialist Skills own task procedures.

## Route with minimum context

1. Confirm one project root or an explicit allowlist. Inspect only the smallest useful evidence: local instructions, profile/handoff if present, Git and manifest state, delivery boundary, and the current task.
2. Classify with evidence. Use `unknown` rather than inventing a business, risk, or ownership fact; ask one decisive question at a time when the answer would change the category, project boundary, acceptance bar, or authority to act.
3. Read exactly one category route and one primary task Skill. Add a supporting Skill only when a dependency, live risk, or acceptance boundary requires it.
4. For `special-large`, route to `large-project-ops`; do not embed work-package rules here. For phase continuity, route to `work-handoff`. For machine history, route to `local-experience` only when it could change the decision.
5. Create the compact project contract only after the root is confirmed. Preview [scripts/install-project-contract.ps1](scripts/install-project-contract.ps1) first; `-Apply` creates only missing files and never overwrites existing project instructions.

## Return a route record

- `category`: coursework | commercial-small | special-large | unknown
- `evidence`: only the files, commands, or user facts used
- `read_now`: smallest project and task context needed next
- `primary_route`: one Skill or direct workflow
- `supporting_route`: none unless specifically justified
- `acceptance`: minimum evidence needed before calling the task complete
- `next_action`: one safe step

## Ownership and loading contract

| Owner | Canonical content |
|---|---|
| project `AGENTS.md` / `PROJECT_PROFILE.md` | stable local constraints and routing metadata |
| `work-handoff` | verified current state, access route, blockers, next action |
| `large-project-ops` | project map, queue, decisions, work packages |
| `local-experience` | bounded historical machine lessons |
| primary specialist Skill | current task procedure and tool route |

Read [references/project-taxonomy.md](references/project-taxonomy.md) only to classify, [references/project-contract.md](references/project-contract.md) only to create or review project files, and [references/skill-routing.md](references/skill-routing.md) only for the chosen category/task row.
