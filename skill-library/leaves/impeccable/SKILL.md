---
name: impeccable
description: Audit and refine an existing UI for layout, accessibility, UX copy, responsiveness and visual consistency. 现有界面打磨、排版对比度、无障碍审查。Preserve identity unless redesign is requested.
metadata:
  version: 4.0.3-local-curation
---
# Refine existing interfaces
Inspect the target and existing tokens/components first. Preserve product facts, user flows and identity within the request. Missing design documents do not make the product a blank canvas.
Load only the playbook for the actual problem:
- [Critique](reference/critique.md): diagnose usability/visual hierarchy.
- [Polish](reference/polish.md): final detail pass.
- [Layout](reference/layout.md) or [Typeset](reference/typeset.md): spacing or typography.
- [Audit](reference/audit.md): web accessibility/responsiveness; use reference/audit.native.md only for native UI.
- [Clarify](reference/clarify.md): labels and errors.
- [Harden](reference/harden.md): recovery and edge states.
- [Adapt](reference/adapt.md): device layouts.
- [Optimize](reference/optimize.md): measured UI performance.
For a specifically requested additional command, locate its matching reference filename. Do not show a command menu or load every playbook for an ordinary refinement.
For concrete optical corrections only, add reference/micro-polish.md. For a standards review, select the matching topic under references/curation-20260908/web-topics/. These are pinned Vercel rules; adapt native keyboard semantics correctly rather than duplicating handlers on native buttons.
Upstream setup scripts, craft-floor blanket bans, document creation, detector hooks, pinning and doctor repair are optional tools, not prerequisites. Never enable hooks automatically. Existing user intent and project conventions override aesthetic bans and fixed iteration ceilings.
Compare real captures at appropriate viewports and verify affected interactions. Fix observed defects and recheck the changed scope; stop when the requested outcome is evidenced. A model critique score is not user research.
