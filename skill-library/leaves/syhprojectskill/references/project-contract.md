# Common Project Contract

Use this reference when creating or reviewing the project layer. The goal is a predictable, low-context entry point for any Codex operator without flattening every project's differences.

## Contract layout

```text
project-root/
├── AGENTS.md              # stable common contract plus local hard rules
├── PROJECT_PROFILE.md     # compact routing and acceptance metadata
├── HANDOFF.md             # current verified state and next action
└── module/AGENTS.md       # only where a module has a genuinely different rule
```

Keep each responsibility separate:

| Layer | Answers | Must not contain |
|---|---|---|
| `AGENTS.md` | What is always required while working here? | Daily status, copied Skill manuals, credentials |
| `PROJECT_PROFILE.md` | What kind of project is this, and what route is likely relevant? | Full architecture or logs |
| `HANDOFF.md` | What is true now, what proves it, and what happens next? | Unverified claims or secret values |
| Specialist Skill | How should this particular task be performed? | Project-specific state unless the task requires it |

## AGENTS.md common kernel

Use this compact block for a new project. It may be appended as a clearly labelled section to an existing `AGENTS.md` only after reviewing the existing instructions for conflicts.

```markdown
# Project Operating Contract

## Scope and sources

- Treat this root as the project boundary unless the user confirms another boundary.
- Read the applicable root or module `AGENTS.md`, compact `PROJECT_PROFILE.md`, and only the relevant `HANDOFF.md` section before non-trivial work.
- Prefer current source, runtime, command output, and user-provided artifacts over old notes.

## Changes and evidence

- Inspect the current implementation and Git state before changing existing work.
- Preserve unrelated files and user changes. Make the smallest change that satisfies the confirmed task.
- Run the smallest relevant validation, and distinguish local, remote, and real-user acceptance.

## Safety and continuity

- Never copy, expose, or commit passwords, tokens, cookies, private keys, or secret values.
- Confirm exact target and scope before irreversible, external, permission, deployment, publication, or deletion actions.
- At meaningful handoff points, update `HANDOFF.md` with verified state, evidence, risks, and the next safe action.

## Project-specific rules

- Record only stable constraints that change normal task decisions.
```

This common block is intentionally not a copy of global operating instructions. It makes the project self-describing when the routing skill is unavailable, while the detailed methodology remains lazy-loaded in Skills.

## PROJECT_PROFILE.md schema

Keep the profile short enough to read before every material task. Use only confirmed values; `unknown` is a valid value.

```markdown
# Project Profile

- Project:
- Root:
- Category: coursework | commercial-small | special-large | unknown
- Capability tags: web | api | database | deployment | browser-console | document | ml | hardware | desktop | unknown
- Risk level: low | medium | high
- Repository and branch:
- Runtime or submission target:
- Data or device boundary:
- Required technology or algorithm route:
- Required validation:
- Required handoff artifact:
- Out-of-scope systems:
- Profile verified: YYYY-MM-DD HH:mm TZ

## Evidence

- Confirmed sources:
- Open classification questions:

## Skill routing hints

- Prefer:
- Escalate to:
- Avoid unless the task requires it:
```

`Capability tags` are selectors, not a preload list. For example, `web`, `api`, and `database` lets a current task choose a framework Skill plus a database Skill only if the request touches data. It does not load three Skills just because the project has three tags.

## HANDOFF.md contract

Use factual, time-bound statements. Keep a compact current-state summary at the top; move obsolete detail out rather than making future agents read an endless timeline.

```markdown
# Handoff

## Current state

- Verified at:
- Completed:
- Current behavior or deployment state:
- Uncommitted or unpushed work:

## Evidence

- Files and revisions:
- Commands, tests, or live checks:
- External confirmations:

## Risks and boundaries

- Not verified:
- Required user input or authorization:
- Rollback or recovery reference:

## Next safe action

- Action:
- Acceptance evidence:
```

## Read order and lazy routing

1. Read the root contract and relevant module contract, if present.
2. Read the profile for category, risk, capability tags, and acceptance target.
3. Read only the handoff section relevant to the task phase.
4. Select one primary specialist Skill from the task intent. Add one supporting Skill only when a live risk, dependency, or distinct acceptance boundary requires it.
5. Read source, logs, or decision records immediately before they affect a decision.
6. At a phase boundary, compact verified facts into the handoff rather than retaining prior exploratory context.

## Module contracts

Create a nested `AGENTS.md` only when a subdirectory has a durable rule that conflicts with or materially sharpens the root contract, such as a separate deployment path, regulated data boundary, generated-code rule, or hardware procedure. Do not create one merely to restate the root contract.
