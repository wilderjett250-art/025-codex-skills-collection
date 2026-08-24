# Work Handoff Schema

Use this compact structure for a project-root `HANDOFF.md`, or adapt the existing canonical continuity record. Keep facts evidence-backed; redact all secret values.

```markdown
# Project Handoff

- Project / scope boundary:
- Repository / branch / environment:
- Freshness: current | stale | blocked
- Evidence cutoff: YYYY-MM-DD HH:mm TZ

## Resume card

- Read first: <up to three exact files, sections, or evidence links>
- Run or inspect first: <one focused command, page, or device check>
- Next safe action: <one action and its acceptance evidence>

## Connection route

- Console or service domain / project / region / resource label:
- SSH, API, or CLI shape: <non-secret alias, port, user, command shape>
- Credential location or variable names: <values omitted>
- Manual gates: login | MFA | CAPTCHA | approval | none

## Verified state

| Claim | Classification | Evidence | Verified at |
|---|---|---|---|
|  | verified-current |  |  |
|  | historical |  |  |

## Current risks and blockers

| State | Owner or input | What clears it | Do not do yet |
|---|---|---|---|
| open |  |  |  |

## Ordered next actions

| Priority | Action | Prerequisite | Acceptance evidence | Recovery / rollback |
|---|---|---|---|---|
| P0 |  |  |  |  |
```

Use classifications `verified-current`, `historical`, `user-provided`, and `open`. Record source change, local validation, remote deployment, and real user or device acceptance as separate claims. If old detail matters, link to a release note, ADR, issue, or dated report instead of extending this document into a diary.
