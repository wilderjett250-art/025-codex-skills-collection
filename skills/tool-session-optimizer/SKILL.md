---
name: tool-session-optimizer
description: Choose the shortest authorized route across connected APIs/MCP, official CLIs, authenticated browser sessions, and native desktop apps. Use when login state, human confirmation, GUI/CLI pairing, or competing tool paths could cause needless reauthentication, background waiting, or indirect workarounds. Do not replace the task's domain Skill.
metadata:
  role: access-control
  inspirations: external-browser, agent-browser, Browser Use, Browserbase skills
---

# Tool Session Optimizer

Select the access path; leave domain execution to the task's primary Skill.

## Route

1. Preserve an explicit user route such as an existing Edge session, native app, SSH alias, or connected service.
2. Inspect current state once: availability, target, session/login, and whether user action is actually required.
3. Choose the shortest route that preserves state:
   - connected API/MCP for structured operations;
   - existing authenticated browser session for web UI;
   - official CLI for non-interactive work when its session is valid;
   - native app/page for login, account choice, permission, or confirmation.
4. Perform the task, then verify through the same causal route. Do not switch tools merely to obtain different-looking evidence.

## Human gate

- If authentication is valid, continue without asking the user to log in again.
- If a human gate is required, open the real native app/page at that gate and state the single action needed.
- Surface QR, MFA, CAPTCHA, password entry, or account choice only when the real interface requests it. Never export a QR/code to another app as a speculative shortcut.
- For paired GUI/CLI tools, the GUI owns login and confirmation; resume CLI automation only after directly confirming the required state.
- Do not leave an invisible/background command waiting for user action when a visible confirmation surface exists.

## Context discipline

- Keep only: chosen route, target, observed session state, current gate, and next action.
- Load one relevant tool profile or specialist Skill, not a portfolio of tool manuals.
- Reuse valid references and observations until navigation, session, or target state changes.
- On failure, diagnose the current route before installing another tool or opening an alternate app.

Read [references/route-patterns.md](references/route-patterns.md) only when more than one access route is plausible or authentication behavior is ambiguous.
