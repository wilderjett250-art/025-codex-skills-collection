---
name: external-browser
description: Operate a task in the user's already-open Chrome or Edge through the external-browser MCP, reusing its authenticated session with compact DOM references instead of coordinates, screenshots, or credentials.
---

# External Browser

Use only when the external-browser MCP tools are registered and connected; an enabled extension alone is not enough.

1. Call `browser_status` once at task start and only again after a connection, navigation, or reference failure.
2. Select a tab only when necessary, then take one compact observation. Reuse its valid references; if state is unchanged, do not observe again.
3. Act only through returned references. Use post-action state first and run focused verification only when the outcome needs proof.
4. Treat a timeout on submit, publish, delete, permission, or payment as possibly complete: verify before any retry.

- Reuse the existing session without reading or exporting passwords, cookies, storage, tokens, keys, or password-field values.
- Ask one concise question when account, tab, target, submitted value, or consequence is materially ambiguous.
- Pause for CAPTCHA, MFA, browser permission, account choice, or final confirmation of an irreversible action.
- Never fall back silently to an isolated browser, pointer control, coordinates, arbitrary JavaScript, or credential collection.
