---
name: "playwright"
description: "Use an authorized Playwright CLI browser workflow for extraction, form interaction or UI debugging; an existing authenticated browser keeps its supported bridge and profile."
---

# Playwright CLI

Use this local CLI route for an authorized browser automation/debugging task when it fits the selected browser/session. Prefer an already-available official browser capability if it directly owns the task. Preserve any explicitly requested tool route.

- For an explicitly requested persistent session, read [playwright-interactive](../playwright-interactive/SKILL.md).
- Existing authenticated Edge/Chrome sessions require their supported external-browser bridge; do not substitute a new Playwright profile or isolated browser silently.

## Local CLI route
Resolve `scripts/playwright_cli.sh` from this SKILL.md's actual directory, rather than assuming it lives in `<home>/skills/playwright`. Inspect its options before use. It requires a supported Bash and Node/npm; on Windows verify the actual executables instead of running POSIX preflight in PowerShell.

Use the existing installed toolchain. Do not auto-initialize a user's package, install globally, change sandbox policy or launch a different browser solely to meet this recipe. Resolve a genuinely missing prerequisite within the authorized project or report it precisely.

The wrapper's normal sequence is `open <url>`, `snapshot`, then actions such as `click <returned-ref>`, `type <text>`, or `press <key>`. Use only observed element references, refresh stale references after navigation, and verify the action's real result. Check possibly completed submissions before retrying.

Keep task screenshots and output on the permitted artifact drive. Use screenshots for meaningful visual checks; retain compact observations when they remain valid. Tool credentials/storage are not exported to bridge sessions.
