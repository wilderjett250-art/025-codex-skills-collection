---
name: skill-library-router
description: 'Route each atomic intent in non-trivial local or compound work to a unique domain path and the best installed on-demand Skill.'
---

# Skill Library Router

Keep discovery cheap while making the user's taxonomy operational.

1. Reuse a `skillRoute` result already supplied by the `UserPromptSubmit` Hook for the current prompt; do not run the router again. If no result was supplied or it is clearly inconsistent with the prompt, query the user's full prompt. The result separates capability work units, access methods, and control Skills without loading Skill bodies:

   macOS/Linux:

   `node "${CODEX_HOME:-$HOME/.codex}/skill-library/scripts/route-task.mjs" --prompt "<current user request>" --limit 5`

   Windows PowerShell:

   `$codexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }; node "$codexRoot\skill-library\scripts\route-task.mjs" --prompt "<current user request>" --limit 5`

2. Treat every `workUnit` independently. Each must have exactly one owner and one canonical path: `plane/domain/discipline/family/skill`. A compound request may yield several work units; do not demote a second capability to generic support.
3. Use [domain-routing.md](references/domain-routing.md) only when the result needs a manual domain/discipline/family drill-down. Examples:

   `node "${CODEX_HOME:-$HOME/.codex}/skill-library/scripts/find-skills.mjs" --domain computing-digital --list-disciplines`

   `node "${CODEX_HOME:-$HOME/.codex}/skill-library/scripts/find-skills.mjs" --domain computing-digital --discipline frontend-ui --family implementation-parity --query "Vue screenshot"`

4. Read each required owner Skill's complete `SKILL.md`, then only the resources it routes to. Add its listed support only for a real dependency or gate. Never load a domain, discipline, family, or portfolio as instructions.
5. `accessSkills` describe how to reach the target, such as the user's existing Edge session. `controlSkills` govern routing, handoff, decomposition, or acceptance. Neither replaces a capability owner.
6. Prefer a runtime-provided system or plugin Skill when it directly owns the atomic work unit. Use the cold library for missing specialization; do not duplicate plugin Skills merely for indexing.
7. Project `AGENTS.md`, current user authority, and safety rules still govern execution. Rebuild or rematerialize the catalog after changing the library.

The index is at `~/.codex/skill-library/catalog.json`, business aliases at `routing-profile.json`, and complete cold Skills under `~/.codex/skill-library/leaves/`.
