# Work Package Schema

Create one file at `work-packages/WP-<id>-<slug>.md` per coherent agent task. Keep it short enough to load with the relevant source files.

```markdown
# WP-<id>: <outcome>

- Status: draft | ready | in-progress | in-review | verified | blocked | superseded
- Owner:
- Created:
- Last verified:
- Depends on:
- Blocks:
- Integration owner / shared contract version:

## Goal

-

## Non-goals

-

## Scope

- Read set (paths, modules, or live routes):
- Write set (paths or approved external targets):
- Out of scope:

## Current evidence

- Source, command, page, runtime, or handoff reference:

## Required context

- Project or module instructions:
- Project-map section:
- Linked decision or handoff section:
- Primary Skill:
- Supporting Skills, only if needed:

## Plan

1.

## Mutation and approval boundary

- Allowed local changes:
- Requires confirmation before:

## Acceptance evidence

- Focused command, test, page, device, or artifact:
- Expected result:
- Cross-component acceptance / rollback boundary, when relevant:

## Completion update

- Update queue:
- Update handoff:
- Result and remaining risk:
```

## Splitting test

Split by independent outcome, conflicting writes or a real delivery boundary, not file count. One vertical slice may legitimately touch several modules. Resolve:

- Can outcomes be verified and rolled back independently?
- Are separate Skills or tool routes needed now, or only in a future phase?
- Who verifies the integration if checks span environments?
- Would two agents share writes or perform ordered mutations? Assign one writer or explicit sequencing rather than pretending the tasks are parallel.
- Can completion be stated in one sentence with one evidence set?

If the package only becomes small by omitting an integration or verification step, keep the missing step as a dependent package rather than calling the first package complete.
