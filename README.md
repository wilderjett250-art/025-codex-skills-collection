# Codex Skills Collection

A compact, safety-conscious collection of reusable Skills for Codex-compatible agents. Each Skill is deliberately narrow: it loads only the context that changes the current decision and records evidence instead of copying sensitive or stale state into prompts.

## Included Skills

| Skill | Use it for | Key behavior |
|---|---|---|
| work-handoff | phase changes, agent or machine handoffs, deployment continuity | creates one concise evidence-backed HANDOFF.md |
| syhprojectskill | selecting a project operating mode | classifies coursework, small commercial, and special-large projects, then routes one primary procedure |
| large-project-ops | agent-ready decomposition of complex projects | uses a compact map, queue, decisions, and bounded work packages instead of copying a whole codebase into context |
| external-browser | tasks in an already logged-in Chrome or Edge session | requires an external-browser MCP and uses DOM references, not coordinates, screenshots, cookies, or passwords |
| local-experience | recurring machine-specific lessons | searches an operator-owned, sanitized manual in a bounded way and live-verifies the result |

## Install one Skill

Copy the desired folder from skills into your agent's local Skills directory. For Codex on Windows, that is normally:

    C:\Users\<your-user>\.codex\skills\<skill-name>

Restart or reload the agent host if it does not discover the new folder automatically. Each Skill has its own SKILL.md entrypoint; read only the references it links when the task needs them.

The local-experience Skill intentionally ships without an experience manual. Set CODEX_EXPERIENCE_MANUAL_PATH to a sanitized manual you own, or pass -ManualPath to its search script.

## External browser requirement

external-browser is an instruction layer, not a browser driver. It requires a compatible MCP server that can operate the user's already-open browser and exposes compact state, observation, action, and verification tools. It must never export session data or silently launch an isolated browser.

## Security and publishing policy

- Do not add credentials, browser profiles, cookies, private keys, raw logs, private hostnames, customer data, or local runtime exports.
- Treat experience notes as historical leads, not proof of current state.
- Confirm the exact target before external mutations such as deployment, publication, permissions, deletion, or billing actions.
- Review a contribution for sensitive material before it enters Git history.

## Contributing

See CONTRIBUTING.md. By contributing, you agree that your submission can be distributed under the MIT License.
