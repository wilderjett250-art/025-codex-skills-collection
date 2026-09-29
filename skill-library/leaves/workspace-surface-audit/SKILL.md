---
name: workspace-surface-audit
description: Inspect local Skill, hook, plugin or tool coverage and recommend focused repairs to discovery, compatibility and context cost. Skill审查、路由检查、工具能力盘点。Read-only unless changes are requested.
metadata:
  origin: ECC
---
# Workspace capability audit
Inspect only the relevant metadata, entrypoints, callers and actual tool availability. Keep secret values out of output.
Separate available capabilities, misrouted or conflicting instructions, and missing integrations. Assess compatibility with this environment rather than preferring the originating framework.
For Skills, check concrete usefulness, trigger boundaries, duplicate responsibilities, progressive loading, actual dependencies and preservation of user scope. Size/popularity alone is not a quality score.
For matching, test near-miss negatives and paraphrased positives. A smaller candidate list does not prove better recall. Distinguish metadata search, Skill selection and downstream task quality.
Recommend a small affected set with evidence, migration/backup needs and measurable validation. Preserve old source and license/provenance when adapting or consolidating.
Do not scan credentials, install plugins, activate tools or launch delegated work merely to create an inventory.
