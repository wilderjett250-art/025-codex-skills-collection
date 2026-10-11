# Bounded Windows UI observation

Applies only after choosing an authorized native desktop route. Prefer an app API/CLI for structured work. Desktop mouse/keyboard or foreground takeover still needs the user's explicit request; tool availability grants no authority.

- Identify the app instance/window/account once. Read the relevant UIA subtree with names, roles, AutomationId, enabled/selected/value state; do not dump every window, inspect passwords or expose private window text unnecessarily.
- Use stable accessible controls before coordinates. AutomationId and accessible Name are different properties; confirm the actual framework mapping. A numbered element ID from a snapshot is transient, not a stable test identifier.
- Windows-MCP's inspected revision supports `Snapshot(use_vision=False, use_ui_tree=True)` for text observation; `region=[left,top,right,bottom]` or `display=[0]` bounds capture. Check the installed schema: do not pass these fields to another tool merely because it has a similar name.
- Request a cropped screenshot for canvas/self-drawn controls, visual quality, ambiguous geometry or final visual evidence. Text trees do not prove color, alignment, pixel state or hidden content. Account for image downscaling, virtual-desktop origin and DPI before coordinate actions.
- After navigation, modal changes, scrolling, window movement or mutations, re-observe the affected region before relying on transient IDs/coordinates. Stable read-only state may be reused. Wait for an observable condition, not fixed sleeps; a missing UIA match does not prove the control is absent.
- Batch only independent safe reads. Keep a checkpoint before dependent actions or consequential writes. Check whether a timed-out write already succeeded before repeating it; preserve the real login/MFA/QR/CAPTCHA surface for the user.
- Verify the requested outcome in the relevant app, with visual evidence when appearance matters. A callable Snapshot or successful click does not prove task completion. Do not install/enable another MCP merely because this profile mentions it.

Adapted ideas, not copied API guarantees: [Windows-MCP Snapshot source](https://github.com/CursorTouch/Windows-MCP/blob/b74c507d9e709223a0904cf08019edf55f2a75bb/src/windows_mcp/tools/snapshot.py). No new server was activated by this profile.
