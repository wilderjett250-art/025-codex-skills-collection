---
name: syhprojectskill
description: 'Classify a confirmed project as coursework, commercial-small, special-large, or unknown, then emit a compact fingerprint for execution, Skill routing, validation depth, and handoff.'
---

# SYH Project Routing

This is a router, not a project record or a universal checklist.

1. Confirm one project root or allowlist; inspect only local instructions, current state, delivery boundary, and task evidence.
2. Classify as `coursework`, `commercial-small`, `special-large`, or `unknown`. Use `unknown` and ask one decisive question when category, authority, or acceptance would otherwise be guessed.
3. Build a compact fingerprint: `project type + lifecycle phase + primary surface/platform + acceptance/risk`. Do not turn these labels into extra instruction bodies.
4. Pass the full prompt to `skill-library-router` for custom Skill routing. Name exactly one owner for each returned atomic work unit; a compound request may have several work units. Keep access methods and control gates separate, and do not guess from one English keyword.
5. Route reported UI/API/device behavior or a delivery/release claim to `evidence-based-acceptance`; route special-large decomposition to `large-project-ops`, phase continuity to `work-handoff`, and machine-specific history to `local-experience` only when each is relevant.
6. Create a compact project contract only after the root is confirmed; the installer previews by default and never overwrites existing instructions.

Return: category, task fingerprint, evidence, atomic work units with one owner each, access/control dependencies, minimum acceptance evidence, and one next safe action.

Read [references/project-taxonomy.md](references/project-taxonomy.md) only to classify, [references/project-contract.md](references/project-contract.md) only to create or review project files, and [references/skill-routing.md](references/skill-routing.md) only for the selected task route.
