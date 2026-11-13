---
name: slides
description: "Compatibility name for general editable PowerPoint decks, source assets and slide layout; use the current primary plugin, with a local fallback only for an explicit stack or actual runtime limitation."
---

# Slides compatibility entry

For a general request, use the currently available `presentations:Presentations` skill and its own runtime/template routing. This old name remains available for compatibility; it does not impose a competing authoring engine.

Use [pptxgenjs-slides](../pptxgenjs-slides/SKILL.md) only when the user explicitly chooses that local stack or the primary runtime cannot perform the actual task. Resolve the capability from current session metadata; a missing catalog row is not proof a plugin is unavailable.

Preserve the user's editable PowerPoint decks, source assets and slide layout. Keep the source, required calculations and meaningful rendering/verification checks. Do not load both complete implementations for one work unit or install a new runtime simply to satisfy an old example. All original scripts, assets and full pre-change instructions remain preserved.
