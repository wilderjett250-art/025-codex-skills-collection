---
name: skill-library-router
description: 'Route non-trivial local or compound work to one owner Skill per atomic capability, using the local library only when runtime Skills do not already cover it.'
---

# Skill Library Router

Keep discovery cheap while making the user's taxonomy operational. Routine work needs no extra routing.

1. Match the user's actual request, confirmed platform, and current phase. Examples, negations, quoted requirements, and future phases do not authorize a separate work unit.
2. Reuse a `skillRoute` result already supplied by the `UserPromptSubmit` Hook for the current prompt; do not run the router again. If no result was supplied or it is clearly inconsistent with the prompt, query the user's full prompt. The result separates capability work units, access methods, and control Skills without loading Skill bodies:

   macOS/Linux:

   `node "${CODEX_HOME:-$HOME/.codex}/skill-library/scripts/route-task.mjs" --prompt "<current user request>" --limit 5`

   Windows PowerShell:

   `$codexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }; node "$codexRoot\skill-library\scripts\route-task.mjs" --prompt "<current user request>" --limit 5`

3. Treat every `workUnit` independently. Each must have exactly one owner and one canonical path: `plane/domain/discipline/family/skill`. A compound request may yield several work units; do not demote a second capability to generic support.
4. Prefer a matching runtime-provided system or plugin Skill when it directly owns a work unit. Use the local library only for missing specialization; do not duplicate plugin Skills merely for indexing.
5. If routing returns no suitable owner, rephrase the search once with a concrete synonym or remove an unnecessary platform filter. Return at most three candidates with their name, scope, and path. If it still misses, proceed with available capabilities and state only the material gap.
6. Use [domain-routing.md](references/domain-routing.md) only when the result needs a manual domain/discipline/family drill-down. Examples:

   `node "${CODEX_HOME:-$HOME/.codex}/skill-library/scripts/find-skills.mjs" --domain computing-digital --list-disciplines`

   `node "${CODEX_HOME:-$HOME/.codex}/skill-library/scripts/find-skills.mjs" --domain computing-digital --discipline frontend-ui --family implementation-parity --query "Vue screenshot"`

7. Read each required owner Skill's complete `SKILL.md`, then only the resources it routes to. Add listed support only for a real dependency or gate. Reuse an unchanged Skill body already in context; re-read only after a relevant change or loss of needed content.
8. `accessSkills` describe how to reach the target, such as the user's existing Edge session. `controlSkills` govern routing, handoff, decomposition, or acceptance. Neither replaces a capability owner.
9. Project `AGENTS.md`, current user authority, and safety rules still govern execution. Rebuild or rematerialize the catalog after changing the library.

The index is at `~/.codex/skill-library/catalog.json`, business aliases at `routing-profile.json`, and complete cold Skills under `~/.codex/skill-library/leaves/`.
