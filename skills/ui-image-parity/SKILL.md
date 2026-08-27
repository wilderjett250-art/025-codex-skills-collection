---
name: ui-image-parity
description: Rebuild and refine a web UI from a supplied screenshot, mockup, Figma export, or authorized live reference by comparing real captures at the same viewport until no obvious mismatch remains.
---

# UI Image Parity

Use for a user-supplied visual target. It is a fidelity workflow, not an invitation to invent a new design.

1. Confirm the target route/state and reference dimensions; use the newest reference as visible source of truth. Inspect the smallest useful project baseline and preserve its stack.
2. Make a short visual ledger for major geometry, typography, surfaces, repeated components, assets, and visible unknowns. Match shell before micro-spacing.
3. Capture the real implementation at the same CSS viewport, theme, and scroll position. Do not use CSS zoom, transforms, or browser chrome to fake parity.
4. Inspect reference and capture; write the ordered mismatch list before editing: state/geometry, text metrics, surfaces, assets, then micro-spacing. Fix, recapture, and repeat.
5. Add focused crops for dense or fragile controls, tables, cards, charts, and repeated rows. Completion requires actual captures inspected in the current task, not only build or lint success.

Keep a compact manifest and real evidence in the confirmed project. Retain the reference, manifest, final evidence, and only the latest three verified generated candidate captures per route-and-viewport family; move confirmed obsolete iterations to the Recycle Bin.

Use this as the owner Skill for screenshot matching. Add `ui-ux-pro-max` only for a separately requested accessibility, responsive, or design-system check after reference-size parity; it must not override the reference.

Read [references/visual-review.md](references/visual-review.md) only for the ledger, evidence manifest, focused-crop triggers, or cleanup boundary.
