# Touch & Interaction

Source: vercel-labs/web-interface-guidelines @ e3d624baaf29dc1fc645aff3e38f03e564d2d6b1, command.md.
Apply only to the requested surface; preserve native semantics.

- `touch-action: manipulation` (prevents double-tap zoom delay)
- `-webkit-tap-highlight-color` set intentionally
- `overscroll-behavior: contain` in modals/drawers/sheets
- During drag: disable text selection, `inert` on dragged elements
- Drag/swipe/pinch/path gestures need tap/click and keyboard alternatives unless essential
- `autoFocus` sparingly—desktop only, single primary input; avoid on mobile
