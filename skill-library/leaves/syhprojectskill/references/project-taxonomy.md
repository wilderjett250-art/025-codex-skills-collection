# SYH Project Taxonomy

Use this reference after the project root is confirmed. Classification is a working mode, not a permanent label; update it when the project scope, owner, risk, or deployment boundary changes.

## Evidence matrix

| Category | Positive evidence | Required caution | Default acceptance |
|---|---|---|---|
| `coursework` | assignment brief, rubric, class repository, fixed algorithm/stack, submission artifact | preserve the required route; avoid adding production scope or changing the teaching objective | reproducible local run plus requested artifact checks |
| `commercial-small` | customer-facing route, business data, login/payment/admin path, deployed service, customer acceptance | protect secrets and data; check compatibility, rollback, health, and release boundary | focused tests plus the real remote route or release check |
| `special-large` | multiple services, hardware/device path, ML training, legacy constraints, regulated or production-critical behavior, cross-team ownership | baseline first; use staged changes, architecture records, handoff, and rollback evidence | subsystem validation plus integrated/live evidence where authorized |
| `unknown` | evidence conflicts, project root unclear, or ownership/risk is not established | stop before risky edits and ask for the smallest missing fact | classification confirmation |

## Profile record

For a confirmed project, create or update `PROJECT_PROFILE.md` at the project root only when that file is in scope:

```markdown
# Project Profile

- Project:
- Root:
- Category: coursework | commercial-small | special-large | unknown
- Category verified: YYYY-MM-DD HH:mm TZ
- Owner or responsible party:
- Repository and branch:
- Environment:
- Deployment or submission target:
- Data/device boundary:
- Required technology or algorithm route:
- Risk level: low | medium | high
- Required validation:
- Required handoff artifact:
- Out-of-scope systems:

## Evidence

- Files or documents inspected:
- Commands or runtime checks:
- User-provided facts:
- Open classification questions:

## Operating rules

-

## Next review trigger

- Reclassify when:
```

Never fill credential values into the profile. Refer to approved local credential stores, environment-file paths, secret-variable names, or user-controlled login steps without copying their contents.

## Portfolio inventory

When the user explicitly requests classification of multiple projects:

1. Establish an allowlist of roots and exclude dependency, cache, browser-profile, build, and temporary folders.
2. Collect compact metadata first: root, Git presence, README/instruction files, manifest, deployment markers, recent activity, and likely category signals.
3. Return a table with category, confidence, evidence, risk, and next review action.
4. Do not open every source file or historical log until a specific project is selected for takeover.
5. Keep the portfolio catalog outside individual project roots only when the user confirms its location and ownership.
