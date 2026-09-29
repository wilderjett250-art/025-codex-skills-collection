---
name: skill-library-router
description: Find task-relevant on-demand local Skills when no already-available Skill fits; search metadata, compare matches, and load only the selected specialist.
---
# Find the right Skill
Use the actual request, conversation, confirmed platform and all already-available Skill descriptions first. Routine work needs no extra Skill.
1. Match the capability to the user's real intent; examples, negation, quoted requirements and future phases do not authorize work.
2. If a specialist would materially help, regardless of task size, search once with task + object + platform using `skill-library/scripts/find-skills.mjs`. Reuse unchanged results rather than searching on every message.
3. Return at most three names/descriptions/paths and compare scope. For the selected current-stage catalog Skill, run `node <library>/scripts/read-skill.mjs <exact-catalog-name>` to load its entire SKILL.md and record a metadata-only local load event. If the helper is unavailable, read that SKILL.md directly and say the local load counter will miss it. Supporting references load only for a concrete need. A load event means instructions were delivered, not that the workflow was applied or counted by Codex's built-in activity page.
4. If search misses, rephrase once using a specific synonym or remove an unnecessary platform filter. If still unsuitable, proceed with available capabilities and state only a material gap; never treat no-match as proof that the capability does not exist.
5. Prefer a matching Skill already available in this session. Keep access methods and acceptance gates separate from domain ownership. A compound request can have several real work units, but do not preload their future phases.
   For a new app whose users/problem/MVP are still undecided, discover product-discovery first. Use interaction-design for flows and recovery; visual styling follows the established journey. Use architecture-decisions for consequential technical tradeoffs. Existing briefs or small fixes do not require repeating these stages.
6. Reuse a Skill body already present and unchanged in context; re-read only after relevant changes or loss of needed content. A disk cache does not prove the model still has its instructions.

Metadata search (resolve the actual Codex home; `CODEX_HOME` overrides the default):
    node <codex-home>/skill-library/scripts/find-skills.mjs --query "React render performance" --limit 3

Useful queries: 产品定位 MVP; 用户流程 表单体验; 架构 技术选型; React 组件性能; Node 接口校验; Playwright 端到端测试.
Add -Domain/-Discipline/-Family only when that filter is known; use listing switches for taxonomy browsing. Names in discovery-profile.json are curated retrieval hints, not a second instruction catalogue.
Metadata search uses search-skills.mjs. Optional explicit lexical lookup uses route-task.mjs and route-core.mjs. Rebuild catalog.json after Skill metadata/move changes. Validate lexical regression with route-task.test.mjs and independent retrieval cases with search-skills.test.mjs.

MCP is a separate access layer. Before relying on a configured MCP, verify its tool is callable in this task. `enabled = true` in config alone is not runtime proof; a session started before a config change may need a new task or app restart. Do not enable all dormant MCPs or assume the activity dashboard includes local Skill loads. The local report is `node <library>/scripts/activity-report.mjs --days 7`.
