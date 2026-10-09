---
name: local-experience
description: Retrieve a small, source-located lesson from an operator-maintained local experience manual when machine-specific history could change the current route. Historical notes never prove current state.
---

# Local Experience

Use only when Windows, browser bridges, deployment, documents, devices, or a recurring local failure could change the decision.

1. Run [scripts/search-experience.ps1](scripts/search-experience.ps1) with an exact `-Query` first; use `-Topic` only when the symptom is unknown.
2. Start with four matches and zero surrounding lines; widen context once only when a result is ambiguous.
3. Apply only entries that change the current decision, then live-verify ports, processes, services, browser registration, project files, or device identity.

Keep project state in its handoff, not the experience manual. Store only reusable, sanitized lessons; never copy secrets, raw logs, browser data, or personal information. For an existing browser session, use an approved browser-specific bridge.
