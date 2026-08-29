---
name: taste-skill
description: Apply a compact anti-generic visual-design critique to a web UI or redesign while preserving the incumbent product's useful strengths.
---

# Frontend Design Taste — Compact Branch

Use this after `frontend-design` when the task needs deeper calibration, not as a replacement for the brief or project design system.

## Three design dials

Choose each dial deliberately and state the choice in the design plan:

1. **Density** — sparse/editorial, balanced/productive, or dense/operational.
2. **Expression** — quiet/systematic, branded/characterful, or bold/experimental.
3. **Structure** — free composition, modular grid, or strict application shell.

Do not let all three drift to the usual AI defaults. A bold visual surface can still use a disciplined grid; a dense dashboard can still have one memorable branded element.

## Redesign preservation

Before changing an existing product, identify:

- components and interaction patterns users already understand;
- tokens, typography, spacing, and navigation that are internally consistent;
- distinctive brand cues worth retaining;
- actual usability or hierarchy failures that justify change.

Preserve strengths unless the user explicitly asks for a new identity. A redesign is not permission to erase functional information density, established workflows, or accessibility behavior.

## Anti-generic review

Challenge elements that could be pasted into an unrelated product without anyone noticing:

- default gradient hero, glass cards, decorative blobs, arbitrary glow, or excessive rounded cards;
- generic feature-card grids with identical hierarchy;
- decorative numbering that does not encode a sequence;
- stock dashboard metrics that are not tied to a real decision;
- repeated animation that adds motion but not meaning;
- placeholder copy that describes implementation instead of the user's task.

Replace generic choices with details derived from the subject: its artifacts, vocabulary, data, workflow, constraints, and audience.

## Focused preflight

Check only what materially applies:

- the first viewport communicates the product and primary action;
- layout survives narrow mobile and wide desktop widths;
- CTA hierarchy is unambiguous;
- keyboard focus is visible and motion respects reduced-motion preferences;
- contrast, text size, and hit areas remain usable;
- redesign does not remove important content or states;
- loading, empty, error, disabled, hover, focus, and success states are intentional;
- screenshots confirm the implemented hierarchy rather than only the source code.

## Output

Return a short calibration note:

- selected design dials;
- strengths being preserved;
- generic tendencies being removed;
- one signature choice tied to the subject;
- the most important responsive or accessibility risk.

For historical edge cases or the original exhaustive rubric, read [references/full-legacy.md](references/full-legacy.md) only when the user explicitly requests a comprehensive taste audit. Do not load it for normal design work.
