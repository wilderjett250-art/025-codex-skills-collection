---
name: local-experience
description: Retrieve a bounded, source-located lesson from an operator-maintained experience manual when local operations, browser bridges, deployment, documents, devices, or a recurring failure could change the task. Never treat historical notes as current state.
---

# Local Experience

Use this Skill only when machine-specific history could change the route. Prefer an exact symptom, tool, or error over a broad topic.

1. Configure a sanitized, operator-owned manual with the `CODEX_EXPERIENCE_MANUAL_PATH` environment variable, or pass its path to [scripts/search-experience.ps1](scripts/search-experience.ps1). Do not point to browser profiles, credential stores, private logs, or unreviewed exports.
2. Run the script with `-Query` first; use `-Topic` only when the exact symptom is unknown. Run `-ListTopics` only when neither is clear.
3. Start with its bounded default: four matches and no surrounding lines. Increase context once only when a returned line is ambiguous.
4. Apply only the entries that change the current decision, and live-verify dynamic facts such as ports, processes, services, browser registration, project files, or device identity.
5. Keep project state in that project's handoff. Add a lesson only when it is reusable, evidence-backed, and safe to store without secrets, raw logs, or personal data.

The manual is historical guidance, never proof that a current service, browser session, host, account, or device exists. Do not read or paste it wholesale. For an existing browser session, use an approved browser-specific bridge; never silently open an isolated browser or collect session data.

See `templates/experience-manual.example.md` for a safe starting structure.
