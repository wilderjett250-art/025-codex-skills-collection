---
name: work-handoff
description: Create, audit, or resume the canonical project handoff when work changes phase, moves to another agent or computer, or needs safe server and current-state continuity. Keep it evidence-backed, compact, and free of credentials.
---

# Work Handoff

Maintain one canonical continuity artifact for the confirmed project, normally `HANDOFF.md` or an existing equivalent. It must let the next operator resume without rediscovering the project boundary, connection route, completed evidence, or already-known blockers.

## Minimal operating flow

1. Locate the existing handoff, status, release, and deployment records before creating another file. Confirm the project boundary.
2. Make only the observations needed for this handoff: working-tree and branch state, current implementation or runtime evidence, and the relevant deployment, console, or device route. Old notes are leads, not current proof.
3. Mark each material claim as `verified-current`, `historical`, `user-provided`, or `open`. Record an evidence cutoff time and set freshness to `current`, `stale`, or `blocked`.
4. Put a short resume card first: exactly what to read or run next, then the next safe action. Keep detailed proof as file paths, revisions, commands, or URLs rather than copying logs or architecture.
5. Describe connection routes reproducibly but never include passwords, private keys, tokens, cookies, session values, or secret URLs. Record only non-secret identifiers, expected credential location or variable name, and manual gates.
6. After approved work changes the state, update the same canonical handoff. Do not leave completed work in its next-actions list.

## Boundaries

- If a missing fact would change the project boundary, connection target, ownership, or next external action, ask one concise question before writing it as fact. Leave non-blocking unknowns explicitly `open` rather than delaying the whole handoff.
- Distinguish local validation, remote deployment, and real user or device acceptance.
- A next action is context, not permission to mutate external systems. Preserve login, MFA, CAPTCHA, payment, publication, permission, deletion, and irreversible confirmation as explicit gates.
- For a small task, update the compact current-state section instead of creating an elaborate project diary.

Read [references/handoff-schema.md](references/handoff-schema.md) only when creating, normalizing, or auditing the document structure.
