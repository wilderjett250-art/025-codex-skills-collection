---
name: windows-desktop-e2e
description: Write or diagnose E2E tests for native Windows WPF, WinForms, Win32/MFC or Qt apps using pywinauto/UI Automation; inspect actual controls and isolate test data.
metadata:
  origin: ECC
---
# Native Windows E2E tests

Own the app's native GUI test outcome, not arbitrary desktop operation. Use browser tools for HTML/WebView2/Electron content, platform tools for mobile and ordinary tests when no GUI is needed. Inspect the real framework, build, process/window and test target before choosing locators.

- Verify an authorized target and isolated synthetic data. Environment redirection alone is not filesystem/network security isolation. Physical input/focus takeover still requires the user's explicit request; never run sample login/destructive tests against a real account.
- Prefer observed AutomationId, then accessible Name/control type, before coordinates. Name and AutomationId differ: do not assume an AccessibleName assignment creates an AutomationId. Check actual UIA properties rather than a generic framework table.
- Inspect only the relevant subtree without screenshots when text/control state suffices. Re-observe transient element IDs after navigation/dialog/scroll/layout changes. Use a bounded screenshot for self-drawn controls, visual assertions or geometry; account for DPI/downscaling/virtual-desktop coordinates.
- Wait for observable readiness/result, not fixed sleeps. Preserve business results on retry; classify stale state, app failure, inaccessible controls and a human-only gate separately.
- Test the requested user action and state/content outcome, not pixel coordinates or merely a successful click. Use failure evidence by default; enable per-step tracing only for a specific repro, redact text and bound retained artifacts.
- The preserved reference examples are starting points, not verified code for this app or current CI. Check platform availability, cleanup/handle lifetimes and containment claims before use. Never infer that hosted CI has an interactive desktop or that Job Objects isolate file/network access.

Read only the matching detail:
- UIA inspection/dependencies/framework identifiers: [uia-foundations](references/uia-foundations.md).
- Building fixtures/page objects/waits or diagnosing flakiness: [test-harness](references/test-harness.md).
- Test data/process isolation or CI: [isolation-ci](references/isolation-ci.md).
- Qt-specific widgets/accessibility: [Qt](references/qt.md).
- Screenshot fallback, DPI, recording or opt-in tracing: [screenshots/tracing](references/screenshots-tracing.md).
- Original scope/source context if needed: [preserved scope](references/source-scope.md).

All original guide bytes are retained across the references; `references/source-layout.json` records reconstruction offsets and the original hash. The shared bounded-observation strategy is adapted from [Windows-MCP](https://github.com/CursorTouch/Windows-MCP). This Skill does not install or activate that MCP.
