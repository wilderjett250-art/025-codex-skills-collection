---
name: ui-ux-pro-max
description: Query the local UI/UX reference database for palette, typography, accessibility, chart or platform guidance. 配色、字体搭配、无障碍、图表选型。Reference lookup, not the default UI builder.
---
# UI/UX reference lookup
Resolve scripts/search.py from this Skill's actual directory. Invoke it with the available Python executable and the specific query/domain; use --help for options. Do not rely on CLAUDE_PLUGIN_ROOT or a hardcoded project-relative path.
- Palette/type/style uncertainty: query color, typography or style.
- Forms, navigation, touch, feedback and accessibility: query ux.
- Charts: query chart against the actual data and decision.
- Framework-specific guidance: pass the repository's actual stack.
Return only the few relevant results and their rationale. Database suggestions are references, not proof that a design suits this user's task.
Use --design-system only when a new system or a comparison is requested/needed. A new page in an existing product should reuse its established tokens/components. Persistence is optional; inspect existing files, back them up, and specify the project output directory before writes.
If no useful result exists, broaden or rephrase once; do not invent database matches. Read references/quick-reference.md or references/pro-rules.md only for the relevant detail.
Keep the selected visual/interaction owner in charge. Do not load the entire style catalogue or impose a universal palette, spacing value, font, animation duration or coverage checklist.
