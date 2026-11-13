---
name: skill-scout
description: Search existing local, marketplace, GitHub, and web skill sources before creating a new skill. Use when the user wants to create, build, fork, or find a skill for a workflow.
metadata:
  origin: community
---

# Find an existing skill before building one

Use the actual task, object and platform to avoid inventing a duplicate capability.

1. Inspect already-available system, plugin and active personal skill descriptions. If a matching specialist is available, use it without installing a second copy.
2. In this Codex library, search once through the actual home-relative `skill-library/scripts/find-skills.mjs --query "task + object + platform"`. It reads metadata; choose by scope and load only the selected owner. Do not treat an empty `~/.claude/skills` directory as absence of Codex skills.
3. For an explicitly selected Claude/other host, inspect that host's documented skill locations instead. Do not write one host's config into another host to create apparent compatibility.
4. If local sources are insufficient or the user requests external discovery, search a bounded set of primary repositories/docs. Distinguish active tool compatibility, author claims and actual model/task evaluation. Inspect source, dependencies, license and current maintenance before recommending adoption.
5. Return the best relevant existing option or the precise missing capability. Installing, enabling hooks, adding services or creating a new skill requires that scope; discovery alone does not authorize it. If the user explicitly chooses creation from scratch, respect that choice.
