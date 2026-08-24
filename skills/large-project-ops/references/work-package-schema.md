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

## Completion update

- Update queue:
- Update handoff:
- Result and remaining risk:
```

## Splitting test

Split a proposed package when any answer is unclear or has more than one independent answer:

- Does it change more than one module or external system?
- Does it require mutually unrelated Skills or tool routes?
- Does it have more than one acceptance environment?
- Would two agents need to edit the same files or perform ordered mutations?
- Can completion be stated in one sentence with one evidence set?

If the package only becomes small by omitting an integration or verification step, keep the missing step as a dependent package rather than calling the first package complete.
